import logging
import pathlib

import pandas

import model
import tag
import constants


class DfHandler:
    def __init__(self, source, supplier):
        self.source = pathlib.Path(source)
        self.supplier = supplier

        # import dataframe
        self.df = self._import_from_excel()

        # clean dataframe
        self._clean_df()

    def _import_instrument_index(self):
        # import from excel
        df = pandas.read_excel(self.source,
                               sheet_name='Instrument Index',
                               usecols=['Tag No', 'Supplied By', 'Model'])
        return df

    def _clean_df(self):
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
                if 'Page' not in column:
                    self.df[column] = constants.not_found
                else:
                    self.df[column] = ''

    def set_search(self, split_type):
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

    def get_by_tag(self, tag_id, return_if_found=False):
        # extract row associated with tag no
        row = self.df.loc[self.df['Tag No'] == tag_id]

        # if return_if_found is not set and page has already been found
        # do not return
        if not return_if_found and row['Page'] != constants.not_found:
            return False
        else:
            return row

    def get_by_model(self, model_id, return_if_found=False):
        # extract rows associated with model no
        rows = self.df.loc[self.df['Model'] == model_id]

        # if return_if_found is not set and page has already been found, do not return
        if not return_if_found and rows['Page'] != constants.not_found:
            logging.info(f"Model {model_id} has already been found ")
            return False
        else:
            return rows

    def update(self, df_update):
        self.df.update(df_update)

    def dump(self, destination):
        self.df.to_excel(destination, sheet_name='Instrument Index')


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
