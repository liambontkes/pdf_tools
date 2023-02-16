import pathlib

import constants


def get_batch_process(selection):
    # set batch root dir
    batch_root = pathlib.Path(constants.batch_root)

    # get batch to process
    batch_root = pathlib.Path(constants.batch_root)
    if len(sorted(batch_root.glob(selection))) != 0:
        print(f"Found batch for supplier {selection}.")
        batch_path = sorted(batch_root.glob(selection))[0]
    else:
        print(f"No batch found for supplier {selection}. Create one using create_batch.")
        batch_path = False

    return batch_path


def get_tool(selection):
    # select document type to process
    if selection == constants.atex or selection == 'x':
        tool = constants.atex
    elif selection == constants.calibration or selection == 'c':
        tool = constants.calibration
    elif selection == constants.sort or selection == 's':
        tool = constants.sort
    else:
        print(f"Tool {selection} not recognized.")
        tool = False

    return tool
