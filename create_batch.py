import pathlib
import constants

if __name__ == "__main__":
    supplier = input("What is the supplier code?: ")

    # create path to batch root
    root = pathlib.Path(constants.BATCH_ROOT)

    doc_types = [
        constants.ATEX,
        constants.CALIBRATION,
        constants.SORT
    ]

    folder_names = [
        "input",
        "output"
    ]

    for doc in doc_types:
        for folder in folder_names:
            path = root / supplier / doc / folder
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)
