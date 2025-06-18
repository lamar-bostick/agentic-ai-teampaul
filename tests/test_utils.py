import os
from backend import utils

def test_output_folder_exists():
    utils.clear_and_create_folder("app_files")
    assert os.path.exists("app_files"), "app_files folder should be created"

def test_list_app_files_empty():
    utils.clear_and_create_folder("app_files")
    result = utils.list_app_files()
    assert isinstance(result, list)
