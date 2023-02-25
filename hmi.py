import logging

import constants


def get_data(pattern):
    # get data to process
    p_data = sorted(constants.p_data.glob(pattern))[0]
    if p_data.exists():
        logging.info(f"Found data for {pattern}.")
        logging.debug(f"p_data: {p_data}")
    else:
        logging.error(f"No batch found for supplier {pattern}.")
        p_data = False

    return p_data


def get_index(pattern):
    # glob excel
    p_index = sorted(constants.p_indexes.glob(pattern))[0]
    if p_index.exists():
        logging.info(f"Found instrument index for {pattern}.")
    else:
        logging.error(f"No instrument index found for {pattern}.")
        p_index = False

    return p_index


def get_tool(pattern):
    if pattern == 'annotate' or pattern == 'a':
        return 'annotate'
    elif pattern == 'search' or pattern == 's':
        return 'search'
    elif pattern == 'split' or pattern == 'p':
        return 'split'
    elif pattern == 'searchsplit' or pattern == 'ss':
        return 'search and split'
    else:
        logging.error(f"No tool selection for {pattern}.")
        return False


def get_type(pattern):
    if pattern == 'tag' or pattern == 't':
        return 'tag'
    elif pattern == 'model' or pattern == 's':
        return 'model'
    else:
        logging.error(f"No tool selection for {pattern}.")
        return False
