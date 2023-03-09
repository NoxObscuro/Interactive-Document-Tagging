#!/usr/bin/env python3
import os
import sys
from datasets import load_dataset
from datasets import load_from_disk
import key_word_extraction as kwe
import topic_modeling as tm


def main(subset:str, data_points:int, nr_topics:int, n_keywords:int):
    dataset = None

    if os.path.isdir(f"./import/dataset-{subset}"):
        print("### Preprocessing:  Found dataset on disk; Loading Dataset...")
        dataset = load_from_disk(f"./import/dataset-{subset}")
    # No dataset found in import
    else:
        # import does not exist: create ist
        if not os.path.exists("./import"):
            print("### Preprocessing:  No import directory found; Creating import...")
            os.makedirs("./import")
        # import exits but ist not a directory
        elif not os.path.isdir("./import"):
            sys.exit(f"{os.getcwd()}/import is not a directory")
        # download dataset and save it to ./import
        print("### Preprocessing:  Dataset localy not found; Downloading...")
        dataset = load_dataset("wikipedia", subset, split="train")
        print("### Preprocessing:  Saving Dataset to import/")
        dataset.save_to_disk(f"./import/dataset-{subset}")

    # if export does not exist: create it
    if not os.path.exists("./export"):
        print("### Preprocessing:  No export directory found; Creating export...")
        os.makedirs("./export")
    elif not os.path.isdir("./export"):
        sys.exit(f"{os.getcwd()}/export is not a directory")

    # reduce the ammount of data points
    if data_points > 0:
        print("### Preprocessing:  Shuffling Dataset...")
        dataset = dataset.shuffle()
        print(f"### Preprocessing:  Reducing Datapoints to {data_points}...")
        dataset = dataset.select(list(range(data_points)))

    print("### Preprocessing:  Renaming 'title' column to 'heading'...")
    dataset = dataset.rename_column("title", "heading")
    print("### Preprocessing:  Renaming 'text' column to 'article_text'...")
    dataset = dataset.rename_column("text", "article_text")
    
    updated_dataset = tm.main(dataset, nr_topics)
    updated_dataset = kwe.main(updated_dataset, n_keywords)

    print("### Preprocessing:  Save updated Dataset to export/...")
    updated_dataset.save_to_disk("./export/article_data")
    
    
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        prog="Interactive Document Tagging: Preprocessing",
        description='Preprocess the Wikipedia dataset for topic modeling'
    )
    parser.add_argument('subset',
        type=str,
        help="a subset Dataset from the Wikipedia dataset (https://huggingface.co/datasets/wikipedia)",
        default="20220301.simple"
    )
    parser.add_argument('-n', '--number-data-points',
        metavar='n',
        action='store',
        type=int,
        help="select only the first n datapoints of the dataset; use 0 to use all",
        default=0
    )
    parser.add_argument('-t', '--topics',
        metavar='t',
        action='store',
        type=int,
        help="The number of topics/clusters which should be created; 0 for a dynamic ammount",
        default=0
    )
    parser.add_argument('-k', '--keywords',
        metavar='t',
        action='store',
        type=int,
        help="The number of keywords per document which should be created",
        default=5
    )

    args = parser.parse_args()
    main(args.subset, args.number_data_points, args.topics, args.keywords)