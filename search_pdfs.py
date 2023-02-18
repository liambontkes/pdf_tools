import logging

import constants
import pdf_handler
import pdf_tools


class SearchPdfs(pdf_tools.PdfTool):
    def __init__(self, input_path, output_path, instrument_index, split_type):
        self.instrument_index = instrument_index
        self.split_type = split_type
        super().__init__(input_path, output_path)

        # get list of pdfs to process
        self.ls_pdf = self._get_ls_pdf()

    def run(self):
        for idx, pdf in enumerate(self.ls_pdf):
            # search for items in pdf
            nf_instruments = self._search(pdf)
            logging.info(f"Done searching in {pdf.name}!")

        logging.info(f"Done searching all PDFs.")

    def _get_ls_pdf(self):
        return pdf_handler.get_pdfs(self.input_folder)

    def _search(self, pdf):
        if self.split_type == 'tag':
            return self._search_tags(pdf)
        elif self.split_type == 'model':
            return self._search_models(pdf)
        else:
            logging.error(f"Split type {self.split_type} not recognized. Skipping search...")
            return False

    def _search_tags(self, pdf):
        # get tags from instrument index
        df_tags = self.instrument_index.get_tags()
        df_tags['First Page'] = df_tags.apply(lambda row: pdf.search_list(row['Search']), axis=1)

        # save pdf to source if found
        df_tags.loc[df_tags['First Page'] != constants.not_found, 'Source'] = pdf

        # update instrument index with the results
        self.instrument_index.update(df_tags)

    def _search_models(self, pdf):
        # get list of models
        ls_models = self.instrument_index.get_models()

        # search for each model
        for mdl in ls_models:
            # get all tags associated with the model
            df_model = self.instrument_index.get_by_model(mdl)
            df_model['First Page'] = pdf.search_list(df_model.at[0, 'Search'])
            logging.info(f"Finished searching for {mdl} in {pdf.name}")

            # save pdf to source if found
            df_model.loc[df_model['First Page'] != constants.not_found, 'Source'] = pdf

            # update instrument index with results
            self.instrument_index.update(df_model)

