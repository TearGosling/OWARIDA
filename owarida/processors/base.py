from abc import ABC, abstractmethod

from ..utils import get_data_dir, get_templates, get_output_dir

class BaseProcessor(ABC):
    def __init__(self):
        '''
        The base class for all processors.
        '''
        self.num_iterations = 0 # To be set later.
    
    @abstractmethod
    def augment(self):
        '''
        This code augments by applying templates to the data.
        '''
        raise NotImplementedError("This is an abstract class.")
    
    @abstractmethod
    def download(self):
        '''
        This code downloads the data from the source, usually from HuggingFace if the data is there,
        otherwise from a different URL if possible.
        '''
        raise NotImplementedError("This is an abstract class.")
    
    def set_num_iterations(self, num_iterations: int) -> None:
        '''
        Sets the number of iterations to augment the dataset.
        Args:
            num_iterations: The number of iterations.
        '''
        self.num_iterations = num_iterations
    
    @abstractmethod
    def write(self):
        '''
        This code writes the newly-augmented data to disk in a specific output format (for now, forced jsonl).
        '''
        raise NotImplementedError("This is an abstract class.")
    
    @abstractmethod
    def _augment_one(self):
        '''
        This function takes a singular entry and reformats it to follow one of the templates.
        We then call map_dataset on this function to apply it to the entire dataset at once.
        '''
        raise NotImplementedError("This is an abstract class.")
    
    def _return_sharegpt(self, augmented_entry: str) -> dict:
        '''
        Returns a ShareGPT-formatted dictionary.
        '''
        # Structure the ShareGPT-formatted dictionary.
        # We use [SEP] as the separator between the human and model turn.
        assert len(augmented_entry.split("[SEP]")) == 2, f"Augmented entry has either no or more than one [SEP]. Entry:\n{augmented_entry}"
        human_turn, model_turn = augmented_entry.split("[SEP]")
        sharegpt_dict = {
            "conversations":
            [
                {
                    "from": "human",
                    "value": human_turn.strip(),
                },
                {
                    "from": "gpt",
                    "value": model_turn.strip(),
                }
            ]
        }
        return sharegpt_dict
