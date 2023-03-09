#!/usr/bin/env python3
from bertopic import BERTopic
from umap import UMAP
from sklearn.feature_extraction.text import CountVectorizer


class TopicModeling():
    """
    Uses BERTopic for Topic Modeling. Clusters the documents and chooses
    a set of Keywords to descripe a Cluster (Topic)
    """
    def __init__(self, dataset:'dataset', nr_topics:int):
        self.articles = dataset['article_text']
        
        # vectorizer_model to filter out stopwords
        vectorizer_model = CountVectorizer(
            ngram_range=(1, 1),
            stop_words="english"
        )

        nr_topics = nr_topics if nr_topics > 0 else None

        # topic_model 
        self.topic_model = BERTopic(
            language='english',
            top_n_words=5,
            calculate_probabilities=True,
            verbose=True,
            vectorizer_model=vectorizer_model,
            nr_topics=nr_topics
        )

        # Topic Modeling
        print("### Topic Modeling:  Fitting Model to Data")
        self.topics, _ = self.topic_model.fit_transform(self.articles)
        embeddings = self.topic_model._extract_embeddings(self.articles, method="document")
        self.umap_embeddings = UMAP(n_neighbors=15, n_components=2, min_dist=0.0, metric='cosine').fit_transform(embeddings)
        
        self.document_info = self.topic_model.get_document_info(self.articles)

        # generate topic labels
        print("### Topic Modeling:  Generating Label for each Topic")
        topic_label = self.topic_model.generate_topic_labels(nr_words=3, separator=", ")
        topic_label_tuples = (label.split(", ", 1) for label in topic_label)
        self.topic_label_dict = {key: value if key != '-1' else 'None' for (key,value) in topic_label_tuples}
        
        
    def add_topics(self, article:dict, idx:int)->dict:
        """
        Add a new column with a topic dictionary:
        {topic_label : <string>, probaility: <float>, x: <float>, y: <float>}
        """
        topic = dict()
    
        topic_id = self.document_info['Topic'][idx]
        topic['topic_name'] = self.topic_label_dict[str(topic_id)]
        topic['probability'] = self.document_info['Probability'][idx]
    
        x,y = tuple(self.umap_embeddings[idx])
        topic['x'] = x
        topic['y'] = y
    
        article['topic'] = topic

        return article



def main(dataset:'dataset', nr_topics:int=0)->'dataset':
    """
    Generates Clusters (sets of documents) with similar content, determines the
    topic for each Cluster and adds a column 'topic' to the dataset, with 
    information about the topic which is asigned to the document and x-, and
    y-coordinates of the document for Cluster visualisation.
    @param dataset: The dataset of documents for the topic modeling
    @param nr_topics: The number of Topics which should be generated
    @return 'dataset'
    """
    topic_modeling = TopicModeling(dataset, nr_topics)
    # Adds a column 'topic' to the data set
    print("### Topic Modeling:  Adding 'topic' column to Dataset")
    updated_dataset = dataset.map(topic_modeling.add_topics, with_indices=True)

    return updated_dataset
    

if __name__ == '__main__':
    from datasets import load_dataset

    # Load and modify dataset
    dataset = load_dataset("wikipedia", "20220301.simple", split="train")
    dataset = dataset.rename_column("title", "heading")
    dataset = dataset.rename_column("text", "article_text")

    # Reduce the ammount of data points
    dataset = dataset.select(list(range(5000)))

    updated_dataset = main(dataset)
    print(updated_dataset[0])
    updated_dataset.save_to_disk("test_data")
