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

import pandas
import slugify

import atex
import calibration
import constants
import pdf_handler


class SearchAndSplit:
    def __init__(self, search_type, input_path, output_path, supplier_name):
        self.start_time = None
        self.search_type = search_type
        self.input_folder = pathlib.Path(input_path)
        self.output_folder = pathlib.Path(output_path)
        self.supplier = supplier_name

    def search_and_split(self):
        """
        Searches the Excel file in the input folder for a list of tags, then searches the PDF documents for each tag.
        When found, extracts all tagged pages and saves them to the output folder.
        """
        # start timer
        self.start_time = time.time()
        logging.info(f"Starting execution timer")

        # get list of pdfs to process
        ls_pdf = pdf_handler.get_pdfs(self.input_folder)

        # get list of search items
        search_items = self._get_search_items()
        logging.info(f"Search items extracted; execution time was: {self._get_execution_time()}")

        # process each input pdf
        for idx, pdf in enumerate(ls_pdf):
            # filter out items
            nf_search_items = self._filter_search_items(search_items)

            # search for item locations within the pdf
            nf_search_items = self._search_for_items(pdf, nf_search_items)
            logging.info(f"Done searching {pdf.name}; execution time was: {self._get_execution_time()}")

            # split pdf based on tag locations
            nf_search_items = self._split_pdf(nf_search_items, pdf)
            logging.info(f"Done processing {pdf.name}; execution time was: {self._get_execution_time()}")

            pct_execution = (idx + 1) / len(ls_pdf) * 100.0
            time_remaining = self._get_execution_time() * (len(ls_pdf) - (idx + 1))
            logging.info(f"{pct_execution}% of PDFs processed, estimated time remaining: {time_remaining}")

            # update tag hits
            search_items.update(nf_search_items)

        # dump tag hits
        self._dump_dataframe(search_items)

        logging.info(f"Search and Split complete; execution time was: {self._get_execution_time()}")

    def _get_search_items(self):
        # select first Excel file found in input folder
        search_excel = sorted(pathlib.Path(self.input_folder).glob('*.xlsx'))[0]

        # extract list of tags from Excel file
        search_items = pandas.read_excel(search_excel,
                                         sheet_name='Instrument Index',
                                         usecols=['Tag No', 'Supplied By', 'Model'])

        # limit search to supplier
        search_items = search_items[search_items['Supplied By'] == self.supplier]
        logging.info(f"Limited search to {self.supplier}, number of items to search for is now {len(search_items)}")

        # clean search items
        # drop cells without tag numbers
        search_items = search_items.dropna(subset=['Tag No'])

        # fix tag notation
        search_items['Tag No'] = search_items['Tag No'].replace(to_replace='-', value='_', regex=True)

        # interpret all Models as strings
        search_items['Model'] = search_items['Model'].astype('string')

        logging.debug(f"Cleaned tag list: \n{search_items}")

        # add columns to search_items
        search_items['Search'] = ''
        search_items['Page'] = constants.not_found
        search_items['Source'] = ''
        search_items['Destination'] = ''

        # get search text for each item
        search_items = self._create_search(search_items)

        return search_items

    def _create_search(self, search_items):
        if self.search_type == constants.calibration:
            search_items['Search'] = search_items.apply(lambda row: calibration.get_search_strings(row['Tag No']), axis=1)
        elif self.search_type == constants.atex:
            search_items['Search'] = search_items.apply(lambda row: atex.get_search_strings(row['Model']), axis=1)
        else:
            logging.error(f"Search type {self.search_type} not recognized")
        return search_items

    @staticmethod
    def _filter_search_items(search_items):
        # only search for items that have not been found
        filtered_items = search_items.loc[search_items['Page'] == constants.not_found]

        return filtered_items

    @staticmethod
    def _search_for_items(pdf, search_items):
        # search each row in dataframe
        search_items['Page'] = search_items.apply(lambda row: pdf.search_list(row['Search']), axis=1)

        # record source pdf
        search_items['Source'] = pdf.name

        return search_items

    def _split_pdf(self, search_items, pdf):
        # sort search items by page number
        search_items = search_items.sort_values(by='Page')
        logging.debug(f"Search items to split from source pdf:\n{search_items}")

        # iterate through each item in search items
        for idx, row in search_items.iterrows():

            # set idx for next tag in list
            next_idx = idx + 1

            # skip items which were not found
            if search_items.at[idx, 'Page'] == constants.not_found:
                logging.info(f"{search_items.at[idx, 'Tag No']} not found in {pdf.name}, skipping split...")

                # log tag as not found
                search_items.at[idx, 'Destination'] = constants.not_applicable
                logging.debug(search_items.at[idx, 'Destination'])

                # skip this tag
                continue

            # find the first and last page related to the tag
            page_range = {
                'first': search_items.at[idx, 'Page']
            }
            try:
                page_range['last'] = search_items.at[next_idx, 'Page']

            # catch key out-of-bounds when selecting next tag
            except KeyError as error:
                page_range['last'] = pdf.number_of_pages
                logging.info(f"Reached last tag, setting page range to end of PDF")
                logging.debug(error)

            # catch multiple tags being found on the same page
            # catch next tag not being found
            while page_range['first'] >= page_range['last'] or page_range['last'] == constants.not_found \
                    and page_range['last'] <= pdf.number_of_pages:

                # increment next tag index
                next_idx = next_idx + 1

                # update page range
                try:
                    page_range['last'] = search_items.at[next_idx, 'Page']

                # if index is out-of-bounds, set last page to end of pdf
                except KeyError:
                    logging.info('Reader reached end of PDF')
                    page_range['last'] = pdf.number_of_pages

            # generate output's file name
            if self.search_type == constants.calibration:
                file_name = calibration.create_file_name(search_items.at[idx, 'Tag No'])
            elif self.search_type == constants.atex:
                file_name = atex.create_file_name(search_items.at[idx, 'Model'])
            else:
                logging.error(f"Search type {self.search_type} not recognized.")
                file_name = slugify.slugify(search_items.at[idx, 'Tag No'], separator="_", lowercase=False)
            output_path = self.output_folder / f'{file_name}.pdf'

            # save output file name
            search_items.at[idx, 'Destination'] = file_name

            # split and write to file
            # check if file exists
            if output_path.is_file():
                logging.warning(f"File {output_path} already exists, skipping split...")
            else:
                if not pdf.split(page_range, output_path):
                    # if pdf fails to split, change destination to not applicable
                    search_items.at[idx, 'Destination'] = constants.not_applicable

        return search_items

    def _dump_dataframe(self, dataframe):
        """
        Dumps the generated dataframe to an Excel document in the output folder.
        :param dataframe:
        """
        # create output file name
        output_name = self.output_folder / f"{self.search_type}_search_split_results.xlsx"

        # dump dataframe to xlsx
        dataframe.to_excel(output_name, sheet_name='Instrument Index')

    def _get_execution_time(self):
        execution_time = time.time() - self.start_time
        return datetime.timedelta(seconds=execution_time)


