# File utils.
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

def get_data_dir(dataset_name: str) -> str:
    '''
    Returns the path to the output folder for a specific dataset.
    Args:
        dataset_name: The name of the dataset.
    Returns:
        The path to the output directory.
    '''
    return os.path.join(DATA_DIR, dataset_name)

def get_output_dir(dataset_name: str) -> str:
    '''
    Returns the path to the output folder for a specific dataset.
    Args:
        dataset_name: The name of the dataset.
    Returns:
        The path to the output directory.
    '''
    return os.path.join(OUTPUTS_DIR, dataset_name)

def get_templates_dir(dataset_name: str) -> str:
    '''
    Returns the path to the template folder for a specific dataset.
    Args:
        dataset_name: The name of the dataset.
    Returns:
        The path to the template directory.
    '''
    return os.path.join(TEMPLATES_DIR, dataset_name)
