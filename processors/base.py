from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    def __init__(self):
        '''
        The base class for all processors.
        '''
        self.num_iterations = 0 # To be set later.
        raise NotImplementedError("This is an abstract class.")
    
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
