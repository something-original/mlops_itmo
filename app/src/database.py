import hashlib
import os
import yaml
from typing import Optional, Dict, Any
from pymongo import MongoClient
from bson.binary import Binary
from pathlib import Path


class DocumentDatabase:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.client = MongoClient(self.config['database']['uri'])
        self.db = self.client[self.config['database']['db_name']]
        self.documents = self.db.documents

    def _calculate_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def get_document(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get document from database if it exists"""
        doc_hash = self._calculate_hash(file_path)
        return self.documents.find_one({"hash": doc_hash})

    def save_document(self, file_path: str, text: str) -> Dict[str, Any]:
        """Save document to database"""
        doc_hash = self._calculate_hash(file_path)
        document = {
            "hash": doc_hash,
            "text": text,
            "file_path": file_path
        }
        self.documents.update_one(
            {"hash": doc_hash},
            {"$set": document},
            upsert=True
        )
        return document

    def delete_document(self, file_path: str) -> bool:
        doc_hash = self._calculate_hash(file_path)
        result = self.documents.delete_one({"hash": doc_hash})
        return result.deleted_count > 0

    def delete_all_documents(self) -> int:
        result = self.documents.delete_many({})
        return result.deleted_count

    def get_all_documents(self) -> list:
        return list(self.documents.find({}, {"_id": 0}))


root_path = Path(__file__).resolve().parent.parent
yaml_path = os.path.join(root_path, "config.yaml")
config = yaml.safe_load(open(yaml_path))
mongo_uri = config["database"]["uri"]

client = MongoClient(mongo_uri)
db = client["image_db"]
collection = db["images"]


def save_image(filename: str, image_bytes: bytes):
    collection.insert_one({"filename": filename, "image": Binary(image_bytes)})


def get_image(filename: str) -> Optional[bytes]:
    result = collection.find_one({"filename": filename})
    if result:
        return result["image"]
    return None
