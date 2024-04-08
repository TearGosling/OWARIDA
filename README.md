# Open reWritten, Augmented and (sometimes) Reversed Instruction Data for All
This repository contains the code for assembling OWARIDA in parts or in full, depending on your specification.
Further information to come soon. This repo is a heavy WIP.

## Installation
The usual command:
`pip3 install -r requirements.txt`

## Usage:
`python build.py --datasets all --num_iterations 1`
By default, all datasets are selected for augmenting, but you can specify specific datasets with a comma-separated list. The valid 

## List of datasets
- `arc_challenge`
    - The "challenge" section of AI2's [ARC dataset](https://huggingface.co/datasets/allenai/ai2_arc).
- `arc_easy`
    - The "easy" section of AI2's [ARC dataset](https://huggingface.co/datasets/allenai/ai2_arc).
