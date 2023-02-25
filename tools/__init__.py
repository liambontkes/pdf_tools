import datetime
import logging
import time

import handlers.instrument_index

# local imports
import annotate
import search
import split


class PdfTool:
    def __init__(self, input_path, output_path):
        self.start_time = None

        # set I/O folders
        self.input_folder = input_path
        self.output_folder = output_path

        # set supplier name
        self.supplier = self.input_folder.parent.name

    @staticmethod
    def _timestamp() -> time.time:
        """
        Creates a timestamp at the current time.
        :return: The current time.
        """
        return time.time()

    def start_timer(self) -> None:
        """
        Sets the start time timestamp.
        """
        self.start_time = self._timestamp()

    def get_execution_time(self) -> datetime.timedelta:
        """
        Gets the execution time of tool.
        :return: The execution time since the timer started.
        """
        execution_time = self._timestamp() - self.start_time
        return datetime.timedelta(seconds=execution_time)

    def log_execution(self, n_processed: int, n_total: int) -> None:
        """
        Logs the completion percentage and estimated time remaining.
        :param n_processed: The number of processed items.
        :param n_total: The total number of items to process.
        """
        pct_execution = n_processed / n_total * 100.0
        estimated_time_remaining = self.get_execution_time() * (n_total - n_processed)
        logging.info(f"{pct_execution}% of items processed, estimated time remaining is {estimated_time_remaining}.")


def search_and_split(p_in, p_out, stype, supplier=False):
    # import instrument index
    p_index = sorted(p_in.glob('*.pdf'))[0]
    index = handlers.instrument_index.InstrumentIndex(p_index, supplier)

    # search pdfs
    search_index = search.Search(p_in, p_out, index, search_type=stype).run()

    # split pdfs
    split_index = split.Split(stype, p_in, p_out, search_index).run()

    # dump index to file
    p_dump = p_out / f"Search and Split Output.xlsx"
    split_index.dump(p_dump)
    logging.info(f"Search and split complete!")
