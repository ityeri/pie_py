import os

def get_data_folder(path: str):

    entire_path = f'data/{path}'

    if not os.path.exists(entire_path) and not os.path.isdir(entire_path):
        os.mkdir(entire_path)

    return entire_path


def get_data_file(file_path: str) -> tuple[str, bool]:

    entire_file_path = f'data/{file_path}'

    if not os.path.exists(entire_file_path) and os.path.isdir(entire_file_path):
        with open(entire_file_path, 'x'): ...
        return entire_file_path, False
    else:
        return entire_file_path, True