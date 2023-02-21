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
import model
import pdf_handler
import pdf_tools
import tag


class SplitPdfs(pdf_tools.PdfTool):
    def __init__(self, split_type, input_path, output_path, df_split):
        self.df = df_split
        self.split_type = split_type
        super().__init__(input_path, output_path)

    def run(self):
        if self.split_type == 'tag':
            for idx, row in self.df.iterrows():
                split_file_name = self._split_pdf(row)
                self.df.at[idx, 'Destination'] = split_file_name

        elif self.split_type == 'model':
            # get list of unique models
            ls_models = self.df.Model.unique()

            for idx, unique_model in enumerate(ls_models):
                # get first row with the unique model
                row = self.df[self.df['Model'] == unique_model].iloc[0]
                split_file_name = self._split_pdf(row)
                self.df.loc[self.df['Model'] == unique_model, 'Destination'] = split_file_name

        else:
            logging.error(f"Split type {self.split_type} not recognized. Skipping split...")

        logging.info(f"Done splitting PDFs")

    def _generate_file_name(self, row):
        # generate output file name
        if self.split_type == 'tag':
            file_name = tag.create_file_name(row['Tag No'])
        elif self.split_type == 'model':
            file_name = model.create_file_name(row['Model'])
        else:
            logging.error(f"Search type {self.split_type} not recognized.")
            file_name = tag.create_file_name(row['Tag No'])
        return file_name

    def _split_pdf(self, row):
        # check if found
        if row['First Page'] == constants.not_found:
            logging.info(f"")
        # generate file name
        file_name = self._generate_file_name(row)

        # create output folder
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
                return False


class SearchAndSplit:
    def __init__(self, search_type, input_path, output_path, supplier_name):
        self.start_time = None
        self.search_type = search_type
        self.input_folder = pathlib.Path(input_path)
        self.output_folder = pathlib.Path(output_path)
        self.supplier = supplier_name

    def search_and_split(self):
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
        if self.search_type == 'tag':
            search_items['Search'] = search_items.apply(lambda row: tag.get_search_strings(row['Tag No']),
                                                        axis=1)
        elif self.search_type == 'model':
            search_items['Search'] = search_items.apply(lambda row: model.get_search_strings(row['Model']), axis=1)
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
        # iterate through each item in search items
        for idx, row in search_items.iterrows():
            # skip items which were not found
            if search_items.at[idx, 'Page'] == constants.not_found:
                logging.info(f"{search_items.at[idx, 'Tag No']} not found in {pdf.name}, skipping split...")

                # log tag as not found
                search_items.at[idx, 'Destination'] = constants.not_applicable
                logging.debug(search_items.at[idx, 'Destination'])

                # skip this tag
                continue

            # get range of pages to extract
            page_range = self._get_page_range(idx, search_items)

            # generate output file name
            if self.search_type == constants.calibration:
                file_name = calibration.create_file_name(search_items.at[idx, 'Tag No'])
            elif self.search_type == constants.atex:
                file_name = atex.create_file_name(search_items.at[idx, 'Model'])
            else:
                logging.error(f"Search type {self.search_type} not recognized.")
                file_name = calibration.create_file_name(search_items.at[idx, 'Tag No'])

            # save output file name
            search_items.at[idx, 'Destination'] = file_name

            # create output path
            output_path = self.output_folder / f'{file_name}.pdf'

            # split and write to file
            # check if file exists
            if output_path.is_file():
                logging.warning(f"File {output_path} already exists, skipping split...")
            else:
                if not pdf.split(page_range, output_path):
                    # if pdf fails to split, change destination to not applicable
                    search_items.at[idx, 'Destination'] = constants.not_applicable

        return search_items

    @staticmethod
    def _get_page_range(idx_search, search_items):
        # set first page number
        page_range = {
            'first': search_items.at[idx_search, 'Page']
        }

        # sort values by page number
        sorted_search_items = search_items.sort_values(by='Page')

        # sort search for item with higher page number
        idx_adjacent = numpy.searchsorted(sorted_search_items.Page.values, page_range['first'], side='right')
        page_range['last'] = sorted_search_items.at[idx_adjacent, 'Page']
        logging.debug(f"Last page for {search_items.at[idx_search, 'Tag No']} set to {page_range['last']}")

        return page_range

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
