configfile: "snakemake_config.yaml"

rule all:
    input:
        expand("{split}/images", split=["ocr_model_training/train", "ocr_model_training/val", "ocr_model_training/test"]),
        expand("{split}/labels.json", split=["ocr_model_training/train", "ocr_model_training/val", "ocr_model_training/test"]),
        "ocr_model_training/doctr",
        "ocr_model_training/doctr_editable_installed.flag",
        "ocr_model_training/doctr_deps_installed.flag",
        "models_pushed.flag"

rule dvc_pull_dataset:
    output:
        "ocr_model_training/dataset.zip"
    shell:
        "cd ocr_model_training && dvc pull dataset.zip.dvc && cd .."

rule unzip_dataset:
    input:
        zipfile="ocr_model_training/dataset.zip"
    output:
        images_dir=directory("ocr_model_training/dataset/images"),
        labels_csv="ocr_model_training/dataset/labels.csv"
    shell:
        "python ocr_model_training/scripts/unzip.py --zip_path {input.zipfile} --out_dir ocr_model_training/dataset/ --labels_file labels.csv"

rule csv_to_json:
    input:
        labels_csv="ocr_model_training/dataset/labels.csv"
    output:
        labels_json="ocr_model_training/dataset/labels.json"
    shell:
        "python ocr_model_training/scripts/labels_csv_to_json.py --csv {input.labels_csv} --json {output.labels_json}"

rule split_dataset:
    input:
        images_dir="ocr_model_training/dataset/images",
        labels_json="ocr_model_training/dataset/labels.json"
    output:
        train_images=directory("ocr_model_training/train/images"),
        train_labels="ocr_model_training/train/labels.json",
        val_images=directory("ocr_model_training/val/images"),
        val_labels="ocr_model_training/val/labels.json",
        test_images=directory("ocr_model_training/test/images"),
        test_labels="ocr_model_training/test/labels.json"
    params:
        train_ratio=lambda w, input: config["split"]["train"],
        val_ratio=lambda w, input: config["split"]["val"],
        test_ratio=lambda w, input: config["split"]["test"]
    shell:
        "python ocr_model_training/scripts/split_dataset.py --images {input.images_dir} --labels {input.labels_json} --train_ratio {params.train_ratio} --val_ratio {params.val_ratio} --test_ratio {params.test_ratio}"

rule clone_doctr:
    output:
        directory("ocr_model_training/doctr")
    shell:
        "git clone https://github.com/something-original/doctr.git ocr_model_training/doctr"

rule install_doctr_deps:
    input:
        "ocr_model_training/doctr/pyproject.toml"
    output:
        "ocr_model_training/doctr_deps_installed.flag"
    shell:
        "python ocr_model_training/scripts/install_doctr_deps.py && python -c \"open('ocr_model_training/doctr_deps_installed.flag', 'a').close()\""

rule install_doctr_editable:
    input:
        directory("ocr_model_training/doctr")
    output:
        "ocr_model_training/doctr_editable_installed.flag"
    shell:
        "poetry run pip install -e ocr_model_training/doctr && python -c \"open('ocr_model_training/doctr_editable_installed.flag', 'a').close()\""

rule train_and_eval:
    input:
        train_images="ocr_model_training/train/images",
        train_labels="ocr_model_training/train/labels.json",
        val_images="ocr_model_training/val/images",
        val_labels="ocr_model_training/val/labels.json",
        test_images="ocr_model_training/test/images",
        test_labels="ocr_model_training/test/labels.json"
    output:
        "models/scores.json",
        "models/model_checkpoints.flag"
    shell:
        "python ocr_model_training/doctr_training.py --train_dir ocr_model_training/train --val_dir ocr_model_training/val --test_dir ocr_model_training/test --out_dir models"

rule push_models:
    input:
        "models/model_checkpoints.flag",
        "models/scores.json"
    output:
        "models_pushed.flag"
    shell:
        "cd models && dvc add . && dvc push && cd .. && python -c \"open('models_pushed.flag', 'a').close()\""
