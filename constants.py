import pathlib

# error handling
not_found = -1
not_applicable = 'N/A'
empty = 'N/P'
error = 'ERROR'

# configuration
tools = ['split-tag', 'split-model', 'sort', 'annotate']
df_columns = {
    'split-tag': ['Tag No', 'Supplied By', 'Model'],
    'split-model': ['Tag No', 'Supplied By']
}

# paths
p_data = pathlib.Path.cwd() / 'data'
p_indexes = pathlib.Path.cwd() / 'misc' / 'indexes'
