import random
import re
import os

from .files import get_templates_dir

# RegEx used to find variants within the templates (e.g.: `%{Hi|Hello} there!`). 
VARIANT_REGEX = re.compile(r'%{(.+?)}')

def get_templates(dataset_name: str) -> list[str]:
    '''
    Returns a list of templates for a specific dataset.
    TODO: proper explanation
    Args:
        dataset_name: The name of the dataset.
    Returns:
        All the templates for the dataset.
    '''
    templates_dir = get_templates_dir(dataset_name)
    templates = []
    for file_name in os.listdir(templates_dir):
        with open(os.path.join(templates_dir, file_name), 'r') as file:
            template = file.read()
            templates.append(template)

    return templates

def select_template(templates: list[str]) -> str:
    '''
    Selects a random template from the list of templates.
    Args:
        templates: The list of templates.
    Returns:
        A random template.
    '''
    # Get a base template for which we can generate a variant on the fly for.
    base_template = random.choice(templates)
    if (match := re.search(VARIANT_REGEX, base_template)) is not None:
        # First copy the base template so that we can not worry about anything weird
        # during finditer.
        selected_template = base_template
        for variant in re.finditer(VARIANT_REGEX, base_template):
            # Get the variant and choose a random one.
            # We do a hacky trim to get rid of the surrounding brackets and %.
            variant_text = variant.group(0)
            choices = variant_text[2:-1].split("|")
            choice = random.choice(choices)
            # Replace the variant text ONCE with the chosen one,
            # so that any duplicate variants are not replaced also.
            selected_template = selected_template.replace(variant_text, choice, 1)
        # The template has been selected and we can now return it.
        return selected_template
    else:
        return base_template
