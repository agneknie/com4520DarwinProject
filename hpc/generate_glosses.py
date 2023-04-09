
if __name__ == '__main__':
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('--n-glosses', type=int)
    parser.add_argument('--input-file', type=str)
    parser.add_argument('--output-file', type=str)
    parser.add_argument('--root', type=str, default='.')
    args = parser.parse_args()

    sys.path.append(os.path.join(args.root, 'src'))
    from data.idiom_dataset import load_dataset
    from data.util import write_csv
    from data.gloss import Glosses

    glosses = Glosses(args.n_glosses)

    header, data = load_dataset(args.input_file, transform=glosses.get_individual_glosses)

    write_csv([header] + data, args.output_file)
