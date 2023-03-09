from elasticsearch.client import IndicesClient
from elasticsearch import Elasticsearch
from datasets import load_from_disk
import json
# TODO: mount the docker volume outside into a local path?
# Standard setting are used, might need to be changed
class DBCreater:
    def __init__(self):
        self.es_client = Elasticsearch(
            "http://localhost:9200",
            http_auth=["elastic", "changeme"],
        )
        self.es_index_client = IndicesClient(self.es_client)
        self.article_db = "articles"
        self.tag_db = "tags"
        self.article_db_configuration = {
    "settings": {
        "index": {"number_of_replicas": 2},
        "analysis": {
            "filter": {
                "ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 15,
                },
            },
            "analyzer": {
                "ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "ngram_filter"],
                },
            },
        },
    },
    
    
    "mappings": {
        "properties": {
            "id": {"type": "long"},
            "heading": {"type": "text"},
            "article_text": {"type": "text"},
    # a keyword consists of the word and its probability to appear
            "keywords": {"type": "nested",
                        "properties": {"word": {"type": "text"}, "similarity": {"type": "float"}}},
            "topic": {"type": "nested",
                      "properties": {"topic_name": {"type": "text"}, "x": {"type": "float"}, "y": {"type": "float"}, "probability": {"type": "float"}}},
            "url": {"type": "text"},
    "tags": {"type": "keyword"}
        }
    }}
        self.tags_db_configuration = {
      "settings": {
        "index": {"number_of_replicas": 2},
        "analysis": {
            "filter": {
                "ngram_filter": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 15,
                },
            },
            "analyzer": {
                "ngram_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "ngram_filter"],
                },
            },
        },
    },
    
    
    
    "mappings": {
        "properties": {
            "id": {"type": "long"},
            "name": {"type": "keyword"},
            "description": {"type": "text"},}
    }

}

    def create_article_db(self):
        self.es_index_client.delete(index=self.article_db, ignore=404)
        self.es_index_client.create(index=self.article_db, body=self.article_db_configuration)
    
    def fill_article_db(self, data):
        actions = []
        for i in range(len(data)):
            article = data[i]
            action = {"index": {"_index": self.article_db, "_id": int(article["id"])}}
            doc = {
                "id": int(article["id"]),
                "heading": article["heading"],
                "article_text": article["article_text"],
                "keywords": article["keywords"],
                "topic": article["topic"],
                "url": article["url"],
                "tags": []
                }
            actions.append(json.dumps(action))
            actions.append(json.dumps(doc))

        with open("article_demo.json", "w") as fo:
            fo.write("\n".join(actions))
            self.es_client.bulk(body="\n".join(actions))

    def create_tag_db(self):
        self.es_index_client.delete(index=self.tag_db, ignore=404)
        self.es_index_client.create(index=self.tag_db, body=self.tags_db_configuration)


if __name__ == '__main__':
    data = load_from_disk("article_data")
    db_create = DBCreater()
    print("### Writing data to database...")
    db_create.create_article_db()
    db_create.fill_article_db(data)
