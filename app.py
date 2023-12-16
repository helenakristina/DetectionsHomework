import logging
import multiprocessing
import sys
import timeit

import dask
import dask.distributed
import dask.dataframe
import pandas as pd

from dask.diagnostics import ResourceProfiler, Profiler


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


def parse_file(path: str) -> pd.DataFrame:
    """Function to parse a single file with graceful failures.
    Will return None if file does not conform to desired format.

    Args:
        path (str): File to parse. Accepts http(s) or local file system paths

    Returns:
        pd.DataFrame: Dataframe if file can be parsed, None if not
    """

    try:
        df = pd.read_csv(path, skipinitialspace=True)

    except ValueError:
        logging.info(f"File failed: {path}")
        return None

    if "fname" not in df.columns:
        logging.info(f"File failed: {path}")
        return None

    return df


def main(files: list) -> None:
    """Main function orchestrates distributed computation on files

    Args:
        files (list): List of file paths to parse
    """

    if not files:
        logging.info("No files to parse.")
        exit(0)

    cpu_count = multiprocessing.cpu_count()
    num_threads = cpu_count if cpu_count < len(files) else len(files)
    client = dask.distributed.Client(nthreads=num_threads)

    with Profiler() as prof, ResourceProfiler(dt=0.25) as rprof:
        futures = client.map(parse_file, files)
        dask.distributed.wait(futures)

    logging.info(f"Processed files using {num_threads} threads")

    print(prof.results)
    print(rprof.results)

    non_null_futures = [f for f in futures if f.type != type(None)]
    if non_null_futures:
        ddf = dask.dataframe.from_delayed(non_null_futures)
    else:
        logging.warning("No valid records were read.")
        exit(1)

    median = ddf["age"].compute().median()
    average = ddf["age"].mean().compute()

    median_record = ddf.query(f"age == {median}").compute().iloc[0]
    if not median_record.empty:
        median_record_fname = median_record["fname"]
        median_record_lname = median_record["lname"]

    logging.info(
        f"The average age is {average} years and The median age is {median} years."
        f"A median record is {median_record_fname} {median_record_lname}"
    )


if __name__ == "__main__":
    main(sys.argv[1:])
