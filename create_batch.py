import pathlib
import constants
import shutil

if __name__ == "__main__":
    supplier = input("What is the supplier code?: ")

    # create path to data root
    root = pathlib.Path(constants.batch_root)

    # path to input Excel file
    excel = pathlib.Path(constants.instrument_index)

    doc_types = [
        constants.atex,
        constants.calibration,
        constants.sort
    ]

    folder_names = [
        "input",
        "output"
    ]

    for doc in doc_types:
        for folder in folder_names:
            path = root / supplier / doc / folder
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
            if folder == "input":
                dst = path / excel.name
                shutil.copy(excel, dst)

