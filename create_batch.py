import pathlib
import constants

if __name__ == "__main__":
    supplier = input("What is the supplier code?: ")

    # create path to batch root
    root = pathlib.Path(constants.BATCH_ROOT)

    batch = f"{supplier}"

    folder_names = [
        "input"
    ]

    for name in folder_names:
        path = root / batch / name
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
