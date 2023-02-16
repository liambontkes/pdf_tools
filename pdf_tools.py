import datetime
import logging
import pathlib
import time

import click

import constants
import hmi


@click.command()
@click.option('--batch', '-B',
              required=True,
              prompt="Batch to process",
              help="The batch to process.")
@click.option('--tool', '-T',
              type=click.Choice([constants.atex, constants.calibration, constants.annotate]),
              case_sensitive=False,
              required=True,
              prompt="Tool to run",
              help="The tool to run on the batch.")
def pdf_tools(batch, tool):
    # set log level
    logging.basicConfig(level=logging.DEBUG)

    # check selections
    batch_path = hmi.get_batch_process(batch)
    if not batch:
        logging.error(f"Selection not valid. Exiting...")
        exit()

    # set input and output folder
    input_folder_path = batch_path / tool / "input"
    output_folder_path = batch_path / tool / "output"
    output_folder_path.mkdir(parents=True, exist_ok=True)


class PdfTool:
    def __init__(self, input_path, output_path):
        self.start_time = None

        # set I/O folders
        self.input_folder = input_path
        self.output_folder = output_path

        # set supplier name
        self.supplier = self.input_folder.parent.name

    @staticmethod
    def _timestamp():
        return time.time()

    def _get_execution_time(self):
        execution_time = self._timestamp() - self.start_time
        return datetime.timedelta(seconds=execution_time)
