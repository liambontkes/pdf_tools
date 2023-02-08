import logging
import pathlib

import pypdf

import constants


class PdfHandler:
    def __init__(self, source):
        self.source = pathlib.Path(source)
        self.reader = pypdf.PdfReader(self.source)

    def search(self, text):
        # search through pdf by page
        for page_number, page in enumerate(self.reader.pages):

            # read text from page
            page_text = page.extract_text()

            # if found, return page number where text is first found
            if text in page_text:
                logging.debug(f"Found {text} on page {page_number} in {self.source.name}")
                return page_number

        # if not found, return not found
        return constants.not_found

    def split(self, page_range, filename):
        # create new writer
        writer = pypdf.PdfWriter()

        # extract all pages in page range
        for page in range(int(page_range['first']), int(page_range['last'])):
            writer.add_page(self.reader.pages[page])

        # write file to disk
        try:
            with open(filename, 'wb') as output:
                writer.write(output)
            logging.info(f"Wrote {filename.name} to {filename.parent}!")
            return True

        # if an error occurs, return False
        except OSError as error:
            logging.error(f"{error}. Unable to write {filename.name} to file.")
            return False
