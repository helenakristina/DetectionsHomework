# DetectionsHomework

## Prerequisites

This solution requires pipenv to run. Install with the following command

```
pip install --user pipenv
```

Navigate to the root folder in the terminal and run the code with the following command:

```
pipenv run python . {file_url} {file_url}
```

File urls can be paths to local files or http(s) urls. The program expects 1 or more command-line arguments to run.

## Implementation

I decided to use <a href="https://docs.dask.org/en/stable/"> Dask</a> to provide parallelization. Dask is a Python library that provides powerful access to parallelization of any Python code and is easy to scale and use on a cluster.

Dask uses distributed DataFrames similar to those in the popular Python library Pandas. One big difference is that Dask Dataframes are distributed to disk and Pandas are stored in-memory.

The implementation details are as follows:

<ol>
<li>Start a Dask client with as many threads as there are cores to the user's CPU, or the length of the files array, whichever is shorter</li>
<li>Use the map function to create futures to parse the individual files concurrently.</li>
<li>Wait for the futures to return with either a dataframe or None. (Failed files are logged.)</li>
<li>If there are non-null results, join them into a Dask Dataframe.</li>
<li>Use the builtin functions to compute median and average.</li>
<li>Query the dataframe for a record that holds the median age. Log either the record, or that no median record was found in the rare case where the median does not have an exact record.</li>
</ol>

## Testing

## Design Decisions

I originally wanted to make my code a bit more modular instead of having so much logic in the main function. I decided that was introducing too much complexity, especially with the passing around of Dask objects and dataframes.

I also had a dataclass in another file that formatted and parsed a data structure for reporting results. I decided to remove that and just use the Python logging function for reporting results. The advantage to having them in the same file is that it makes the program much easier to build and run.

I wanted to use a dask dataframe to calculate the median, but only an approximate_median can be calculated without all the records in one place. (The `compute()` function in `median = ddf["age"].compute().median()` creates a Pandas dataframe).

## Assumptions

I made an assumption that all valid files would contain headers. I had to do this because read_csv will still read a file with no commas in it.

I also made the assumption that individual files were small enough to be stored in memory, so implemented the `parse_file` function using a Pandas Dataframe. I did this because I was running into an error using the Dask `read_csv` function.

I made an assumption that it would not be too much to ask the user to install pipenv to manage the python dependencies and virtual environment.

I made an assumption that the timeit module was sufficient for measuring the clock time. I wanted to use the Dask profiler, but unfortunately it doesn't work for distributed solutions.

## How would I change my program if it had to process many files where each file was over 10M Records

In this case, I would definitely use the Dask `read_csv` function as well as looking at splitting the file into chunks like this <a href="https://stackoverflow.com/questions/65890030/how-to-split-a-large-csv-file-using-dask/65944272#65944272">Stack Overflow link </a>.
I would also spin up an HPC cluster of some kind to do the computations. Because the median needs all values to compute, I would also make a case for using the approximate median from Dask instead of the exact median.

## How would I change my program if it had to process data from more than 20k URLS

The nice thing about Dask (and one reason I chose it) is that the same code could run on an HPC cluster as my local machine. I would also play around with the number of threads as well as processes to find the optimal compute power.

## How would I test my code for production use at scale
