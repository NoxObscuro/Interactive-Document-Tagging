#!/usr/bin/env python3
from keybert import KeyBERT


class KeywordExtractor:
    """
    Uses keyBERT to extract a list of Keywords for a given Document.
    """

    def __init__(self, documents:list, n_keywords: int, stop_words=None, min_length_of_keywords: int = 1, max_length_of_keywords: int = 1, model:str=None):
        """
        @param stop_words: list of strings of stop words or known string w.g. 'english'
        @param int min_length_of_keywords: minimal number of words for a keyword
        @param int max_length_of_keywords: maximal number of words for a keyword
        """
        self.kw_model = None
        if model is None:
            self.kw_model = KeyBERT()
        else:
            self.kw_model = KeyBERT(model=model)

        self.n_keywords = n_keywords
        self.stop_words = stop_words
        self.min_length_of_keywords = min_length_of_keywords
        self.max_length_of_keywords = max_length_of_keywords
        self.keywords_per_document = self.get_keywords(documents)

    def get_keywords(self, documents: list) -> list:
        """
        Generates keywords from 'article' and returns a list of dictionaries of the
        form: [[{"word": <keyword>, "similarity": <float>}], [...], ...]
        The similarity indicates how similar the keyword is to the article.

        @param str document: the document from which the Keywords should be extracted
        @return list
        """
        # Generate Keywords from the String article.
        keywords_per_document = self.kw_model.extract_keywords(
            documents,
            keyphrase_ngram_range=(
                self.min_length_of_keywords, self.max_length_of_keywords),
                stop_words=self.stop_words,
                top_n=self.n_keywords
        )

        # Convert list of tuples to list of dictionaries
        keyword_dicts = [[{"word": keyword[0], "similarity": keyword[1]}
                         for keyword in document] for document in keywords_per_document]

        return keyword_dicts

    def add_keywords(self, document: dict, idx) -> dict:
        """
        Adds a new column with a list of keywords to the dataset.
        @param dict document: a row from the dataset to which the keywords should be added
        @return dict
        """
        document["keywords"] = self.keywords_per_document[idx]
        return document


def main(dataset: 'dataset', n_keywords: int, stop_words=None, min_length_of_keywords: int = 1, max_length_of_keywords: int = 1, model:str=None) -> 'dataset':
    print("### Keyword extraction:  Adding 'keywords' column to Dataset")
    keyword_extractor = KeywordExtractor(dataset['article_text'], n_keywords, stop_words, min_length_of_keywords, max_length_of_keywords, model)
    return dataset.map(keyword_extractor.add_keywords, with_indices=True)
