import logging
import pathlib

import pandas

import model
import tag
import constants


class InstrumentIndex:
    def __init__(self, source, supplier):
        self.source = pathlib.Path(source)
        self.supplier = supplier

        # import dataframe
        self.df = self._import()

        # clean dataframe
        self._clean()

    def _import(self):
        # TODO add function to handle multiple import options
        # import from excel
        df = pandas.read_excel(self.source,
                               sheet_name='Instrument Index',
                               usecols=['Tag No', 'Supplied By', 'Model'])
        return df

    def _clean(self):
        # limit search to supplier
        self.df = self.df[self.df['Supplied By'] == self.supplier]
        logging.info(f"Limited search to {self.supplier}, number of items to search for is now {len(self.df)}")

        # clean search items
        # drop cells without tag numbers
        self.df = self.df.dropna(subset=['Tag No'])

        # fix tag notation
        self.df['Tag No'] = self.df['Tag No'].replace(to_replace='-', value='_', regex=True)

        # interpret all Models as strings
        self.df['Model'] = self.df['Model'].astype('string')

        logging.debug(f"Cleaned tag list: \n{self.df}")

        # add columns to self.df
        required_columns = ['Search', 'First Page', 'Last Page', 'Source', 'Destination']
        for column in required_columns:
            if column not in self.df.columns:
                if 'Page' in column:
                    self.df[column] = constants.not_found
                else:
                    self.df[column] = constants.empty

    def _set_search(self, split_type):
        if split_type == 'tag':
            self.df['Search'] = self.df.apply(lambda row: tag.get_search_strings(row['Tag No']),
                                              axis=1)
            return True
        elif split_type == 'model':
            self.df['Search'] = self.df.apply(lambda row: model.get_search_strings(row['Model']),
                                              axis=1)
            return True
        else:
            logging.error(f"Search type {split_type} not recognized")
            return False

    def get_tags(self, return_if_found=False):
        # if return_if_found is set, return all tags
        if return_if_found:
            return self.df

        # otherwise only return tags which have not been found yet
        else:
            return self.df.loc[self.df['Source'] == constants.empty]

    def get_by_tag(self, tag_id, return_if_found=False):
        # extract row associated with tag no
        row = self.df.loc[self.df['Tag No'] == tag_id]

        # if return_if_found is not set and page has already been found
        # do not return
        if not return_if_found and row['Source'] != constants.empty:
            return False
        else:
            return row

    def get_models(self, return_if_found=False):
        # if return_if_found is set, return all models
        if return_if_found:
            return self.df['Model'].unique()

        # otherwise only return models which have not been found
        else:
            nf_models = self.df.loc[self.df['Source'] == constants.empty]
            return nf_models['Model'].unique()

    def get_by_model(self, model_id, return_if_found=False):
        # extract rows associated with model no
        rows = self.df.loc[self.df['Model'] == model_id]

        # if return_if_found is not set and page has already been found
        # do not return
        if not return_if_found and rows.at[0, 'Source'] != constants.empty:
            logging.info(f"Model {model_id} has already been found.")
            return False
        else:
            return rows

    def get_sources(self, return_if_found=False):
        # if return_if_found is set, return all sources
        if return_if_found:
            return self.df['Source'].unique()

        # otherwise only return sources which have not been assigned destinations
        else:
            nf_sources = self.df.loc[self.df['Destination'] == constants.empty]
            return nf_sources['Source'].unique()

    def get_by_source(self, source, sort=True):
        # extract rows with common sources
        rows = self.df.loc[self.df['Source'] == source]

        # sort by First Page number
        if sort:
            rows = rows.sort_values(by='First Page')

        return rows

    def get_no_page_range(self):
        """
        Finds all items which have been found but not assigned a page range.
        :return: Items which have not been assigned a page range.
        """
        return self.df.loc[self.df['First Page'] != constants.not_found and self.df['Last Page'] == constants.not_found]

    def update(self, df_update):
        self.df.update(df_update)

    def dump(self, destination):
        # create dump df
        df_dump = self.df.copy()

        # change source to stem only
        df_dump['Source'] = self.df.apply(lambda row: row['Source'].stem)

        # write df to file
        df_dump.to_excel(destination, sheet_name='Instrument Index')

    @property
    def length(self):
        return len(self.df.index)
