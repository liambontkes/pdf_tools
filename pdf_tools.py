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
@click.option('--tool', '-T',
              type=click.Choice(['annotate', 'search', 'split', 'searchsplit']),
              required=True,
              prompt="Tool to run",
              help="The tool to run on the batch.")
@click.option('--stype', '-Y',
              type=click.Choice(['tag', 'model']),
              required=True,
              prompt="Tool to run",
              help="The tool to run on the batch.")
@click.option('--supplier', '-S',
              required=False,
              help="Limits the instrument index to the supplier.")
@click.option('--log', '-L',
              type=click.Choice(['debug', 'info', 'warning', 'error']),
              default='warning',
              required=False,
              help="Log level to set.")
def pdf_tools(data, tool, stype, supplier, log):
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
    tool = hmi.get_tool(tool)
    stype = hmi.get_type(stype)
    if not p_data or not tool or not stype:
        logging.error(f"Invalid selection, exiting...")
        exit()

    # set input and output name
    p_in = p_data / "input"
    p_out = p_data / "output"

    # run tool
    if tool == 'search and split':
        tools.search_and_split(p_in, p_out, stype, supplier)


if __name__ == '__main__':
    pdf_tools()
