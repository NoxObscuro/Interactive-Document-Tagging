#!/usr/bin/env python3
from bertopic import BERTopic
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer


class TopicModeling:
    """
    Uses BERTopic for Topic Modeling. Clusters the documents and chooses a set of
    Keywords to descripe a Cluster (Topic)
    """
    
    def __init__(self, dataset: 'dataset', nr_topics: int = None, language: str = 'english', stop_words=None, lemmatization: bool = False, min_length_of_keywords: int = 1, max_length_of_keywords: int = 1):
        self.articles = dataset['article_text']

        # vectorizer_model to filter out stopwords
        vectorizer_model = CountVectorizer(
            ngram_range=(min_length_of_keywords, max_length_of_keywords),
            stop_words=stop_words
        )

        if lemmatization:
            from nltk import word_tokenize
            from nltk.stem import WordNetLemmatizer

            class LemmaTokenizer:
                def __init__(self):
                    self.wnl = WordNetLemmatizer()

                def __call__(self, doc):
                    return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

            vectorizer_model = CountVectorizer(
                tokenizer=LemmaTokenizer(),
                ngram_range=(min_length_of_keywords, max_length_of_keywords),
                stop_words=stop_words
            )

        nr_topics = nr_topics if nr_topics > 0 else None

        # topic_model
        self.topic_model = BERTopic(
            language=language,
            top_n_words=5,
            calculate_probabilities=False,
            vectorizer_model=vectorizer_model,
            nr_topics=nr_topics,
            verbose=True
        )

        # Topic Modeling
        print("### Topic Modeling:  Fitting Model to Data")
        self.topics, _ = self.topic_model.fit_transform(self.articles)
        embeddings = self.topic_model._extract_embeddings(
            self.articles, method="document")
        self.umap_embeddings = UMAP(
            n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine').fit_transform(embeddings)

        self.document_info = self.topic_model.get_document_info(self.articles)

        # generate topic labels
        print("### Topic Modeling:  Generating Label for each Topic")
        topic_label = self.topic_model.generate_topic_labels(
            nr_words=3, separator=", ")
        topic_label_tuples = (label.split(", ", 1) for label in topic_label)
        self.topic_label_dict = {
            key: value if key != '-1' else 'None' for (key, value) in topic_label_tuples}

    def add_topics(self, article: dict, idx: int) -> dict:
        """
        Add a new column with a topic dictionary:
        {topic_label : <string>, probaility: <float>, x: <float>, y: <float>}
        """
        topic = dict()

        topic_id = self.document_info['Topic'][idx]
        topic['topic_name'] = self.topic_label_dict[str(topic_id)]
        topic['probability'] = self.document_info['Probability'][idx]

        x, y = tuple(self.umap_embeddings[idx])
        topic['x'] = x
        topic['y'] = y

        article['topic'] = topic

        return article


def main(dataset: 'dataset', nr_topics: int = 0, language: str = 'english', stop_words=None, lemmatization: bool = False, min_length_of_keywords: int = 1, max_length_of_keywords: int = 1) -> 'dataset':
    """
    Generates Clusters (sets of documents) with similar content, determines the
    topic for each Cluster and adds a column 'topic' to the dataset, with 
    information about the topic which is asigned to the document and x-, and
    y-coordinates of the document for Cluster visualisation.

    @param dataset: The dataset of documents for the topic modeling
    @param int nr_topics: The number of Topics which should be generated
    @param str language: The language of the documents
    @param stop_words: list of strings with stop_words or a known string for built in stop_words e.g. 'english'
    @param bool lemmatization: should lemmatization be used for the creation of the topic representation
    @param int min_length_of_keywords: minimal number of words for a keyword in the topic representation
    @param int max_length_of_keywords: maximal number of words for a keyword in the topic representation
    @return 'dataset'
    """
    topic_modeling = TopicModeling(dataset, nr_topics)
    # Adds a column 'topic' to the data set
    print("### Topic Modeling:  Adding 'topic' column to Dataset")
    updated_dataset = dataset.map(topic_modeling.add_topics, with_indices=True)

    return updated_dataset
