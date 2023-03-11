#!/usr/bin/env python3
import os
import sys
from datasets import load_dataset, load_from_disk
import create_dataset as create_ds
import keyword_extraction as kwe
import topic_modeling as tm


def create_needed_directories():
    """
    Create import and export directory if not present
    """
    # import does not exist: create ist
    if not os.path.exists("./import"):
        print("### Preprocessing:  No import directory found; Creating import...")
        os.makedirs("./import")

    # import exits but ist not a directory
    elif not os.path.isdir("./import"):
        sys.exit(f"{os.getcwd()}/import is not a directory")

    # if export does not exist: create it
    if not os.path.exists("./export"):
        print("### Preprocessing:  No export directory found; Creating export...")
        os.makedirs("./export")
    elif not os.path.isdir("./export"):
        sys.exit(f"{os.getcwd()}/export is not a directory")


def get_stop_words(file_name:str)->list:
    """
    Extract whitespace seperated stop words from file.
    @param str: file_name, name of a file in /data/import containing the stop words
    @return list
    """
    try:
        with open(os.path.join("/data/import", file_name), 'r') as f:
            lines = f.readlines()
    except IOError:
        sys.exit(f"{sys.argv[0]}: File '{file_name}' does not exist. Can't read stop words from file.")
        
    stop_words = "\n".join(lines)
    return stop_words.split()


def get_dataset(subset: str) -> 'dataset':
    """
    Get Wikipedia Dataset from Hugging Face
    """
    dataset = None

    if os.path.isdir(f"./import/dataset-{subset}"):
        print("### Preprocessing:  Found dataset on disk; Loading Dataset...")
        dataset = load_from_disk(f"./import/dataset-{subset}")
    # No dataset found in import
    else:
        # download dataset and save it to ./import
        print("### Preprocessing:  Dataset localy not found; Downloading...")
        dataset = load_dataset("wikipedia", subset, split="train")
        print("### Preprocessing:  Saving Dataset to import/")
        dataset.save_to_disk(f"./import/dataset-{subset}")

    return dataset


