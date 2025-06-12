import pandas as pd
import json
import os
import argparse


def csv_to_json(csv_path, json_path):

    df = pd.read_csv(csv_path, sep=';')
    df['words'] = df['words'].str.replace('\\', '')
    df = df[df['words'].str.len() < 30]
    labels = {os.path.basename(row['filename']): row['words'] for _, row in df.iterrows()}
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert labels.csv to labels.json.")
    parser.add_argument('--csv', required=True, help='Path to labels.csv')
    parser.add_argument('--json', required=True, help='Output path for labels.json')
    args = parser.parse_args()
    csv_to_json(args.csv, args.json)
