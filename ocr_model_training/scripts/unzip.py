import os
import zipfile
import argparse
import tqdm


def unzip(zip_path, out_dir, labels_filename):
    images_dir = os.path.join(out_dir, 'images')
    labels_csv = os.path.join(out_dir, labels_filename)

    if os.path.exists(images_dir) and os.listdir(images_dir):
        if os.path.isfile(labels_csv) and os.path.getsize(labels_csv) > 0:
            print(f"{images_dir} and {labels_csv} already exist and are non-empty. Skipping extraction.")
            return

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        members = zip_ref.namelist()
        for member in tqdm.tqdm(members, desc='Extracting'):
            zip_ref.extract(member, out_dir)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Unzip a zip file and move images to images directory")
    parser.add_argument("--zip_path", type=str, required=True, help="Path to the zip file")
    parser.add_argument("--out_dir", type=str, required=True, help="Path to the output directory")
    parser.add_argument("--labels_file", type=str, required=True, help="Path to the labels file")
    args = parser.parse_args()
    unzip(args.zip_path, args.out_dir, args.labels_file)
