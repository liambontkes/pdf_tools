import logging
import re

import constants


def get_search_strings(model):
    # search list in case there are multiple strings to search for
    ls_search = []

    # don't search for undetermined models
    if re.search(r"TBD", model):
        ls_search.append(constants.not_applicable)

    # handle combined model numbers
    elif re.search(r"\s+/\s+", model):
        combined_models = re.split(r"\s+/\s+", model)
        ls_search.extend(combined_models)

    # search for model outright
    else:
        ls_search.append(model)

    # remove whitespace
    for string in ls_search:
        string.strip()

    logging.debug(f"Cleaned search strings for {model}: {ls_search}")

    return ls_search
