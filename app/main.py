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
            result = model.compare_documents(
                doc1_path=None,
                doc2_path=None,
                doc1_text=doc1_cached["text"],
                doc2_text=doc2_cached["text"],
            )
        else:
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

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics():
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

    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
