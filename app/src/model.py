from __future__ import annotations

# import torch
import os
import subprocess
import logging

from pathlib import Path
from utils import check_file_type

logger = logging.getLogger(f'main_logger.{__name__}')


def load_model(model_name: str):

    logger.info(f'Loading model {model_name}')
    current_path = Path(__file__).resolve().parent
    models_dir = "models"
    models_path = os.path.join(current_path, models_dir)

    if not os.path.exists(models_path):
        os.makedirs(models_path)

    model_url = f'https://huggingface.co/smthrgnl/{model_name}/resolve/main/{model_name}.pt'
    logger.info(f'Downloading {model_name} from HuggingFaces')
    subprocess.run(["wget", model_url, "-O", models_path], check=True)
    logger.info('Downloading done!')
    # model_path = os.path.join(models_path, model_name)

    logger.info('Loading decection model')
    # detection_model = db_resnet50(pretrained=True, pretrained_backbone=False)
    logger.info('Loading recognition model')

    # vocab = VOCABS['russian']
    # model_params = {'pretrained': False, 'pretrained_backbone': False, 'vocab': vocab}
    if model_name == 'ocr_crnn_mobilenet_v3_small':
        recognition_model = 'crnn_mobilenet_v3_small'  # crnn_mobilenet_v3_small(**model_params)
    if model_name == 'doctr_parseq':
        recognition_model = 'parseq'  # parseq(**model_params)
    if model_name == 'doctr_master':
        recognition_model = 'master'  # master(**model_params)

    logger.info('Loading model to torch')
    # recognition_params = torch.load(model_path, map_location="cuda:0", weights_only=False)
    # recognition_model.load_state_dict(recognition_params, strict=False)
    # ocr_model = ocr_predictor(detection_model, recognition_model)
    logger.info('Model is ready')

    return recognition_model  # ocr_model


def predict_text(ocr_model, file_path) -> str | None:

    file_type = check_file_type(file_path)
    if file_type == 'pdf':
        document = 'Load PDF file'
    elif file_type == 'image':
        document = 'Load image file'
    else:
        return None

    text = ocr_model(document).render()
    return text
