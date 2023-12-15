from dataclasses import dataclass


@dataclass
class Result:
    """_summary_

    Returns:
        Result: Data Structure to persist result data calculated in main function
    """

    average_age: int = 0
    elapsed_sec: int = 0
    median_age: int = 0
    median_record_fname: str = ""
    median_record_lname: str = ""
    num_threads: int = 0

    def get_median_record_str(self) -> str:
        """_summary_

        Returns:
            str: Description of median record, if found.
        """
        if self.median_record_fname:
            return f"A median record is {self.median_record_fname} {self.median_record_lname}."
        else:
            return "No median record found."

    def __str__(self) -> str:
        return f"""
            This program completed in {self.elapsed_sec} seconds
            using {self.num_threads} threads.
            The average age is {self.average_age} years and
            The median age is {self.median_age} years.
            {self.get_median_record_str()}
            """
