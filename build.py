import argparse

from tqdm import tqdm

from owarida.processors import PROCESSOR_MAP

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--datasets", help='List of datasets to augment, separated by commas. Default: all datasets.', default='all')
    parser.add_argument('-n', "--num_iterations", help='Number of times to run augmentations.', type=int, default=1)
    args = parser.parse_args()

    datasets = args.datasets.split(',') if args.datasets != 'all' else list(PROCESSOR_MAP.keys())
    for dataset in (pbar := tqdm(datasets)):
        # Update the progress bar for the current dataset.
        pbar.write(f"Processing dataset '{dataset}'")
        processor = PROCESSOR_MAP[dataset]
        processor.set_num_iterations(args.num_iterations)
        processor.augment()
        processor.write()

    dataset_str = ', '.join(datasets[:-1])
    if len(datasets) > 2:
        dataset_str += f" and {datasets[-1]} have"
        dataset_str = "Datasets " + dataset_str
    else:
        dataset_str = dataset_str[:-2] + datasets[-1]
        dataset_str = f"Datasets {dataset_str} have" if len(datasets) > 1 \
        else f"Dataset {dataset_str} has"

    print(f"{dataset_str} been augmented and saved to disk. Check the output directories for the augmented datasets.")

if __name__ == '__main__':
    main()
