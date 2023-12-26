import logging
import multiprocessing
import sys
import timeit

import dask
import dask.distributed
import dask.dataframe
import pandas as pd

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


def parse_file(path: str) -> pd.DataFrame | None:
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
        logging.warning(
            "No files to parse. Please provide files as command line arguments."
        )
        exit(1)

    cpu_count = multiprocessing.cpu_count()
    num_threads = cpu_count if cpu_count < len(files) else len(files)
    client = dask.distributed.Client(nthreads=num_threads)

    start = timeit.default_timer()
    futures = client.map(parse_file, files)
    dask.distributed.progress(futures)
    stop = timeit.default_timer()
    logging.info(
        f"Processed {len(files)} file(s) using {num_threads} threads in {stop-start} seconds."
    )

    if non_null_futures := [f for f in futures if f.type != type(None)]:
        ddf = dask.dataframe.from_delayed(non_null_futures)
    else:
        logging.warning("No valid records were read.")
        exit(1)

    median = ddf["age"].compute().median()
    average = ddf["age"].mean().compute()

    logging.info(
        f"The average age is {average} years and The median age is {median} years."
    )

    median_records = ddf.query(f"age == {median}").compute()
    if not median_records.empty:
        median_record = median_records.iloc[0]
        median_record_fname = median_record["fname"]
        median_record_lname = median_record["lname"]

        logging.info(f"A median record is {median_record_fname} {median_record_lname}.")
    else:
        logging.info("No median record found.")


if __name__ == "__main__":
    main(sys.argv[1:])
