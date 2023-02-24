import pathlib

import pandas

if __name__ == "__main__":
    p_out = pathlib.Path.cwd() / 'misc' / 'Morenci - Instrument Index.xlsx'

    instrument_types = ['FIC', 'FIT', 'FY', 'FV']
    common = "704AMX4"
    n_groups = 2
    n_subgroups = 6

    ls_tags = list()

    for group in range(1, n_groups + 1):
        for subgroup in range(1, n_subgroups + 1):
            for instrument in instrument_types:
                ls_tags.append(f"{instrument}-704AMX4{group}{subgroup}L")

    d = {
        'Tag No': ls_tags,
        'Supplied By': 'default',
        'Model': 'default'
    }

    df = pandas.DataFrame(d)
    print(df)
    df.to_excel(p_out, sheet_name='Instrument Index')
