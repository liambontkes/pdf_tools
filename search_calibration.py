import pathlib
import re
import logging

import pandas
import constants


def get_tag_list(input_folder):
    """
    Gets a list of items to search for from the input folder.
    :param input_folder: the input folder to search in
    :return: a list of tags
    """
    # select first Excel file found in input folder
    search_excel = sorted(pathlib.Path(input_folder).glob('*.xlsx'))[0]

    # extract list of tags from Excel file
    search_hits = pandas.read_excel(search_excel, sheet_name='Instrument Index', usecols=['Tag No', 'Supplied By'])

    logging.info(f'Extracted tag list, found {len(search_hits)} tags')

    # clean search items
    search_hits = search_hits.dropna()
    search_hits['Tag No'] = search_hits['Tag No'].replace(to_replace='-', value='_', regex=True)

    logging.debug(f"Cleaned tag list: \n{search_hits}")

    return search_hits


def search_for_tag(pdf_reader, search_item):
    """
    Searches through the PDF for the first hit of the item.
    :param search_item: the search item to operate on
    :param pdf_reader: the pdf to search in
    :return: the page number where the item is found
    """
    # make Tag No searchable
    tag_sections = search_item['Tag No'].split(".")
    tag_search = f"{tag_sections[-2]}.{tag_sections[-1]}"

    # only search for tags with 'T' or 'I'
    matches = ['T', 'I', 'E']
    if not any([x in tag_sections[-1] for x in matches]):
        logging.info(f"Tag {search_item['Tag No']} is not type 'Indicator' or 'Transmitter', skipping search...")
        return search_item

    # search through each page of the pdf
    for page_number, page in enumerate(pdf_reader.pages):

        # read text from pdf page
        page_text = page.extract_text()

        # if found, save page number where text is found
        if tag_search in page_text:
            logging.debug(f"'{search_item['Tag No']}' found on page {page_number}")
            search_item['Page'] = page_number
            return search_item

    # if not found, return
    logging.debug(f"'{search_item['Tag No']}' not found")
    return search_item


def filter_tags(search_items):
    # make Tag No searchable
    tag_id = search_items['Tag No'].split(".")[-1]

    # only search for tags with 'T' or 'I'
    matches = ['T', 'I', 'E']
    if not any([x in tag_id for x in matches]):
        logging.info(f"Tag {search_items['Tag No']} is not type 'Indicator' or 'Transmitter', skipping search...")
        return search_items
    return search_items


def get_tag_name(tag):
    """
    Creates tag name from the passed tag.
    :param tag: the passed tag
    :return: the corresponding tag name
    """
    # split tag into it's sections
    tag_sections = tag.split(".")
    tag_area = tag_sections[3]
    tag_id = tag_sections[-1]

    # remove 'connected to' component of tag id
    if tag_id.find('_') != constants.not_found:
        tag_id = tag_sections[-1].split("_")[-1]

    # create tag name from area and id components
    # if id and area are the same, use only the id
    if tag_id == tag_area:
        tag_name = tag_id
    else:
        tag_name = f'{tag_area}.{tag_id}'

    return tag_name