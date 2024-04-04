import random
import re
import os

from typing import Generator

from .files import get_templates_dir

# RegEx used to find variants within the templates (e.g.: `%{Hi|Hello} there!`). 
VARIANT_REGEX = re.compile(r'%{(.+?)}')

def get_templates(dataset_name: str) -> list[list[str]]:
    '''
    Returns a list of templates for a specific dataset, divided into two levels.
    TODO: proper explanation
    Args:
        dataset_name: The name of the dataset.
    Returns:
        A group of templates structured into 
    '''
    templates_dir = get_templates_dir(dataset_name)
    # The overall list of templates, each entry being a list of variants of said template.
    templates = []
    for file_name in os.listdir(templates_dir):
        template_variants = []
        with open(os.path.join(templates_dir, file_name), 'r') as file:
            template = file.read()
            template_variants = list(generate_variants_for(template))

        templates.append(template_variants)
    return templates

def select_template(templates: list[list[str]]) -> str:
    '''
    Selects a random template from the list of templates.
    Args:
        templates: The list of templates.
    Returns:
        A random template.
    '''
    return random.choice(random.choice(templates))

def generate_variants_for(template: str) -> Generator[str, None, None]:
    '''
    Returns a list of variants for a specific template.
    Args:
        template: The template.
    Returns:
        A list of variants.
    '''
    if (match := re.search(VARIANT_REGEX, template)) is not None:
        # Once we have a "%{X|Y|Z}" matched inside the original string, we:
        # - Fetch .groups()[0] (which will give us `X|Y|Z`)
        # - Split by `|` (so we have ["X", "Y", "Z"])
        # - Filter out empty strings
        alternatives = filter(lambda x: x.strip(), match.groups()[0].split("|"))

        # Then, we break the string apart into what comes before and after the
        # alternatives, that way we can re-build with "prefix + choice + sufix".
        prefix = template[:match.start()]
        suffix = template[match.end():]

        for alternative in alternatives:
            variant = f'{prefix}{alternative}{suffix}'
            # However, some strings have multiple variant blocks. In that case,
            # we operate on them recursively until we have just regular strings
            # after generating all possible variants.
            still_have_match = re.search(VARIANT_REGEX, variant) is not None
            if still_have_match:
                for inner_variant in generate_variants_for(variant):
                    yield inner_variant
            else:
                yield variant
    else:
        yield template
