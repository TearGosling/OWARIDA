import random

from typing import Optional

from datasets import concatenate_datasets, load_dataset

from .base import BaseProcessor
from ..utils import (
    AnswerChoice,
    get_data_dir,
    get_templates,
    get_output_dir,
    select_template
)
BLANK_SUBS = ["_", "___", "[BLANK]", "<BLANK>", "(BLANK)", "[TO FILL IN]", "----------"]

class WinograndeProcessor(BaseProcessor):
    def __init__(self) -> None:
        '''
        The processor for the Winogrande dataset.
        '''
        self.data_dir = get_data_dir(f'winogrande')
        self.output_dir = get_output_dir(f'winogrande')
        self.num_iterations = 0 # To be set later.

        self.dataset = self.download()
        self.new_dataset = None # Placeholder for the augmented dataset.

    def augment(self):
        '''
        This code augments by applying templates to the data.
        '''
        self.templates = get_templates('winogrande')
        for _ in range(self.num_iterations):
            if self.new_dataset is None:
                # First run of augmentations. Create the first one by applying augmentations to old dataset.
                self.new_dataset = self.dataset.map(self._augment_one, remove_columns=self.dataset.column_names,) #batched=True)
            else:
                # New runs of augmentations. Append the new augmentations to the existing dataset.
                temp_dataset = self.dataset.map(self._augment_one, remove_columns=self.dataset.column_names,) #batched=True)
                self.new_dataset = concatenate_datasets([self.new_dataset, temp_dataset])
    
    def download(self):
        '''
        Downloads the Winogrande dataset from HuggingFace.
        '''
        dataset = load_dataset(
            'winogrande',
            'winogrande_debiased',
            split="train",
            cache_dir=self.data_dir # Saves the files locally.
        )
        return dataset
    
    def write(self, output_dir: Optional[str] = None) -> None:
        '''
        Writes the augmented dataset to disk.
        Args:
            data_dir: The directory to write the augmented dataset to,
            if it needs to be something other than the default. Set to None to use the default.
        '''
        output_dir = output_dir if output_dir is not None else self.output_dir
        self.new_dataset.to_json(
            f"{output_dir}/augmented.jsonl",
            orient="records",
            lines=True
        )
    
    def _augment_one(self, entry: dict) -> dict:
        '''
        This function takes a singular entry and reformats it to follow one of the templates.
        The output is in ShareGPT format, which is what we use as our dataset format.
        '''
        # Get the template.
        augmented_entry = select_template(self.templates)
        # We get the question, but first, we take the blank, represented with char "_",
        # and spice it up by widening the variety of strings that can be used to indicate a blank.
        blank = f"{random.choice(BLANK_SUBS)}"
        # Sometimes lower-case it too, to account for case-sensitive tokenizers.
        if random.random() < 0.5:
            blank = blank.lower()

        # Same principle with letters.
        lowered_letters = False
        if random.random() < 0.5:
            lowered_letters = True

        question = entry['sentence'].replace("_", blank)
        # Now we substitute the question into the template.
        augmented_entry = augmented_entry.replace("{{question}}", question)

        # Get the possible answers.
        answers = [entry['option1'], entry['option2']]
        correct_answer_idx = int(entry['answer']) - 1
        correct_answer = answers[correct_answer_idx]

        # Closed QA task.
        if "answer_choices}}" in augmented_entry:
            # Choose a random separator for the purposes of further generalizing.
            separator = random.choice([": ", " - ", ") ", ". "])
            # Shuffle answer choices.
            random.shuffle(answers)

            # Develop answer choices string.
            answer_choices_str = ""
            for idx, answer in enumerate(answers):
                option_string = ""
                if "{{letter_answer_choices}}" in augmented_entry:
                    letter = AnswerChoice(idx).name.lower() if lowered_letters else AnswerChoice(idx).name
                    option_string = f"{letter}{separator}{answer}"
                    str_to_replace = "{{letter_answer_choices}}"
                elif "{{number_answer_choices}}" in augmented_entry:
                    option_string = f"{idx+1}{separator}{answer}"
                    str_to_replace = "{{number_answer_choices}}"
                if idx == correct_answer_idx:
                    correct_answer = option_string
                answer_choices_str += option_string + "\n"
            answer_choices_str = answer_choices_str.strip()
            # And replace.
            augmented_entry = augmented_entry.replace(str_to_replace, answer_choices_str)
        
        # Replace the correct answer.
        augmented_entry = augmented_entry.replace("{{answer}}", correct_answer)
        return self._return_sharegpt(augmented_entry)
