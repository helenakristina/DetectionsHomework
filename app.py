import logging
import sys
import timeit

import dask
import dask.distributed
import dask.dataframe as dd
import pandas as pd

from result import Result


logging.basicConfig(format='%(levelname)s:%(message)s',
                    level=logging.INFO)

NUM_THREADS = 8


def parse_file(path: str) -> pd.DataFrame:

    try:
        df = pd.read_csv(path, skipinitialspace=True)
    except Exception as err:
        logging.info(f"File failed: {path}")
        return None
    if "fname" not in df.columns:
        logging.info(f"File failed: {path}")
        return None
    return df


if __name__ == "__main__":

    files = sys.argv[1:]
    if not files:
        logging.info("No files to parse.")
        exit(0)

    result = Result()
    result.num_threads = NUM_THREADS
    client = dask.distributed.Client(nthreads=NUM_THREADS)

    try:
        start = timeit.default_timer()

        futures = client.map(parse_file, files)
        dask.distributed.wait(futures)

        non_null_futures = [f for f in futures if f.type != type(None)]
        if non_null_futures:
            ddf = dask.dataframe.from_delayed(non_null_futures)
        else:
            logging.warning("No valid records were read.")
            exit(0)

        median = ddf["age"].compute().median()
        result.median_age = median
        average = ddf["age"].mean().compute()
        result.average_age = average
        median_record = ddf.query(f'age == {median}').compute().iloc[0]
        if not median_record.empty:
            result.median_record_fname = median_record['fname']
            result.median_record_lname = median_record['lname']

        stop = timeit.default_timer()
        result.elapsed_sec = stop - start

        logging.info(result)

    except Exception as err:
        logging.error(err)
        exit(1)
