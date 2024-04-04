# Util file for getting total filesizes of the datasets.

# Pre-calculated rough sizes of the storage taken up by each dataset, *including* input and output.
# We have to hardcode the sizes in there because otherwise it would be impossible to say beforehand
# how much storage space we roughly need for both the input files and output augmented files.

# The sizes are in MB.
DATASET_SIZES = {
    'arc_challenge': 0.1,
}


def _format_filesize(mb: float, digits: int = 2) -> float:
    '''
    Returns a very pretty filesize in whatever unit is most appropriate.
    Args:
        mb: The size in MB.
        digits: The number of digits to round the size to. (default: 2  )
    '''
    size = mb
    suffix = "MB"
    if mb < 1000:
        # GB
        size = mb / 1000
        suffix = "GB"
    return f"{round(size, digits)} {suffix}"

