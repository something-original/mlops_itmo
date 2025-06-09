# Snakemake Pipeline Instructions

## Prerequisites
- Python 3.10+
- Poetry
- DVC (with HuggingFace remote configured)
- Docker (for containerized run)
- HuggingFace account/token (for dataset/model push)

## Local Run

1. **Install dependencies:**
   ```
   poetry install --no-root
   ```
2. **Authenticate DVC with HuggingFace:**
   ```sh
   dvc remote modify hf --local auth basic
   dvc remote modify hf --local user <your_hf_username>
   dvc remote modify hf --local password <your_hf_token>
   ```
3. **Run the pipeline:**
   ```
   snakemake -s Snakefile --cores all
   ```
   - Adjust `config.yaml` for split ratios if needed.

## Docker Run

1. **Build the Docker image:**
   ```sh
   docker build -f Dockerfile.snakemake -t snakemake-ocr .
   ```
2. **Run the pipeline in Docker:**
   ```sh
   docker run --rm -it -v $(pwd):/workspace snakemake-ocr
   ```
   - For DVC/HuggingFace authentication, you may need to pass environment variables or mount your `.dvc` and `.cache` directories.

## Notes
- The pipeline will:
  1. Download and unzip the dataset (via DVC)
  2. Preprocess and split the data
  3. Train and evaluate models
  4. Push model checkpoints and metadata to HuggingFace (via DVC)
- All split ratios and paths are configurable in `config.yaml`.
- For custom training logic, edit `ocr_model_training/doctr_training.py`. 