def main(subset: str, json_file:str, paperless_dir:str, data_points: int, nr_topics: int, n_keywords: int, stop_words:str, min_length_of_keywords:int, max_length_of_keywords:int, language:str, model:str):
    """
    Update Dataset and run topic modeling and keyword extration
    """
    create_needed_directories()
    dataset = None
    if subset is not None:
        dataset = get_dataset(subset)
    elif json_file is not None:
        dataset = create_ds.from_json(json_file)
    else:
        dataset = create_ds.from_paperless_manifest(paperless_dir)

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

    updated_dataset = tm.main(dataset, nr_topics, language, stop_words, min_length_of_keywords, max_length_of_keywords)
    updated_dataset = kwe.main(updated_dataset, n_keywords, stop_words, min_length_of_keywords, max_length_of_keywords, model)

    print("### Preprocessing:  Save updated Dataset to export/...")
    updated_dataset.save_to_disk("./export/article_data")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        prog="itd-preprocessing.py",
        description="The preprocessing Script for the Interactive Document Tagging.\n" +
            "It needs a .json file with a set of documents/articles, each with a " +
            "title, the text and a url. Or a string which stands for a subset of " +
            "the Wikipedia dataset from Hugging Face (https://huggingface.co/datasets/wikipedia)." +
            "This script then creates or extends the dataset with the following " +
            "features: topics with a label, a probability, and x and y coordinates " +
            "of each document used for clustering. Furthermore, a set of keywords, " +
            "which represent the respective document in the best possible way.",
        epilog="Topic Modeling with BERTopic and KeyBERT"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('-w', '--wikipedia',
        metavar="SUBSET",
        type=str,
        help="The subset of the Wikipedia dataset (https://huggingface.co/datasets/wikipedia)",
        default=None
    )
    source.add_argument('-j', '--json',
        metavar="JSON FILE",
        type=str,
        help="A file path from the import directory to a json from which the Data should be parsed",
        default=None
    )
    source.add_argument('-p', '--paperless',
        metavar="MANIFEST.JSON",
        type=str,
        help="A file path relative to the import directory to a manifest.json " +
            "created by a paperless export. See (https://docs.paperless-ngx.com)",
        default=None
    )
    parser.add_argument('-n', '--number-data-points',
        metavar='n',
        action='store',
        type=int,
        help="Select only the first n datapoints of the dataset. Set to 0 to use all (Default)",
        default=0
    )
    parser.add_argument('-t', '--topics',
        metavar='t',
        action='store',
        type=int,
        help="If there BERTopic genereates more than t Topics let BERTopic iteratively " +
            "merger the to most similar topics until there are only t Topics left." +
            "Set to 0 for a dynamic ammount (Default)",
        default=0
    )
    parser.add_argument('-k', '--keywords',
        metavar='k',
        action='store',
        type=int,
        help="Specifies that k keywords are to be created per document. Default: 5",
        default=5
    )
    parser.add_argument('--stop-words',
        action='store',
        metavar='STOP_WORDS',
        type=str,
        help="File path, relative to the import directory, to a space seperated " +
            "list of stop words or the string 'english' for a pre defined list of " +
            "english stop words which should be removed before the keywords are " +
            "extracted or the topic representation is created. Default: None (don't" +
            "remove stop words)",
        default=None
    )
    parser.add_argument('--min',
        metavar='MIN',
        action='store',
        type=int,
        help="The minimal number of words per keywords for the keyword extraction. " +
            "Default: 1",
        default=1
    )
    parser.add_argument('--max',
        metavar='MAX',
        action='store',
        type=int,
        help="The maximal number of words per keywords for the keyword extraction. " +
            "Default: 1",
        default=1
    )
    parser.add_argument('-l', '--language',
        action='store',
        metavar='LANGUAGE',
        type=str,
        help="The language of the documents. E.g. 'english', 'german', 'multilingual'. " +
            "Default: 'english'",
        choices=["english", "multilingual", "german", 'afrikaans', 'albanian', 'amharic', 
            'arabic', 'armenian', 'assamese', 'azerbaijani', 'basque', 'belarusian',
            'bengali', 'bengali romanize', 'bosnian', 'breton', 'bulgarian', 'burmese',
            'burmese zawgyi font', 'catalan', 'chinese (simplified)', 'chinese (traditional)',
            'croatian', 'czech', 'danish', 'dutch', 'esperanto', 'estonian', 'filipino',
            'finnish', 'french', 'galician', 'georgian', 'greek', 'gujarati', 'hausa',
            'hebrew', 'hindi', 'hindi romanize', 'hungarian', 'icelandic', 'indonesian',
            'irish', 'italian', 'japanese', 'javanese', 'kannada', 'kazakh', 'khmer',
            'korean', 'kurdish (kurmanji)', 'kyrgyz', 'lao', 'latin', 'latvian',
            'lithuanian', 'macedonian', 'malagasy', 'malay', 'malayalam', 'marathi',
            'mongolian', 'nepali', 'norwegian', 'oriya', 'oromo', 'pashto', 'persian',
            'polish', 'portuguese', 'punjabi', 'romanian', 'russian', 'sanskrit',
            'scottish gaelic', 'serbian', 'sindhi', 'sinhala', 'slovak', 'slovenian',
            'somali', 'spanish', 'sundanese', 'swahili', 'swedish', 'tamil', 'tamil romanize',
            'telugu', 'telugu romanize', 'thai', 'turkish', 'ukrainian', 'urdu',
            'urdu romanize', 'uyghur', 'uzbek', 'vietnamese', 'welsh', 'western frisian',
            'xhosa', 'yiddish'],
        default='english'
    )
    parser.add_argument('-L','--lemmatization',
        action='store_true',
        help="Should lemmatization be applied before the creation of the topic " +
            "representation. Default: False",
        default=False
    )

    args = parser.parse_args()
    stop_words = args.stop_words
    if stop_words != "english" and stop_words is not None:
        stop_words = get_stop_words(stop_words)

    model = None
    if args.language != 'english':
        model = 'paraphrase-multilingual-MiniLM-L12-v2'
    
    main(args.wikipedia, args.json, args.paperless, args.number_data_points, args.topics, args.keywords, stop_words, args.min, args.max, args.language, model)
