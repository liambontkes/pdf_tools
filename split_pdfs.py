# Calibration Doc Extractor
#
# Author: Liam Bontkes
# Description: Parses the Excel doc for a list of tags to search for in the PDF doc.
# It will then extract the relevant pages from the PDF doc and rename them according
# to their tag.
import datetime
import logging
import pathlib
import time

import numpy
import pandas

import constants
import instrument_index
import model
import pdf_handler
import pdf_tools
import tag


class SplitPdfs(pdf_tools.PdfTool):
    def __init__(self, split_type: str, input_path: pathlib.Path, output_path: pathlib.Path, index: instrument_index.InstrumentIndex) -> None:
        """
        PDF Split tool, subclass of PdfTool.
        :param split_type: The type of items to split on.
        :param input_path: The input folder to read from.
        :param output_path: The output folder to write to.
        :param index: The Search Index to split by.
        """
        self.index = index
        self.type = split_type
        super().__init__(input_path, output_path)

    def run(self) -> bool:
        """
        Splits all PDFs in the index based on split type.
        :return: Boolean whether split was successful.
        """
        # start the timer
        self.start_timer()

        # split based on split type
        if self.type == 'tag':
            tags = self.index.get_tags(return_if_found=True)
            for idx, row in tags.iterrows():
                # split file
                file_name = self._split_pdf(row)

                # save destination
                row['Destination'] = file_name

                # log execution stats
                self.log_execution(n_processed=idx + 1, n_total=self.index.length)

        elif self.type == 'model':
            # get list of unique models
            ls_models = self.index.get_models(return_if_found=True)

            for idx, mdl in enumerate(ls_models):
                # get first row associated with the model
                models = self.index.get_by_model(mdl, return_if_found=True)
                row = models.iloc[0]

                # split based on the model
                file_name = self._split_pdf(row)

                # save destination for all models
                models.loc[models['Destination']] = file_name

                # update index
                self.index.update(models)

                # log execution stats
                self.log_execution(n_processed=idx + 1, n_total=len(ls_models))

        else:
            logging.error(f"Split type {self.type} not recognized. Skipping split...")

        logging.info(f"Done splitting PDFs.")
        return True

    def _split_pdf(self, row: pandas.DataFrame) -> str:
        """
        Splits a PDF based on the page range in row.
        :param row: The row to split the PDF on.
        :return: The destination file name or applicable error.
        """
        # check if found
        if row['First Page'] == constants.not_found:
            return constants.not_applicable

        # generate file name
        file_name = self._generate_file_name(row)

        # create output path
        output_path = self.output_folder / f'{file_name}.pdf'

        # split and write to file
        # check if file exists
        if output_path.is_file():
            logging.warning(f"File {output_path} already exists, skipping split...")
        else:
            # return file_name if able to write to file
            if row['Source'].split(row['First Page'], row['Last Page'], output_path):
                return file_name
            else:
                return constants.error

    def _generate_file_name(self, row: pandas.DataFrame) -> str:
        """
        Generates a file name based on the split type and item.
        :param row: The row to write a file name for.
        :return: The filename.
        """
        # generate output file name
        if self.type == 'tag':
            file_name = tag.create_file_name(row['Tag No'])
        elif self.type == 'model':
            file_name = model.create_file_name(row['Model'])
        else:
            logging.error(f"Search type {self.type} not recognized.")
            file_name = tag.create_file_name(row['Tag No'])
        return file_name
