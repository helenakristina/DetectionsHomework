# DetectionsHomework

## Prerequisites

This solution requires pipenv to run. Install pipenv with the following command

```
pip install --user pipenv
```
Note: Alternatively, pipenv can be installed using Homebrew on Mac, but the documentation suggests using pip whenever possible.

Navigate to the root folder of this repository in the terminal and run the code with the following command:

```
pipenv run python . {file_url} {file_url}
```

File urls can be paths to local files or http(s) urls. The program expects 1 or more command-line arguments to run, but will fail gracefully if no arguments are passed in.

## Implementation

I decided to use <a href="https://docs.dask.org/en/stable/"> Dask</a> to provide parallelization. Dask is a Python library that provides powerful access to parallelization of any Python code and is easy to scale and use on a cluster.

Dask uses distributed DataFrames similar to those in the popular Python library Pandas. One big difference is that Dask Dataframes are distributed to disk and Pandas are stored in-memory.

### The implementation details are as follows:

<ol>
<li>Start a Dask client with as many threads as there are cores to the user's CPU, or the length of the files array, whichever is shorter</li>
<li>Use the map function to create futures to parse the individual files concurrently.</li>
<li>Wait for the futures to return with either a dataframe or None. (Failed files are logged.)</li>
<li>If there are non-null results, join them into a Dask Dataframe.</li>
<li>Use the builtin functions to compute median and average.</li>
<li>Query the dataframe for a record that holds the median age. Log either the record, or that no median record was found in the rare case where the median does not have an exact record.</li>
</ol>

## Testing
During development, I debugged and tested using the provided test files through both the file system as well as https by hosting them on my Github repo and accessing the raw files.

I tested running the program without any arguments, running with only bad file(s), running it with some good and some bad files. Because the largest file provided was only 10,000 records, I also wanted to test it with a larger dataset.

I also used the Python faker library to generate random datasets for testing.

I generated a file with a million records and processed it twenty times for testing.

The output was as follows:
```
 DetectionsHomework git:(main) ✗ pipenv run python . data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv data/fake_million.csv 
INFO:Processed 20 file(s) using 12 threads in 0.36238343198783696 seconds.
INFO:The average age is 49.988716 years and The median age is 50.0 years.
INFO:A median record is Jacob Rogers.ß
```

I also used Pandas to read the csv files and verify that the mean and median were calculated correctly.

I then tested the rare case where there is no median record using the file `data/fake_ten.csv` (included in repo).

```  
DetectionsHomework git:(main) ✗ pipenv run python . data/fake_ten.csv
INFO:Processed 1 file(s) using 1 threads in 0.059239980997517705 seconds.
INFO:The average age is 53.5 years and The median age is 46.5 years.
INFO:No median record found. 
```

## Design Decisions

I originally wanted to make my code a bit more modular instead of having so much logic in the main function. I decided that was introducing too much complexity, especially with the passing around of Dask objects and dataframes.

I also had a dataclass in another file that formatted and parsed a data structure for reporting results. I decided to remove that and just use the Python logging function for reporting results. The advantage to having them in the same file is that it makes the program much easier to build and run.

I wanted to use a dask dataframe to calculate the median, but only an approximate_median can be calculated without all the records in one place. (The `compute()` function in `median = ddf["age"].compute().median()` creates a Pandas dataframe).

I had also intended to use more pure Python functions so I could have unit tests that made sense as part of my solution. Unit tests no longer made sense based on my implementation, because I would just have been mocking out the Dask functionality.

## Questions

### What assumptions did I make?

I made an assumption that all valid files would contain headers. I had to do this because read_csv will still read a file with no commas in it.

I also made the assumption that individual files were small enough to be stored in memory, so implemented the `parse_file` function using a Pandas Dataframe. I did this because I was running into an error using the Dask `read_csv` function, because it was expecting a Pandas dataframe.

I made an assumption that it would not be too much to ask the user to install pipenv to manage the python dependencies and virtual environment.

I made an assumption that the timeit module was sufficient for measuring the clock time. I wanted to use the Dask profiler, but unfortunately it doesn't work for distributed solutions using the Dask client.

### How would I change my program if it had to process many files where each file was over 10M Records?

In this case, I would definitely use the Dask `read_csv` function as well as looking at splitting the file into chunks like this <a href="https://stackoverflow.com/questions/65890030/how-to-split-a-large-csv-file-using-dask/65944272#65944272">Stack Overflow link </a>.
I would also spin up an HPC cluster of some kind to do the computations. Because the median needs all values to compute, I would also make a case for using the approximate median from Dask instead of the exact median, depending on the use case for requiring the median.

### How would I change my program if it had to process data from more than 20k URLS?

The nice thing about Dask (and one reason I chose it) is that the same code could run on an HPC cluster as my local machine. I would also play around with the number of threads as well as processes to find the optimal compute power.

### How would I test my code for production use at scale?
I would start by increasing my logging to include development logs for testing in a development environment.

I would then generate a lot of data to do integration and load tests at scale. I would add those to the CI/CD pipeline so that the containerized image would verify that nothing breaks on each commit.