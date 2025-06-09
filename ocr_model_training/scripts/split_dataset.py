import os
import json
import shutil
import argparse
import random
from pathlib import Path


def split_dataset(images_dir, labels_json, out_dir, train_ratio, val_ratio, seed=42):

    random.seed(seed)
    with open(labels_json, 'r', encoding='utf-8') as f:
        labels = json.load(f)

    image_files = list(labels.keys())
    random.shuffle(image_files)

    n = len(image_files)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    train_files = image_files[:n_train]
    val_files = image_files[n_train:n_train+n_val]
    test_files = image_files[n_train+n_val:]

    splits = {'train': train_files, 'val': val_files, 'test': test_files}

    for split, files in splits.items():

        split_dir = os.path.join(out_dir, split)
        images_out = os.path.join(split_dir, 'images')
        os.makedirs(images_out, exist_ok=True)
        split_labels = {}

        for fname in files:
            src = os.path.join(images_dir, fname)
            dst = os.path.join(images_out, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                split_labels[fname] = labels[fname]

        with open(os.path.join(split_dir, 'labels.json'), 'w', encoding='utf-8') as f:
            json.dump(split_labels, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":

    root_dir = Path(__file__).resolve().parent.parent

    parser = argparse.ArgumentParser(description="Split dataset into train, val, test.")
    parser.add_argument('--images_dir', required=True, help='Path to images directory')
    parser.add_argument('--labels_path', required=True, help='Path to labels.json')
    parser.add_argument('--out_dir', required=True, help='Output directory')
    parser.add_argument('--train_ratio', type=float, required=True, help='Train split ratio')
    parser.add_argument('--val_ratio', type=float, required=True, help='Validation split ratio')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()

    images_path = os.path.join(root_dir, args.images_dir)
    labels_path = os.path.join(root_dir, args.labels_path)
    out_path = os.path.join(root_dir, args.out_dir)

    split_dataset(images_path, labels_path, out_path, args.train_ratio, args.val_ratio, args.seed)
