import logging

import handlers.instrument_index
# local imports
import tools.annotate
import tools.search
import tools.split


def search_and_split(p_in, p_out, stype, supplier=False):
    # import instrument index
    p_index = sorted(p_in.glob('*.xlsx'))[0]
    index = handlers.instrument_index.InstrumentIndex(p_index, supplier)

    # search pdfs
    search_index = search.Search(p_in, p_out, index, search_type=stype).run()

    # split pdfs
    split_index = split.Split(stype, p_in, p_out, search_index).run()

    # dump index to file
    p_dump = p_out / f"Search and Split Output.xlsx"
    split_index.dump(p_dump)
    logging.info(f"Search and split complete!")
