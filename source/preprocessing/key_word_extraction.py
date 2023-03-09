#!/usr/bin/env python3
from keybert import KeyBERT

class KeywordExtractor():
    def __init__(self, n_keywords:int):
        self.kw_model = KeyBERT()
        self.n_keywords = n_keywords


    def get_keywords(self, document:str)->list:
        """
        Generates keywords from 'article' and returns a list of dictionaries of the
        form: [{"word": <keyword>, "similarity": <float>}, ...]
        The similarity indicates how similar the keyword is to the article.
        @param str document: the document from which the Keywords should be extracted
        @return list
        """
        # Generate Keywords from the String article.
        keywords = self.kw_model.extract_keywords(document, keyphrase_ngram_range=(1, 1), stop_words='english', top_n=self.n_keywords)
        
        # Convert list of tuples to list of dictionaries
        keyword_dicts = [{"word" : keyword[0], "similarity": keyword[1]} for keyword in keywords]

        return keyword_dicts


    def add_keywords(self, document:dict)->dict:
        """
        Adds a new column with a list of keywords to the dataset.
        @param dict document: a row from the dataset to which the keywords should be added
        @return dict
        """
        document["keywords"] = self.get_keywords(document['article_text'])
        return document


def main(dataset:'dataset', n_keywords:int)->'dataset':
    print("### Keyword extraction:  Adding 'keywords' column to Dataset")
    keyword_extractor = KeywordExtractor(n_keywords)
    return dataset.map(keyword_extractor.add_keywords)
    

if __name__ == '__main__':
    from datasets import load_dataset
    dataset = load_dataset("wikipedia", "20220301.simple", split="train")

    # reduce the ammount of data points
    dataset = dataset.select(list(range(100)))
    
    updated_dataset = main(dataset, 3)
    print(updated_dataset[0])