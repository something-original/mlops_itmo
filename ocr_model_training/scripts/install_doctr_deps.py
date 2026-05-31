import toml
import subprocess
import sys
from pathlib import Path

doctr_pyproject = Path("ocr_model_training/doctr/pyproject.toml")
if not doctr_pyproject.exists():
    print("doctr/pyproject.toml not found!")
    sys.exit(1)

data = toml.load(doctr_pyproject)
deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})

deps = {k: v for k, v in deps.items() if k.lower() != "python"}

for dep, version in deps.items():
    if isinstance(version, dict):
        version_str = version.get("version", "")
    else:
        version_str = version
    dep_str = f"{dep}{version_str if version_str else ''}"
    print(f"Adding {dep_str} to poetry environment...")
    subprocess.run(["poetry", "add", dep_str], check=True)
