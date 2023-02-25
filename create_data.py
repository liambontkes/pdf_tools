import pathlib
import constants
import shutil

if __name__ == "__main__":
    data = input("What is the data code?: ")
    index_pattern = input("Which index would you like to associate with it?: ")

    p_index = sorted(constants.p_indexes.glob(f"*{index_pattern}*.xlsx"))[0]

    folder_names = [
        "input",
        "output"
    ]

    for name in folder_names:
        p_folder = constants.p_data / data / name
        pathlib.Path(p_folder).mkdir(parents=True, exist_ok=True)
        if "input" in name:
            destination = p_folder / p_index.name
            shutil.copy(p_index, destination)
