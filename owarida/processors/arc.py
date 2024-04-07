import random
import sys

from enum import Enum
from typing import Optional

from datasets import Dataset, concatenate_datasets, load_dataset

from .base import BaseProcessor
from ..utils import get_data_dir, get_templates, get_output_dir, select_template

# Enum to make indexing much easier.
class AnswerChoice(Enum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4

class ArcProcessor(BaseProcessor):
    def __init__(self, split_name: str) -> None:
        '''
        The processor for the ARC dataset.
        Args:
            split_name: The split of the dataset to use. Only valid splits: 'easy', 'challenge'.
        '''
        self.data_dir = get_data_dir(f'arc_{split_name}')
        self.output_dir = get_output_dir(f'arc_{split_name}')
        self.full_split_name = 'ARC-Easy' if split_name == 'easy' else 'ARC-Challenge'
        self.num_iterations = 0 # To be set later.

        self.dataset = self.download()
        self.new_dataset = None # Placeholder for the augmented dataset.
        self.templates = get_templates('arc')

    def augment(self):
        for _ in range(self.num_iterations):
            if self.new_dataset is None:
                # First run of augmentations. Create the first one by applying augmentations to old dataset.
                self.new_dataset = self.dataset.map(self._augment_one, remove_columns=self.dataset.column_names,) #batched=True)
            else:
                # New runs of augmentations. Append the new augmentations to the existing dataset.
                temp_dataset = self.dataset.map(self._augment_one, remove_columns=self.dataset.column_names, batched=True)
                self.new_dataset = concatenate_datasets([self.new_dataset, temp_dataset])

    def download(self) -> Dataset:
        '''
        Downloads the ARC dataset from HuggingFace.
        '''
        dataset = load_dataset(
            'allenai/ai2_arc',
            self.full_split_name,
            split="train",
            cache_dir=self.data_dir # Saves the files locally.
        )
        return dataset
    
    def set_num_iterations(self, num_iterations: int) -> None:
        '''
        Sets the number of iterations to augment the dataset.
        Args:
            num_iterations: The number of iterations.
        '''
        self.num_iterations = num_iterations
    
    def write(self, data_dir: Optional[str] = None) -> None:
        '''
        Writes the augmented dataset to disk.
        Args:
            data_dir: The directory to write the augmented dataset to,
            if it needs to be something other than the default. Set to None to use the default.
        '''
        data_dir = data_dir if data_dir is not None else self.output_dir
        self.new_dataset.to_json(
            f"{data_dir}/augmented.jsonl",
            orient="records",
            lines=True
        )
    
    def _augment_one(self, entry: dict) -> dict:
        '''
        Takes a single entry from the dataset and augments it by applying a template to it.
        The output is in ShareGPT format, which is what we use as our dataset format.
        '''
        augmented_entry = select_template(self.templates)
        # First, we substitute "{{question}}" in with the actual question.
        augmented_entry = augmented_entry.replace("{{question}}", entry['question'])

        # Get the correct answer now so that we can assign the right letter to it later
        # during letter choice scrambling.
        numeric_answer = entry['answerKey'] in "1234"
        if numeric_answer:
            answer_idx = int(entry['answerKey']) - 1
        else:
            answer_idx = getattr(AnswerChoice, entry['answerKey']).value
        correct_answer = entry['choices']['text'][answer_idx]
        augmented_entry = augmented_entry.replace("{{answer}}", correct_answer)

        # Closed QA task.
        if "answer_choices}}" in augmented_entry:
            # Choose a random separator for the purposes of further generalizing.
            separator = random.choice([": ", " - ", ") ", ". "])

            # Now we can shuffle the answer choices...
            answers = entry['choices']['text']
            random.shuffle(answers)
            # ...get the new letter for the correct answer...
            correct_answer_idx = answers.index(correct_answer)
            # ...and do a reverse lookup on the enum to find the new letter, if the answer choice isn't numeric.
            correct_answer_letter = AnswerChoice(correct_answer_idx).name if not numeric_answer else str(correct_answer_idx + 1)

            # There are two potential ways to format the answer choices in the ARC templates.
            # The first is {{letter_with_answer}}, which combines the letter, the separator, and the answer in one go.
            if "{{letter_with_answer}}" in augmented_entry:
                correct_answer = f"{correct_answer_letter}{separator}{correct_answer}"
                augmented_entry = augmented_entry.replace("{{letter_with_answer}}", correct_answer)
            # The other scenario is where the letter and the answer are separately mentioned in the template.
            else:
                # We replace {{letter}} with the correct letter.
                augmented_entry = augmented_entry.replace("{{letter}}", correct_answer_letter)
                # And replace {{answer}} with the correct answer.
                augmented_entry = augmented_entry.replace("{{answer}}", correct_answer)

            # Finally, we have to insert the answer choices into the template.
            answer_choices = ""
            str_to_replace = "{{answer_choices}}"
            # Iterate over the enum.
            enum_iterator = list(AnswerChoice)
            # Knock out the enum iterator if the number of answer choices is less than the number of enum values.
            if len(answers) < len(enum_iterator):
                num_missing = len(enum_iterator) - len(answers)
                enum_iterator = enum_iterator[:-num_missing]
            # One of the templates designed to boost generalizaiton
            # is where answer choices are not in alphabetical/numerical order but rather scrambled.
            # Check for that and if this exists, scramble the enum iterator.
            if "{{jumbled_answer_choices}}" in augmented_entry:
                random.shuffle(enum_iterator)
                str_to_replace = "{{jumbled_answer_choices}}"

            for i in enum_iterator:
                try:
                    if numeric_answer:
                        answer_choices += f"{i.value + 1}{separator}{answers[i.value]}\n"
                    else:
                        answer_choices += f"{i.name}{separator}{answers[i.value]}\n"
                except IndexError:
                    print(f"IndexError: i.value: {i.value}, answers: {answers}, len(answers): {len(answers)}")
            # Replace the answer choices in the template.
            augmented_entry = augmented_entry.replace(str_to_replace, answer_choices.strip())

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
