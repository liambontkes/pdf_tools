import logging

import click

import hmi


@click.command()
@click.option('--project', '-P',
              required=True,
              prompt="Project to process",
              help="The project to process.")
@click.option('--tool', '-T',
              type=click.Choice(['annotate', 'search', 'split']),
              case_sensitive=False,
              required=True,
              prompt="Tool to run",
              help="The tool to run on the project.")
@click.option('--log', '-L',
              type=click.Choice(['debug', 'info', 'warning', 'error']),
              default='warning',
              required=False,
              help="Log level to set.")
def pdf_tools(batch, tool, log):
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

    # check selections
    batch_path = hmi.get_batch_process(batch)
    if not batch:
        logging.error(f"Selection not valid. Exiting...")
        exit()

    # set input and output folder
    input_folder_path = batch_path / tool / "input"
    output_folder_path = batch_path / tool / "output"
    output_folder_path.mkdir(parents=True, exist_ok=True)
