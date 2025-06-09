import argparse
import os
import subprocess
import json
import torch
from doctr.models import db_resnet50, parseq, master, crnn_mobilenet_v3_small, ocr_predictor
from doctr.datasets.vocabs import VOCABS
from doctr.io import DocumentFile
from tqdm import tqdm


def run_training(model_name, train_dir, val_dir, out_dir, device=0, epochs=10):
    script = os.path.join('doctr', 'references', 'recognition', 'train_pytorch.py')
    vocab = 'russian'
    cmd = [
        'python', script, model_name,
        '--train_path', train_dir,
        '--val_path', val_dir,
        '--vocab', vocab,
        '--epochs', str(epochs),
        '--name', model_name,
        '--device', str(device),
        '--pretrained'
    ]
    subprocess.run(cmd, check=True, cwd='doctr')

    src = os.path.join('doctr', f'{model_name}.pt')
    dst = os.path.join(out_dir, f'{model_name}.pt')
    if os.path.exists(src):
        os.rename(src, dst)


def evaluate_model(model_name, checkpoint_path, test_dir):
    detection_model = db_resnet50(pretrained=True, pretrained_backbone=False)

    if model_name == 'ocr_crnn_mobilenet_v3_small':
        recognition_model = crnn_mobilenet_v3_small(
            pretrained=False, pretrained_backbone=False, vocab=VOCABS['russian']
        )
    elif model_name == 'doctr_parseq':
        recognition_model = parseq(
            pretrained=False, pretrained_backbone=False, vocab=VOCABS['russian']
        )
    elif model_name == 'doctr_master':
        recognition_model = master(
            pretrained=False, pretrained_backbone=False, vocab=VOCABS['russian']
        )
    else:
        raise ValueError(f"Unknown model: {model_name}")
    recognition_params = torch.load(
        checkpoint_path,
        map_location="cuda:0" if torch.cuda.is_available() else "cpu",
        weights_only=False
    )
    recognition_model.load_state_dict(recognition_params, strict=False)
    ocr_model = ocr_predictor(detection_model, recognition_model)

    test_labels_path = os.path.join(test_dir, 'labels.json')
    test_images_dir = os.path.join(test_dir, 'images')

    with open(test_labels_path, 'r', encoding='utf-8') as f:
        labels = json.load(f)

    scores = []

    for img_name, real_text in tqdm(labels.items(), desc=f'Eval {model_name}'):
        img_path = os.path.join(test_images_dir, img_name)
        if not os.path.exists(img_path):
            continue
        doc = DocumentFile.from_images(img_path)
        result = ocr_model(doc)
        pred_text = result.render()

        if len(real_text) == 0:
            score = 1.0 if pred_text == '' else 0.0
        else:
            correct = sum(
                1 if gt_c == pred_c else 0 for gt_c, pred_c in zip(real_text, pred_text)
            )
            score = correct / len(real_text)
        scores.append(score)

    return sum(scores) / max(1, len(scores))


def main(train_dir, val_dir, test_dir, out_dir):

    os.makedirs(out_dir, exist_ok=True)

    for model_name in ['ocr_crnn_mobilenet_v3_small', 'doctr_parseq', 'doctr_master']:
        run_training(model_name, train_dir, val_dir, out_dir)

    ctc_loss_results = {}

    for model_name in ['ocr_crnn_mobilenet_v3_small', 'doctr_parseq', 'doctr_master']:
        checkpoint = os.path.join(out_dir, f'{model_name}.pt')
        ctc_loss = evaluate_model(model_name, checkpoint, test_dir)
        ctc_loss_results[model_name] = ctc_loss

    for split in ['train', 'val', 'test']:
        split_dir = train_dir if split == 'train' else val_dir if split == 'val' else test_dir
        labels_path = os.path.join(split_dir, 'labels.json')
        with open(labels_path, 'r', encoding='utf-8') as f:
            ctc_loss_results[f'{split}_samples'] = len(json.load(f))

    ctc_loss_results['dataset_version'] = 'v1' 

    with open(os.path.join(out_dir, 'ctc_loss.json'), 'w', encoding='utf-8') as f:
        json.dump(ctc_loss_results, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, 'model_checkpoints.flag'), 'w') as f:
        f.write('done')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--train_dir', required=True)
    parser.add_argument('--val_dir', required=True)
    parser.add_argument('--test_dir', required=True)
    parser.add_argument('--out_dir', required=True)
    args = parser.parse_args()
    main(args.train_dir, args.val_dir, args.test_dir, args.out_dir) 