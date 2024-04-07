import argparse

from tqdm import tqdm

from owarida.processors import PROCESSOR_MAP

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--datasets", help='List of datasets to augment, separated by commas. Default: all datasets.', default='all')
    parser.add_argument('-n', "--num_iterations", help='Number of times to run augmentations.', type=int, default=1)
    args = parser.parse_args()

    datasets = args.datasets.split(',') if args.datasets != 'all' else PROCESSOR_MAP.keys()

    for dataset in tqdm(datasets, desc='Augmenting datasets'):
        processor = PROCESSOR_MAP[dataset]
        processor.set_num_iterations(args.num_iterations)
        processor.augment()
        processor.write()

    print("Done!")

if __name__ == '__main__':
    main()
