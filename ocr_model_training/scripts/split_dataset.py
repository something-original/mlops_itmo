import os
import json
import shutil
import argparse
import random


def split_dataset(images_dir, labels_json, train_ratio, val_ratio, test_ratio, seed=42):

    random.seed(seed)
    with open(labels_json, 'r', encoding='utf-8') as f:
        labels = json.load(f)

    image_files = list(labels.keys())
    random.shuffle(image_files)

    n = len(image_files)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)
    n_test = int(n * test_ratio)

    train_files = image_files[:n_train]
    val_files = image_files[n_train:n_train+n_val]
    test_files = image_files[n_train+n_val:n_train+n_val+n_test]

    # Use output directories as expected by Snakemake (relative to project root)
    train_path = os.path.join('ocr_model_training', 'train')
    val_path = os.path.join('ocr_model_training', 'val')
    test_path = os.path.join('ocr_model_training', 'test')

    splits = {train_path: train_files, val_path: val_files, test_path: test_files}

    for split_dir, files in splits.items():

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

    print('Split ready')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Split dataset into train, val, test.")
    parser.add_argument('--images_dir', required=True, help='Path to images directory')
    parser.add_argument('--labels_path', required=True, help='Path to labels.json')
    parser.add_argument('--train_ratio', type=float, required=True, help='Train split ratio')
    parser.add_argument('--val_ratio', type=float, required=True, help='Validation split ratio')
    parser.add_argument('--test_ratio', type=float, required=True, help='Test split ratio')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    args = parser.parse_args()

    split_dataset(args.images_dir, args.labels_path, args.train_ratio, args.val_ratio, args.test_ratio, args.seed)
