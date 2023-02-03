import logging
import pathlib
import re

import pandas

import constants


def get_model_list(input_folder):
    """
    Gets a list of items to search for from the input folder.
    :param input_folder: the input folder to search in
    :return: a list of tags
    """
    # select first Excel file found in input folder
    search_excel = sorted(pathlib.Path(input_folder).glob('*.xlsx'))[0]

    # extract list of tags from Excel file
    search_hits = pandas.read_excel(search_excel, sheet_name='Instrument Index', usecols=['Tag No', 'Model'])

    logging.info(f'Extracted tag list, found {len(search_hits)} tags')

    # clean search items
    search_hits = search_hits.dropna()
    search_hits['Tag No'] = search_hits['Tag No'].replace(to_replace='-', value='_', regex=True)

    logging.debug(f"Cleaned tag list: \n{search_hits}")

    # add columns to search_hits
    search_hits['Page'] = constants.NOT_FOUND
    search_hits['Source'] = ''

    return search_hits


def search_for_models(pdf_reader, search_item):
    """
    Searches through the PDF for the first hit of the item.
    :param search_item: the search item to operate on
    :param pdf_reader: the pdf to search in
    :return: the page number where the item is found
    """
    # search through each page of the pdf
    for page_number, page in enumerate(pdf_reader.pages):

        # read text from pdf page
        page_text = page.extract_text()

        # if found, save page number where text is found
        if re.search(search_item['Model'], page_text):
            logging.debug(f"'{search_item['Model']}' found on page {page_number}")
            search_item['Page'] = page_number
            return search_item

    # if not found, return
    logging.debug(f"'{search_item['Model']}' not found")
    return search_item
