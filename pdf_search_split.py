# Calibration Doc Extractor
#
# Author: Liam Bontkes
# Description: Parses the Excel doc for a list of tags to search for in the PDF doc.
# It will then extract the relevant pages from the PDF doc and rename them according
# to their tag.

import pathlib
import re
import pypdf
import click
import pandas
import logging


# # Parse command args
# @click.command()
# @click.option("--tags", help="The file path to parse for the list of tags. Ensure it uses the correct path formatting.")
# @click.option("--pdf", help="The file to search for pages related to the tags. Ensure it uses the correct path "
#                             "formatting.")
def search_and_split(input_path, output_path):
    """
    Searches the Excel file in the input folder for a list of tags, then searches the PDF documents for each tag.
    When found, extracts all tagged pages and saves them to the output folder.
    :param input_path: the input folder to search in
    :param output_path: the output folder to write to
    :returns: none
    """
    # convert to path objects
    input_folder = pathlib.Path(input_path)
    output_folder = pathlib.Path(output_path)

    logging.info(f'Tags Source set to {input_folder}')
    logging.info(f'PDF Source set to {output_folder}')

    # get list of tags
    tag_list = get_tags(input_folder)

    # search for tag locations within the pdf
    tag_hits = get_tag_hits(tag_list, output_folder)

    # split pdf based on tag locations
    split_pdf(tag_hits, output_folder)


def get_tags(tags_source):
    """
    Gets a list of tags from the passed Excel file.
    :param tags_source: the path to the Excel file to parse
    :return: a list of tags
    """
    # extract list of tags from Excel file
    tag_list = pandas.read_excel(tags_source, sheet_name='Instrument Index', usecols=['Tag No'])

    logging.info(f'Extracted tag list, found {len(tag_list)} tags')

    # clean tags
    tag_list = tag_list.replace(to_replace='-', value='_', regex=True)

    logging.debug(f"Cleaned tag list: \n{tag_list}")

    return tag_list


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
    if tag_id.find('_') != -1:
        tag_id = tag_sections[-1].split("_")[-1]

    # create tag name from area and id components
    # if id and area are the same, use only the id
    if tag_id == tag_area:
        tag_name = tag_id
    else:
        tag_name = f'{tag_area}.{tag_id}'

    return tag_name


def get_tag_hits(tag_hits, pdf_source):
    """
    Generates a dataframe of tags and their location in the pdf document.
    :param tag_hits: the list of tags to search for
    :param pdf_source: the path to the pdf document to search
    :return: a dataframe of tags and the page number where they are found
    """
    # search pdf for each hit, then store page number in 'Page' column
    tag_hits['Page'] = tag_hits.apply(lambda row: search_pdf(row['Tag No'], pdf_source), axis=1)

    return tag_hits


def search_pdf(text, pdf):
    """
    Searches through the PDF for the first hit of the text.
    :param text: the text to search for
    :param pdf: the pdf to search in
    :return: the page number where the text is found
    """
    # create pdf reader
    pdf_reader = pypdf.PdfReader(pdf)

    # search through each page of the pdf
    for page_number, page in enumerate(pdf_reader.pages):

        page_text = page.extract_text()

        # if found, return page number where text is found
        if re.search(text, page_text):
            logging.debug(f"'{text}' found on page {page_number} in {pdf.stem}")
            return page_number

    # if not found, return -1
    logging.debug(f"'{text}' not found in {pdf.stem}")
    return -1


def split_pdf(tag_hits, pdf_source):
    """
    Creates a new file for each tag in tag hits, composed of the relevant pages from the pdf source.
    :param tag_hits: the dataframe of tags and the first page they found in pdf source
    :param pdf_source: the pdf source document
    :return: none
    """
    # sort tag hits by page number
    tag_hits.sort_values(by=['Page'])

    # create pdf reader
    pdf_reader = pypdf.PdfReader(pdf_source)

    # create output folder
    output_folder = pathlib.Path('temp/')
    output_folder.mkdir(parents=True, exist_ok=True)
    logging.info(f'Created output folder {output_folder.name}')

    # iterate through each tag in tag hits
    for tag_idx, tag_hit in tag_hits.iterrows():

        # set idx for next tag in list
        next_tag_idx = tag_idx + 1

        # find the first and last page related to the tag
        page_range = {
            'first': tag_hits.at[tag_idx, 'Page']
        }

        # catch key out-of-bounds
        try:
            page_range['last'] = tag_hits.at[next_tag_idx, 'Page']
        except KeyError as error:
            logging.info(f"Reached last tag, setting last page to end of PDF")
            logging.debug(error)
            page_range['last'] = len(pdf_reader.pages)

        # catch tags which were not found
        if page_range['first'] == -1:

            # skip this tag
            continue

        # catch multiple tags being found on the same page
        # catch next tag not being found (-1)
        while page_range['first'] >= page_range['last'] != -1 and page_range['last'] <= len(pdf_reader.pages):

            # increment next tag index
            next_tag_idx = next_tag_idx + 1

            # update page range
            try:
                page_range['last'] = tag_hits.at[next_tag_idx, 'Page']

            # if index is out-of-bounds, set last page to end of pdf
            except IndexError:
                logging.info('Reader reached end of PDF')
                page_range['last'] = len(pdf_reader.pages)

        # generate output's file name
        tag_name = get_tag_name(tag_hits.at[tag_idx, 'Tag No'])
        output_name = output_folder / f'{pdf_source.stem}_{tag_name}.pdf'

        # extract all pages in page range
        pdf_writer = pypdf.PdfWriter()
        for page_number in range(page_range['first'], page_range['last']):
            pdf_writer.add_page(pdf_reader.pages[page_number])

        # write file to disk
        with open(output_name, 'wb') as output_file:
            pdf_writer.write(output_file)

        logging.info(f"Generated PDF for tag no {tag_hits.at[tag_idx, 'Tag No']} at {output_name.name}")


if __name__ == '__main__':

    # set log level
    logging.basicConfig(level=logging.DEBUG)

    # input/output folders
    input_folder_path = r"input/"
    output_folder_path = r"output/"

    search_and_split(input_path=input_folder_path, output_path=output_folder_path)
