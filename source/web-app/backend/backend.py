from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient
from time import sleep

class DocumentClient:
    def __init__(self):
        self.es_client = Elasticsearch(
            "localhost:9200",
            http_auth=["elastic", "changeme"],
        )
        self.es_index_client = IndicesClient(self.es_client)
        self.article_db = "articles"
        self.tag_db = "tags"
        self.size = 1000


    ###########ARTICLE DB############
    def get_article_text(self, id):
        """
        Input: ID of article
        Output: Text of article as String
        """
        return self.es_client.get(index=self.article_db, id=id)["_source"]["article_text"]
    
    def get_article_name_and_topic(self, id):
        """
        Input: ID of article
        Output: Name and topic of article as Dict with keys "heading" and "topic"
        """
        result =self.es_client.get(index=self.article_db, id=id)["_source"]
        return {"heading": result["heading"], "topic": result["topic"]}
    
    def add_tag_to_articles(self, tag, ids):
        """
        Input: List of tags and list of IDs where you want to add the tags
        Output: None
        """
        query =    {
            "match": { "name" : tag
            }
        }
        if tag != "":
            tag_id =self.es_client.search(size=self.size, index=self.tag_db, query=query)["hits"]["hits"][0]["_id"]
            for id in ids:
                article = self.es_client.get(index=self.article_db, id=id)
                doc = article["_source"]
                if "tags" in doc.keys() and tag_id not in doc["tags"]:
                    doc["tags"].append(tag_id)
                else:
                    doc["tags"] = [tag_id]
                self.es_client.update(index=self.article_db, id=id, body={"doc": doc})
            return "SUCCESS"
    
    def delete_tag_from_articles(self, tag, ids):
        query =    {
            "match": { "name" : tag
            }
        }

        if tag != "":
            tag_id =self.es_client.search(size=self.size, index=self.tag_db, query=query)["hits"]["hits"][0]["_id"]
            for id in ids:
                article = self.es_client.get(index=self.article_db, id=id)
                doc = article["_source"]
                if "tags" in doc.keys() and tag_id in doc["tags"]:

                    doc["tags"].remove(tag_id)
                    self.es_client.update(index=self.article_db, id=id, body={"doc": doc})
        
    
    def get_all_articles(self):
        """
        Input: None
        Output: List of all articles as Dicts with keys "id", "heading" and "topic"
        """
        all_articles = []
        articles = self.es_client.search(size=self.size, index=self.article_db, filter_path=["hits.hits._id", "hits.hits._source.heading", "hits.hits._source.topic"], query={"match_all": {}})["hits"]["hits"]
        for article in articles:
            all_articles.append({"id": article["_id"], "heading": article["_source"]["heading"], "topic": article["_source"]["topic"]})
        return all_articles
    
    def get_all_keywords(self):
        """
        Input: None
        Output: List of all keywords as Strings"""
        all_keywords = []
        articles = self.es_client.search(size=self.size, index=self.article_db, query={"match_all": {}})["hits"]["hits"]
        for article in articles:
            keywords = article["_source"]["keywords"]
            for keyword in keywords:
                #if keyword["word"] not in all_keywords: #TODO: DO we want duplicates or not?
                all_keywords.append(keyword["word"])
        return all_keywords
    
    def get_article_id_by_tag(self, tag):
        """
        Input: Tag as String
        Output: List of IDs of articles with the same tag
        """
        tag_id = self.es_client.search(size=self.size, index=self.tag_db, query={"match": {"name": tag}})["hits"]["hits"][0]["_id"]
        ids = self.es_client.search(size=self.size, index=self.article_db, filter_path=["hits.hits._id"], query={"match": {"tags": tag_id}})["hits"]["hits"]
        all_ids = []
        for id in ids:
            all_ids.append(id["_id"])
        return all_ids

    def get_keywords_by_ids(self, ids):
        """
        Input: List of IDs
        Output: List of keywords as Strings"""
        all_keywords = []
        for id in ids:
            try:
                keywords = self.es_client.get(index=self.article_db, id=id)["_source"]["keywords"]
            except:
                continue
            for keyword in keywords:
                all_keywords.append(keyword["word"]) #TODO: DO we want duplicates or not?
        return all_keywords

    
    def get_all_articles_id(self):
        """
        Input: None
        Output: List of all article ids as Strings
        """
        hits = self.es_client.search(size=self.size, index=self.article_db, query={"match_all": {}})["hits"]["hits"]
        all_articles = []
        for hit in hits:
            all_articles.append(hit["_id"])
        return all_articles

    def get_url_from_id(self, ids):
        urls = []
        for id in ids:
            urls.append(self.es_client.get(index=self.article_db, id=id)["_source"]["url"])
        return urls

    ############TAG DB################

    def get_all_tags_id(self):
        """
        Input: None
        Output: List of all tag ids as Strings
        """
        hits = self.es_client.search(size=self.size, index=self.tag_db, query={"match_all": {}})["hits"]["hits"]
        all_tags = []
        for hit in hits:
            all_tags.append(hit["_id"])
        return all_tags
    
    def get_tags_by_ids(self, ids, filter=True):
        """
        Input: List of article ids
        Output: List of tags as Strings"""
        all_tags = []
        for id in ids:
            article = self.es_client.get(index=self.article_db, id=id)["_source"]
            if "tags" in article.keys():
                tag_ids = article["tags"]
                if tag_ids == []:
                    continue
                query = {
    "terms": {
      "_id": tag_ids
    }
  }
                tags = self.es_client.search(size=self.size, index=self.tag_db, query=query)["hits"]["hits"]
                if filter:
                    for tag in tags:
                        tag_id = tag["_source"]["name"]
                        if tag_id not in all_tags:
                            all_tags.append(tag_id)
                else:
                    for tag in tags:
                        tag_id = tag["_source"]["name"]
                        all_tags.append(tag_id)

        return all_tags
    
    
    def get_tags_by_partial_words(self, part):
        query= {
    "regexp": {
      "name": {
        "value": part+".*",
        "flags": "ALL",
        "max_determinized_states": 10000,
        "rewrite": "constant_score"
      }
    }
  }
        tags = self.es_client.search(size=self.size, index=self.tag_db, query=query)["hits"]["hits"]
        all_tags = []
        for tag in tags:
            all_tags.append(tag["_source"]["name"])
        return all_tags
    
    def add_new_tag(self, tag, description):
        """
        Input: Tag as String, Description as String
        Output: ID of new tag as Sting or if it already exists "TAG ALREADY EXISTS""" #TODO: I dont think the front end needs the tag ID
        if tag not in self.get_all_tags():
            new_tag = self.es_client.index(index=self.tag_db, body={"name": tag, "description": description})
            sleep(2)
            return new_tag["_id"]
        return "TAG ALREADY EXISTS"
    
    def get_all_tags(self, filter=True):
        """
        Input: None
        Output: List of all tags as Strings"""
        if filter:
            all_tags = []
            try:
                tags_dict = self.es_client.search(size=self.size, index=self.tag_db, query={"match_all": {}}, filter_path=["hits.hits._source.name"])["hits"]["hits"]
                for tag in tags_dict:
                    all_tags.append(tag["_source"]["name"])
                return all_tags
            except:
                return []
        else:
            
            all_tags=[]
            all_ids = self.get_all_articles_id()
            for id in all_ids:
                article = self.es_client.get(index=self.article_db, id=id)["_source"]
                if "tags" in article.keys():
                    tag_ids = article["tags"]
                    for tag_id in tag_ids:
                        all_tags.append(self.es_client.get(index=self.tag_db, id=tag_id)["_source"]["name"])
            return all_tags


    def delete_tag(self, tag):
        tag = self.es_client.search(size=self.size, index=self.tag_db, query={"match": {"name": tag}})["hits"]["hits"][0]
        id = tag["_id"]
        self.es_client.delete(index=self.tag_db, id=id)
        for article in self.get_all_articles_id():
            tags_of_article = self.es_client.get(index=self.article_db, id=article)["_source"]["tags"]
            if id in tags_of_article:
                tags_of_article.remove(id)
                self.es_client.update(index=self.article_db, id=article, body={"doc": {"tags": tags_of_article}})
        print("deleted tag")
