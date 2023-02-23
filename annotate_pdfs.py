import logging
import pathlib
from typing import List

import pandas

import constants
import instrument_index
import pdf_handler
import pdf_tools


class AnnotatePdfs(pdf_tools.PdfTool):
    def __init__(self, input_path: pathlib.Path, output_path: pathlib.Path, index: instrument_index.InstrumentIndex, annotate_type: str) -> None:
        self.index = index
        self.type = annotate_type
        super().__init__(input_path, output_path)

    def run(self) -> None:
        # get list of pdfs to annotate
        ls_pdf = self._get_ls_pdf()

        for pdf in ls_pdf:
            # get annotation text for the pdf
            annotation = self._get_annotation(pdf)

            # annotate the pdf with all tags that point to it
            self._annotate(pdf, annotation)

    def _get_ls_pdf(self):
        return pdf_handler.get_pdfs(self.input_folder)

    def _get_annotation(self, pdf) -> list[str]:
        # extract all items which point to the pdf
        rows = self.index.get_by_destination(pdf.name)

        if self.type == 'tag':
            # get list of tags to annotate onto pdf
            return rows['Tag No'].to_list()

        else:
            logging.error(f"Annotate type {self.type} not recognized. Skipping annotation...")
            return [constants.error]

    def _annotate(self, pdf, annotation):
        if self.type == 'tag':
            return pdf.annotate_tags(0, annotation, pdf)

        else:
            logging.error(f"Annotate type {self.type} not recognized. Skipping annotation...")
            return [constants.error]
