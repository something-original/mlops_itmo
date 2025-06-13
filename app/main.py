import os
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.model import DocumentComparisonModel
from src.database import DocumentDatabase
from src.utils import setup_logging
from pathlib import Path
import uvicorn

setup_logging('w', 'logs.log')
app = FastAPI(title="Document Comparison API")

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


@app.post("/compare")
async def compare_documents(
    doc1: UploadFile = File(...),
    doc2: UploadFile = File(...)
):
    """Compare two documents and return their text content and comparison metrics"""
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
            # Use cached results
            result = model.compare_documents(
                doc1_cached["text"],
                doc2_cached["text"]
            )
        else:
            result = model.compare_documents(temp1_path, temp2_path)

            if not doc1_cached:
                db.save_document(temp1_path, result["doc1_text"])
            if not doc2_cached:
                db.save_document(temp2_path, result["doc2_text"])

        os.unlink(temp1_path)
        os.unlink(temp2_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
    """Get aggregated metrics for the current model"""
    try:
        return model.get_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
