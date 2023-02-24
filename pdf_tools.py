import logging

import click

import constants
import hmi
import tools


@click.command()
@click.option('--data', '-D',
              required=True,
              prompt="Data to process",
              help="The data to process.")
@click.option('--index', '-I',
              required=True,
              prompt="Instrument index to use",
              help="The instrument index to search in for instrument data.")
@click.option('--tool', '-T',
              type=click.Choice(['annotate', 'search', 'split', 'searchsplit']),
              case_sensitive=False,
              required=True,
              prompt="Tool to run",
              help="The tool to run on the batch.")
@click.option('--stype', '-Y',
              type=click.Choice(['tag', 'model']),
              case_sensitive=False,
              required=True,
              prompt="Tool to run",
              help="The tool to run on the batch.")
@click.option('--log', '-L',
              type=click.Choice(['debug', 'info', 'warning', 'error']),
              default='warning',
              required=False,
              help="Log level to set.")
def pdf_tools(data, index, stype, tool, log):
    if log == 'debug':
        # set log level
        logging.basicConfig(level=logging.DEBUG)
    if log == 'info':
        # set log level
        logging.basicConfig(level=logging.INFO)
    if log == 'warning':
        # set log level
        logging.basicConfig(level=logging.WARNING)
    if log == 'error':
        # set log level
        logging.basicConfig(level=logging.ERROR)
    else:
        # set log level to default
        logging.basicConfig(level=logging.WARNING)

    # confirm selection
    p_data = hmi.get_data(data)
    p_index = hmi.get_index(index)
    tool = hmi.get_tool(tool)
    stype = hmi.get_type(stype)
    if not p_data or not p_index or not tool or not stype:
        logging.error(f"Invalid selection, exiting...")
        exit()

    # set input and output folder
    p_in = constants.p_data / "input"
    p_out = constants.p_data / "output"

    # run tool
    if tool == 'search and split':
        tools.search_and_split(p_in, p_out, p_index, stype)


if __name__ == '__main__':
    pdf_tools()
