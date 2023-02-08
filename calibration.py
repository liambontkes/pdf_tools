import logging
import re

from slugify import slugify

import constants


def get_search_strings(tag):
    ls_search = []

    # only search for transmitter and indicator tags
    if re.search(r"[IT]\d+$", tag):
        logging.debug(f"Tag {tag} is type transmitter or indicator, calibration required")

        # only search for last 3 sections of the tag
        ls_search.append(re.search(r"\w+.\w+[-_]\w+|\w+$", tag).group(0))

    # if tag is not correct type, return not applicable
    else:
        logging.debug(f"Tag {tag} is not type transmitter or indicator, calibration NOT required")
        ls_search.append(constants.not_applicable)

    return ls_search


def create_file_name(tag):
    safe_tag = slugify(tag, separator='_', lowercase=False)
    return f"Calibration Certificate - {safe_tag}"
