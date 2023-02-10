import pathlib

import constants


def get_batch_process(display_available=False):
    # set batch root dir
    batch_root = pathlib.Path(constants.batch_root)

    if display_available:
        # display available batches
        available_batches = [x for x in batch_root.iterdir() if x.is_dir()]
        print(f"Batches available for processing: ")
        for batch in available_batches:
            print(batch.name)

    # get batch to process
    supplier = input("Which supplier would you like to process?: ")
    batch_root = pathlib.Path(constants.batch_root)
    if len(sorted(batch_root.glob(supplier))) != 0:
        print(f"Found batch for supplier {supplier}.")
        batch_path = sorted(batch_root.glob(supplier))[0]
    else:
        print(f"No batch found for supplier {supplier}. Create one using create_batch.")
        batch_path = False

    return batch_path


def get_document_type(display_available=False):
    if display_available:
        print(f"Document type options are {constants.atex} (a), {constants.calibration} (c), {constants.sort} (s)")

    # select document type to process
    doc_type = input("What is the document type you want to process?: ")
    if doc_type == constants.atex or doc_type == 'a':
        doc_type = constants.atex
    elif doc_type == constants.calibration or doc_type == 'c':
        doc_type = constants.calibration
    elif doc_type == constants.sort or doc_type == 's':
        doc_type = constants.sort
    else:
        print(f"Document type {doc_type} not recognized.")
        doc_type = False

    return doc_type
