import logging
import time

import pandas

import constants
import pdf_handler
import pdf_tools


class SearchPdfs(pdf_tools.PdfTool):
    def __init__(self, input_path, output_path, instrument_index, search_type):
        """
        PDF Search tool, subclass of PdfTool.
        :param input_path: The input folder to search in for PDFs.
        :param output_path: The output folder to write to.
        :param instrument_index: The Instrument Index to pull search items from.
        :param search_type: The type of item to search for.
        """
        self.index = instrument_index
        self.type = search_type
        super().__init__(input_path, output_path)

        # get list of pdfs to process
        self.ls_pdf = self._get_ls_pdf()

    def run(self) -> pandas.DataFrame:
        """
        Searches through all PDFs for items and saves the PDF they are found in and the page range in the search index.
        :return: The search index with the page range and source file where the search item was found.
        """
        # process pdfs
        for idx, pdf in enumerate(self.ls_pdf):
            # search for items in pdf
            self._search(pdf)
            logging.info(f"Done searching in {pdf.name}!")
            logging.info(f"Time to process PDF: {self.get_execution_time()}")

            logging.info(f"{self.get_pct_execution(n_processed=idx+1, n_total=len(self.ls_pdf))}% of PDFs processed, "
                         f"estimated time "
                         f"remaining is {self.estimate_time_remaining(n_processed=idx+1, n_total=len(self.ls_pdf))}.")

        logging.info(f"Done searching all PDFs.")
        return self.index

    def _get_ls_pdf(self) -> list:
        """
        Gets a list of PDFs to process from the input folder.
        :return: A list of PDF handlers.
        """
        return pdf_handler.get_pdfs(self.input_folder)

    def _search(self, pdf: pdf_handler.PdfHandler) -> bool:
        """
        Searches through the PDF for strings in instrument index.
        :param pdf: The PDF to search in.
        :return: Whether the search completed successfully.
        """
        if self.type == 'tag':
            self._search_tags(pdf)
            return True
        elif self.type == 'model':
            self._search_models(pdf)
            return True
        else:
            logging.error(f"Split type {self.type} not recognized. Skipping search...")
            return False

    def _search_tags(self, pdf: pdf_handler.PdfHandler) -> bool:
        """
        Searches through the PDF for Tag numbers.
        :param pdf: The PDF to search in.
        :return: Boolean if search was successful.
        """
        # get tags from instrument index
        df_tags = self.index.get_tags()
        df_tags['First Page'] = df_tags.apply(lambda row: pdf.search_list(row['Search']), axis=1)

        # save pdf to source if found
        df_tags.loc[df_tags['First Page'] != constants.not_found, 'Source'] = pdf

        # update instrument index with the results
        self.index.update(df_tags)

        return True

    def _search_models(self, pdf: pdf_handler.PdfHandler) -> bool:
        """
        Searches through the PDF for Model numbers.
        :param pdf: The PDF to search in.
        :return: Boolean if search was successful.
        """
        # get list of models
        ls_models = self.index.get_models()

        # search for each model
        for mdl in ls_models:
            # get all tags associated with the model
            df_model = self.index.get_by_model(mdl)
            df_model['First Page'] = pdf.search_list(df_model.at[0, 'Search'])
            logging.info(f"Finished searching for {mdl} in {pdf.name}")

            # save pdf to source if found
            df_model.loc[df_model['First Page'] != constants.not_found, 'Source'] = pdf

            # update instrument index with results
            self.index.update(df_model)

        return True

