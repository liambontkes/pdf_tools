import logging
import pathlib

import pypdf

import constants


class PdfHandler:
    def __init__(self, source):
        self.source = pathlib.Path(source)
        self.reader = pypdf.PdfReader(self.source)

    def search_list(self, ls_text):
        # search for all each element in list
        for text in ls_text:
            page_number = self.search(text)

            # if text is found, return page number
            if page_number != constants.not_found:
                return page_number

        # if none of the list elements are found, return not found
        return constants.not_found

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

    def split(self, page_range, path):
        # create new writer
        writer = pypdf.PdfWriter()

        # extract all pages in page range
        for page in range(int(page_range['first']), int(page_range['last'])):
            writer.add_page(self.reader.pages[page])

        # write file to disk
        try:
            with open(path, 'wb') as output:
                writer.write(output)
            logging.info(f"Wrote {path.name} to {path.parent}!")
            return True

        # if an error occurs, return False
        except OSError as error:
            logging.error(f"{error}. Unable to write {path.name} to file.")
            return False

    @property
    def name(self):
        return self.source.stem

    @property
    def number_of_pages(self):
        return len(self.reader.pages)


def get_pdfs(directory):
    # search directory for pdfs
    ls_pdf = sorted(pathlib.Path(directory).glob('*.pdf'))

    logging.info(f"Found {len(ls_pdf)} PDFs to process in {directory.name}")
    logging.debug(f"PDFs in {directory.name}: {ls_pdf}")

    # instantiate pdf handlers
    pdfs = []
    for pdf in ls_pdf:
        pdfs.append(PdfHandler(pdf))

    return pdfs
