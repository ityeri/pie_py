import os

def get_data_folder(path: str):
    data_path_exist = False

    if not( os.path.exists('data') and os.path.isdir('data') ):
        os.mkdir('data')
    
    if not( os.path.exists(f'data/{path}') and os.path.isdir(f'data/{path}') ):
        os.mkdir(f'data/{path}')

    return f'data/{path}'


# def getDataFile(path: str):
#     dataPathExist = False
#
#     if not( os.path.exists('data') and os.path.isdir('data') ):
#         os.mkdir('data')
#
#     if not( os.path.exists(f'data/{path}') and os.path.isdir(f'data/{path}') ):
#         os.mkdir(f'data/{path}')
#
#     return f'data/{path}'