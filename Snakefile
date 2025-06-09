configfile: "snakemake_config.yaml"

rule all:
    input:
        expand("{split}/images", split=["ocr_model_training/train", "ocr_model_training/val", "ocr_model_training/test"]),
        expand("{split}/labels.json", split=["ocr_model_training/train", "ocr_model_training/val", "ocr_model_training/test"]),
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
        images_dir="ocr_model_training/dataset/images",
        labels_csv="ocr_model_training/dataset/labels.csv"
    shell:
        "python ocr_model_training/scripts/unzip.py {input.zipfile} ocr_model_training/dataset/"

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
        val_ratio=lambda w, input: config["split"]["val"]
    shell:
        "python ocr_model_training/scripts/split_dataset.py --images {input.images_dir} --labels {input.labels_json} --out ocr_model_training --train_ratio {params.train_ratio} --val_ratio {params.val_ratio}"

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
        "python ocr_model_training/doctr_training.py --train_dir train --val_dir val --test_dir test --out_dir models"

rule push_models:
    input:
        "models/model_checkpoints.flag",
        "models/scores.json"
    output:
        "models_pushed.flag"
    shell:
        "cd models && dvc add . && dvc push && cd .. && touch models_pushed.flag"