if __name__ == '__main__':
    # set log level
    logging.basicConfig(level=logging.DEBUG)

    # find batch to process
    supplier = input("Which supplier would you like to process?: ")
    batch_root = pathlib.Path(constants.batch_root)
    if len(sorted(batch_root.glob(supplier))) != 0:
        print(f"Found batch for supplier {supplier}.")
        batch_path = sorted(batch_root.glob(supplier))[0]
    else:
        print(f"No batch found for supplier {supplier}. Create one using create_batch.")
        exit()

    # select document type to process
    doc_type = input("What is the document type you want to process? "
                     f"Options are '{constants.atex}', '{constants.calibration}', '{constants.sort}': ")
    if doc_type == constants.atex or doc_type == 'a':
        doc_type = constants.atex
    elif doc_type == constants.calibration or doc_type == 'c':
        doc_type = constants.calibration
    elif doc_type == constants.sort or doc_type == 's':
        doc_type = constants.sort
    else:
        print(f"Document type {doc_type} not recognized.")
        exit()

    # set input and output folder
    input_folder_path = batch_path / doc_type / "input"
    output_folder_path = batch_path / doc_type / "output"
    output_folder_path.mkdir(parents=True, exist_ok=True)

    # run search and split
    sas = SearchAndSplit(doc_type, input_folder_path, output_folder_path, supplier)
    sas.search_and_split()
