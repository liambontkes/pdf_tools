# Calibration Doc Extractor
#
# Author: Liam Bontkes
# Description: Parses the Excel doc for a list of tags to search for in the PDF doc.
# It will then extract the relevant pages from the PDF doc and rename them according
# to their tag.
import functools
import logging
import pathlib
import re
import datetime
import time

import pypdf

import search_calibration
import constants
import search_models


class SearchAndSplit:
    def __init__(self, search_type, input_path, output_path):
        self.search_type = search_type
        self.input_folder = pathlib.Path(input_path)
        self.output_folder = pathlib.Path(output_path)

        # create input and output folders
        self.input_folder.mkdir(parents=True, exist_ok=True)
        logging.info(f'Created input folder {self.input_folder.name}')

        self.output_folder.mkdir(parents=True, exist_ok=True)
        logging.info(f'Created output folder {self.output_folder.name}')

    def search_and_split(self):
        """
        Searches the Excel file in the input folder for a list of tags, then searches the PDF documents for each tag.
        When found, extracts all tagged pages and saves them to the output folder.
        """
        # start timer
        start_time = time.time()
        logging.info(f"Starting execution timer")

        # get list of pdfs to process
        pdf_input_list = self._get_input_pdfs()

        # get list of search items
        search_items = self._get_search_items()
        execution_time = time.time() - start_time
        logging.info(f"Search items extracted; execution time was: {datetime.timedelta(seconds=execution_time)}")

        # process each input pdf
        for pdf in pdf_input_list:
            # filter out items
            nf_search_items = self._filter_search_items(search_items)

            # search for item locations within the pdf
            nf_search_items = self._get_search_hits(pdf, nf_search_items)

            execution_time = time.time() - start_time
            logging.info(f"Search items found; execution time was: {datetime.timedelta(seconds=execution_time)}")

            # split pdf based on tag locations
            self._split_pdf(nf_search_items, pdf)

            execution_time = time.time() - start_time
            logging.info(f"Done processing {pdf.name}; execution time was: {datetime.timedelta(seconds=execution_time)}")

            # update tag hits
            search_items.update(nf_search_items)

        # dump tag hits
        self.dump_dataframe(search_items)

        execution_time = time.time() - start_time
        logging.info(f"Search and Split complete; execution time was: {datetime.timedelta(seconds=execution_time)}")

    def _get_input_pdfs(self):
        """
        Generates a list of PDFs to search.
        :return: a list of paths
        """
        pdf_list = sorted(pathlib.Path(self.input_folder).glob('*.pdf'))

        logging.info(f"Found {len(pdf_list)} PDFs to process in {self.input_folder.name}")

        logging.debug(f"PDF process list: \n{pdf_list}")

        return pdf_list

    def _get_search_items(self):
        """
        Gets a list of items to search for from the input folder.
        :return: a list of search items
        """
        if self.search_type == 'calibration':
            return search_calibration.get_tag_list(self.input_folder)
        else:
            return search_models.get_model_list(self.input_folder)

    def _filter_search_items(self, search_items):
        # only search for items that have not been found
        filtered_items = search_items.loc[search_items['Page'] == constants.NOT_FOUND]

        # context dependent filtering
        if self.search_type == 'calibration':
            return search_calibration.filter_tags(filtered_items)
        else:
            return search_models.filter_models(filtered_items)

    def _get_search_hits(self, pdf_source, nf_search_items):
        """
        Generates a dataframe of search items and their location in the pdf document.
        :param nf_search_items: the list of items to search for
        :param pdf_source: the path to the pdf document to search
        :return: a dataframe of items and the page number where they are found
        """
        # create pdf reader
        pdf_reader = pypdf.PdfReader(pdf_source)

        if self.search_type == 'calibration':
            search_pdf_partial = functools.partial(search_calibration.search_for_tag, pdf_reader)
        else:
            search_pdf_partial = functools.partial(search_models.search_for_models, pdf_reader)

        nf_search_items = nf_search_items.apply(search_pdf_partial, axis=1)

        # record source pdf
        nf_search_items['Source'] = pdf_source.stem

        return nf_search_items

    def _split_pdf(self, search_hits, pdf_source):
        """
        Creates a new file for each tag in tag hits, composed of the relevant pages from the pdf source.
        :param search_hits: the dataframe of search items and the first page they are found in pdf source
        :param pdf_source: the pdf source document
        """
        # sort tag hits by page number
        search_hits = search_hits.sort_values(by='Page').reset_index(drop=True)
        logging.debug(f"Search items to split from source pdf:\n{search_hits}")

        # create pdf reader
        pdf_reader = pypdf.PdfReader(pdf_source)

        # iterate through each tag in tag hits
        for item_idx, hit in search_hits.iterrows():

            # set idx for next tag in list
            next_item_idx = item_idx + 1

            # find the first and last page related to the tag
            page_range = {
                'first': search_hits.at[item_idx, 'Page']
            }

            # catch key out-of-bounds
            try:
                page_range['last'] = search_hits.at[next_item_idx, 'Page']
            except KeyError as error:
                logging.info(f"Reached last tag, setting page range to end of PDF")
                logging.debug(f"KeyError: {error}")

                page_range['last'] = len(pdf_reader.pages)

            # catch tags which were not found
            if page_range['first'] == constants.NOT_FOUND:
                logging.info(f"{search_hits.iloc[item_idx]} not found in {pdf_source.stem}, skipping split...")
                # skip this tag
                continue

            # catch multiple tags being found on the same page
            # catch next tag not being found
            while page_range['first'] >= page_range['last'] or page_range['last'] == constants.NOT_FOUND and page_range[
                'last'] <= len(
                    pdf_reader.pages):

                # increment next tag index
                next_item_idx = next_item_idx + 1

                # update page range
                try:
                    page_range['last'] = search_hits.at[next_item_idx, 'Page']

                # if index is out-of-bounds, set last page to end of pdf
                except KeyError:
                    logging.info('Reader reached end of PDF')
                    page_range['last'] = len(pdf_reader.pages)

            # generate output's file name
            if self.search_type == 'calibration':
                file_name = f"Calibration Certificate - {search_hits.at[item_idx, 'Tag No']}"
            else:
                file_name = f"ATEX Certificate - {search_hits.at[item_idx, 'Model']}"
            output_name = self.output_folder / f'{file_name}.pdf'

            # extract all pages in page range
            pdf_writer = pypdf.PdfWriter()
            for page_number in range(page_range['first'], page_range['last']):
                pdf_writer.add_page(pdf_reader.pages[page_number])

            # write file to disk
            with open(output_name, 'wb') as output_file:
                pdf_writer.write(output_file)

            logging.info(f"Generated {output_name.name} for item \n{search_hits.iloc[item_idx]}")

    def dump_dataframe(self, dataframe):
        """
        Dumps the generated dataframe to an Excel document in the output folder.
        :param dataframe:
        """
        # create output file name
        output_name = self.output_folder / "search_split_results.xlsx"

        # dump dataframe to xlsx
        dataframe.to_excel(output_name, sheet_name='Instrument Index')


if __name__ == '__main__':
    # set log level
    logging.basicConfig(level=logging.DEBUG)

    # input/output folders
    input_folder_path = r"input/"
    output_folder_path = r"output/"

    # run search and split
    calibration_sas = SearchAndSplit('atex', input_folder_path, output_folder_path)
    calibration_sas.search_and_split()
