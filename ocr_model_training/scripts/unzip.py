import zipfile
import sys


def unzip(zip_path, out_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(out_dir)


if __name__ == '__main__':
    unzip(sys.argv[1], sys.argv[2])
