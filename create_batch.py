import pathlib
import constants
import shutil

if __name__ == "__main__":
    supplier = input("What is the supplier code?: ")

    # create path to batch root
    root = pathlib.Path(constants.BATCH_ROOT)

    # path to input Excel file
    excel = pathlib.Path(r'C:\Users\BONT17424\PycharmProjects\pdf_search_split\misc\H363404-00000-270-216-0001, 0002 & 0003-MstrRedline.xlsx')

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
            if folder == "input":
                dst = path / excel.name
                shutil.copy(excel, dst)

