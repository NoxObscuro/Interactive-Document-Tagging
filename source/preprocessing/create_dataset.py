#!/usr/bin/env python3
import json
import os
from datasets import load_dataset, load_from_disk


def from_json(path:str):
    """
    Create Dataset from a json file with the following structure:
    [
        {
            "title": "<title>",
            "text": "<text>",
            "url": "<url>",
        }
    ]
    @param str path: a relativ path from /data/import.
    """
    if os.path.isdir("./import/dataset-paperless"):
        print("### Preprocessing:  Found dataset on disk; Loading Dataset...")
        return load_from_disk(f"./import/dataset-{path.split('/')[-1]}")

    try:
        dataset = load_dataset("json", data_files=os.path.join("/", "data", "import", path), split='train')
    except IOError:
        sys.exit(f"{sys.argv[0]}: File '{path}' does not exist. Can't read stop words from file.")

    def assign_id(document, idx):
        document["id"] = idx
        return document

    dataset.map(assign_id, with_indices=True)
    dataset.save_to_disk(f"./import/dataset-{path.split('/')[-1]}")
    
    return dataset


def from_paperless_manifest(base_dir: str):
    """
    Create Dataset from paperless-ngx manifest.json
    """
    if os.path.isdir(os.path.join(".", "import", "dataset-paperless")):
        print("### Preprocessing:  Found dataset on disk; Loading Dataset...")
        return load_from_disk(os.path.join(".", "import", "dataset-paperless"))

    if not os.path.isdir(os.path.join(".", "import", base_dir)):
        sys.exit(f"{sys.argv[0]}: {base_dir}' does not exist or is not an directory.")
    elif not os.path.exists(os.path.join(".", "import", base_dir, "manifest.json")):
        sys.exit(f"{sys.argv[0]}: {base_dir}' does not contain a manifest.json.")
    
    with open(os.path.join(".", "import", base_dir, "manifest.json"), "r") as f:
        json_data = json.load(f)

    documents = list()
    for i, element in enumerate(json_data):
        if element["model"] == "documents.document":
            documents.append({
                "title": element["fields"]["title"],
                "text": element["fields"]["content"],
                "url": "",
                "id": i
            })

    with open("dataset.json", "w") as f:
        json.dump(documents, f, ensure_ascii=False, indent=4)

    dataset = load_dataset("json", data_files="dataset.json", split='train')
    dataset.save_to_disk("./import/dataset-paperless")
    
    os.remove("dataset.json")
    
    return dataset
