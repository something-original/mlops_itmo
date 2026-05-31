import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.model import DocumentComparisonModel
from src.database import DocumentDatabase
from src.utils import setup_logging
from src.metrics import (
    REQUEST_COUNT, REQUEST_LATENCY, MODEL_ACCURACY, MODEL_INFERENCE_TIME,
    CACHE_HITS, CACHE_MISSES, HEALTH_CHECK
)
from prometheus_client import make_asgi_app
from pathlib import Path
import uvicorn
import time

setup_logging('w', 'logs.log')
app = FastAPI(title="Document Comparison API")


metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

root_path = Path(__file__).resolve().parent
config_path = os.path.join(root_path, "config.yaml")
model = DocumentComparisonModel(config_path)
db = DocumentDatabase(config_path)


HEALTH_CHECK.set(1)
MODEL_ACCURACY.labels(model_name=model.model_name).set(0)
MODEL_INFERENCE_TIME.labels(model_name=model.model_name).set(0)


@app.post("/compare")
async def compare_documents(
    doc1: UploadFile = File(...),
    doc2: UploadFile = File(...)
):
    start_time = time.time()
    REQUEST_COUNT.labels(model_name=model.model_name).inc()

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp1, \
             tempfile.NamedTemporaryFile(delete=False) as temp2:
            temp1.write(await doc1.read())
            temp2.write(await doc2.read())
            temp1_path = temp1.name
            temp2_path = temp2.name

        doc1_cached = db.get_document(temp1_path)
        doc2_cached = db.get_document(temp2_path)

        if doc1_cached and doc2_cached:
            CACHE_HITS.inc()
            result = model.compare_documents(
                doc1_path=None,
                doc2_path=None,
                doc1_text=doc1_cached["text"],
                doc2_text=doc2_cached["text"],
            )
        else:
            CACHE_MISSES.inc()
            result = model.compare_documents(
                doc1_path=temp1_path,
                doc2_path=temp2_path,
                doc1_text=None,
                doc2_text=None,
            )

            if not doc1_cached:
                db.save_document(temp1_path, result["doc1_text"])
            if not doc2_cached:
                db.save_document(temp2_path, result["doc2_text"])

        os.unlink(temp1_path)
        os.unlink(temp2_path)

        MODEL_ACCURACY.labels(model_name=model.model_name).set(result["metrics"]["accuracy"])
        MODEL_INFERENCE_TIME.labels(model_name=model.model_name).set(result["metrics"]["inference_time"])
        REQUEST_LATENCY.labels(model_name=model.model_name).observe(time.time() - start_time)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model-metrics")
async def get_model_metrics():
    try:
        return model.get_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/cache")
async def delete_cache():
    try:
        deleted_count = db.delete_all_documents()
        return {"message": f"Successfully deleted {deleted_count} cached documents"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    HEALTH_CHECK.set(1)
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
