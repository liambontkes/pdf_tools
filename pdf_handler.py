import logging
import math
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

    def _annotate(self, page_number, annotation_format, path):
        # copy pdf
        writer = pypdf.PdfWriter()
        for page in self.reader.pages:
            writer.add_page(page)

        # add annotation to page
        annotation = pypdf.generic.AnnotationBuilder.free_text(
            text=annotation_format.text,
            rect=annotation_format.rect,
            font=annotation_format.font,
            bold=annotation_format.bold,
            italic=annotation_format.italic,
            font_size=annotation_format.font_size,
            font_color=annotation_format.font_color,
            border_color=annotation_format.border_color,
            background_color=annotation_format.background_color
        )
        writer.add_annotation(page_number, annotation)

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

    def annotate_tags(self, page_number, tags, path):
        # get page height and width
        box = self.reader.pages[page_number].mediabox
        page_width = box.width
        page_height = box.height

        # get tags annotation formatting
        tags_annotation = TagsAnnotation(tags, page_height, page_width)

        # annotate to new file
        return self._annotate(page_number, tags_annotation, path)

    @property
    def name(self):
        return self.source.stem

    @property
    def number_of_pages(self):
        return len(self.reader.pages)


class TagsAnnotation:
    font = "Arial"
    bold = False
    italic = False
    font_number = 6
    font_color = "000000"
    border_color = "ffd700"
    background_color = "ffff00"

    height_scale = 12
    width_scale = 3.6
    text_buffer = 10

    def __init__(self, tags, page_height, page_width):
        self.tags = tags
        self.page_width = float(page_width)
        self.page_height = float(page_height)

        self.width = self._get_box_width()
        self.height = self._get_box_height()

        self.text = self._get_text()

    def _get_box_width(self):
        return max(len(tag) for tag in self.tags) * self.width_scale

    def _get_box_height(self):
        return len(self.tags) * self.font_number + self.text_buffer

    def _get_text(self):
        return "\n".join(self.tags)

    @property
    def font_size(self):
        return f"{self.font_number}pt"

    @property
    def rect(self):
        # lower left corner coordinates
        x_lower_left = self.page_width - self.width
        y_lower_left = self.page_height - self.height

        # upper right corner coordinates
        x_upper_right = self.page_width
        y_upper_right = self.page_height

        return x_lower_left, y_lower_left, x_upper_right, y_upper_right


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
