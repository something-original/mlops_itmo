from __future__ import annotations
import torch
import logging
import os
from pathlib import Path
import time
import yaml
import subprocess
from typing import Dict, Any, Tuple
from doctr.io import DocumentFile
from doctr.models import ocr_predictor, db_resnet50, master, parseq
from src.vocabs import VOCABS
from pymongo import MongoClient
from datetime import datetime
from src.utils import check_file_type

logger = logging.getLogger(f'main_logger.{__name__}')


class DocumentComparisonModel:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.model_name = self.config['models']['default']
        model_path = self.config['models']['paths'][self.model_name]
        root_path = Path(__file__).resolve().parent.parent.parent
        self.model_path = os.path.join(root_path, model_path)

        self.client = MongoClient(self.config['database']['uri'])
        self.db = self.client[self.config['database']['db_name']]
        self.metrics_collection = self.db[self.config['metrics']['collection_name']]

        self._load_model()

    def _load_model(self):

        try:
            subprocess.run(['git', 'checkout', self.config["models"]["version"]], check=True)
            subprocess.run(['dvc', 'checkout'], check=True)
            subprocess.run(['dvc', 'pull', self.model_path + '.dvc'], check=True)

            logger.info(f"Successfully pulled model from DVC: {self.model_path}")

            self.detection_model = db_resnet50(pretrained=True, pretrained_backbone=True)

            recognition_kwargs = {'pretrained': False, 'pretrained_backbone': False, 'vocab': VOCABS['multilingual']}
            if self.model_name == 'master':
                self.recognition_model = master(**recognition_kwargs)
            elif self.model_name == 'parseq':
                self.recognition_model = parseq(**recognition_kwargs)
            else:
                raise ValueError(f"Invalid model name: {self.model_name}")

            recognition_params = torch.load(self.model_path, map_location="cuda:0", weights_only=False)
            self.recognition_model.load_state_dict(recognition_params, strict=False)

            self.model = ocr_predictor(det_arch=self.detection_model, reco_arch=self.recognition_model,
                                       pretrained=False)

            logger.info(f"Successfully loaded model: {self.model_name}")
        except subprocess.CalledProcessError as e:
            logger.error(f"DVC pull failed: {str(e)}")
            raise Exception(f"Failed to pull model from DVC: {str(e)}")
        except Exception as e:
            logger.error(f"Model loading failed: {str(e)}")
            raise Exception(f"Failed to load model: {str(e)}")

    def _calculate_metrics(self, start_time: float, end_time: float, doc1_text: str, doc2_text: str) -> Dict[str, Any]:

        inference_time = end_time - start_time

        total_chars = max(len(doc1_text), len(doc2_text))
        matching_chars = sum(1 for a, b in zip(doc1_text, doc2_text) if a == b)
        accuracy = matching_chars / total_chars if total_chars > 0 else 0

        current_time = datetime.now()
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        metrics = {
            "model_name": self.model_name,
            "inference_time": inference_time,
            "accuracy": accuracy,
            "timestamp": timestamp_str,
            "total_chars": total_chars,
            "matching_chars": matching_chars
        }

        self.metrics_collection.update_one(
            {
                "model_name": self.model_name,
                "timestamp": timestamp_str
            },
            {"$set": metrics},
            upsert=True
        )

        return metrics

    def compare_documents(self, doc1_path: str | None, doc2_path: str | None,
                          doc1_text: str | None, doc2_text: str | None) -> Tuple[Dict[str, Any], Dict[str, Any]]:

        start_time = time.time()

        if doc1_path is not None and doc2_path is not None:
            doc1_type = check_file_type(doc1_path)
            doc2_type = check_file_type(doc2_path)

            if doc1_type == "wrong format" or doc2_type == "wrong format":
                raise ValueError("Wrong file format")

            if doc1_type == "pdf":
                doc1 = DocumentFile.from_pdf(doc1_path)
            elif doc1_type == "image":
                doc1 = DocumentFile.from_images(doc1_path)

            if doc2_type == "pdf":
                doc2 = DocumentFile.from_pdf(doc2_path)
            elif doc2_type == "image":
                doc2 = DocumentFile.from_images(doc2_path)

            result1 = self.model(doc1)
            result2 = self.model(doc2)

            doc1_words = [
                word.value
                for page in result1.pages
                for block in page.blocks
                for line in block.lines
                for word in line.words
            ]
            doc2_words = [
                word.value
                for page in result2.pages
                for block in page.blocks
                for line in block.lines
                for word in line.words
            ]

            doc1_text = " ".join(doc1_words)
            doc2_text = " ".join(doc2_words)

        end_time = time.time()

        metrics = self._calculate_metrics(start_time, end_time, doc1_text, doc2_text)

        return {
            "doc1_text": doc1_text,
            "doc2_text": doc2_text,
            "metrics": metrics
        }

    def get_metrics(self) -> Dict[str, Any]:

        model_names = self.metrics_collection.distinct("model_name")

        if not model_names:
            return {"error": "No metrics found for any model"}

        all_metrics = {}
        for model_name in model_names:
            metrics = list(self.metrics_collection.find(
                {"model_name": model_name},
                {"_id": 0}
            ))

            all_metrics[model_name] = {
                "avg_inference_time": sum(m["inference_time"] for m in metrics) / len(metrics),
                "avg_accuracy": sum(m["accuracy"] for m in metrics) / len(metrics),
                "total_tries": len(metrics)
            }

        return all_metrics
