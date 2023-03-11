# Interactive Document Tagging 
This project was created as part of the project "Anwendungen der künstlichen Intelligenz"
in the winter semester 2022/2023 at the University of Hamburg. Authors of this project
are Alan Kniep, Julia Janßen, Maja Lingl, Valerie Bartel and Vanessa Maeder.

## Use case and functionality
The goal of our project is to cluster large quantities of documents or articles
according to their content, and to visualize these clusters to get a fast overview
of a document collection. Additionally, the application should enable the user to
tag documents in an interactive way. 

For the visualization, we represent the clustered articles in a scatter plot in
the center of our web application. On the left side, the user can toggle between
two bar charts: a representation of the keywords or the tags. On the right side
the document text and title (including a direct link to the article) are displayed when
selecting only one article. If several documents are selected, user-created
tags are shown with an option to filter the tags and create a new tag.

![Screenshot of the web application](images/screenshot.png "Screenshot of the web application")

This project is divided into three parts: the [preprocessing](#Preprocessing), the 
[backend](#Backend) and the [frontend](#Frontend). 

In preprocessing, the corpus of documents is loaded, clustered according to their
content, and a fixed number of keywords is extracted for each document. This information
is then written to an elasticsearch database.

The backend provides an interface to the database, which is used by the frontend
to present the data visually to the user. The user can interactively view the data,
create tags and assign them to a set of documents.


## Preprocessing
The goal of preprocessing is to load the documents, cluster them and extract a
given number of keywords for each document.

The first step is to load the documents, which can be done either by loading the
prebuilt Wikipedia dataset from Hugging Face or by parsing from a JSON file specified
by the user, which should provide the same features as the Wikipedia dataset:
 - title
 - text 
 - url
 - id

These features are then extended during preprocessing by a topic dictionary, which
indicates for each document the probability with which it belongs to which topic
and the x and y coordinates of each document for the clustering plot and a list of
keyword dictionaries.

To do this, we first use a technique called *topic modelling* to determine which
topics can be extracted from the corpus of documents. For this, we use the `BERTopic`
Python package by Maarten Grootendorst. The topic modelling process of `BERTopic`
can be divided into the following four steps:

1. **Document embedding**: First, the documents, which are represented by a string
of text, have to be transformed into a numeric vector space. For this purpose, `BERTopic`
uses so-called *Sentence Transformers*, which by default use the first 512 tokens
and generate vectors with several hundred dimensions.

2. **Dimension Reduction**: In order to cluster the documents in a senseful way,
the vectors generated in the previous step have to be transformed into a smaller,
here two-dimensional, vector space. For this purpose, `UMAP` is used because, according
to the author of `BERTopic`, this algorithm keeps some of the local and the global
structure of the vectors.

3. **Clustering**: In this step, the two-dimensional vectors of the documents are
clustered using the `HDBSCAN` algorithm. This is used for two main reasons: Firstly,
it is able to detect outliers and does not force them into a cluster where they may
not belong and secondly, it works with a density based approach which allows clusters
in different shapes.

4. **Topic Representation**: Each cluster is considered a topic. To show the user
what a given topic is about, a label is generated for each topic. To do this, all
documents in a cluster are first concatenated and converted into a vector of variable
length using the *bag of words* approach. With the *bag of words* approach, the nth
component of the resulting vector indicates how often the nth word occurs in the
document. Once such a vector has been generated for each topic, the c-TF-IDF formula
is used to determine which words of a topic best describe it and are as unique as
possible for the respective topic. This means that these words occur as often as
possible in the given topic and as rarely as possible in all others.

For more details of `BERTopic` read the documentation [https://maartengr.github.io/BERTopic/algorithm/algorithm.html](https://maartengr.github.io/BERTopic/algorithm/algorithm.html)

After topic modelling, a given number of keywords is determined for each document
using the python package `keyBERT`. In doing so, `keyBERT` tries to find possible
words that have the highest similarity with the document according to cosine similarity.
For this purpose, the cosine of the angle between the vector of the respective word
and the vector of the corresponding document is calculated. The higher this value,
the better the word represents the corresponding document.


## Backend
The backend should manage, persist and read data. It is the interface to the database for the frontend.

As Elasticsearch is used for the Database, the [low-level python client for ES](https://elasticsearch-py.readthedocs.io/en/v8.6.2/) is used in code to write queries.
 Databasemodel:

| ID    | url | Titel | Topics | Keywords | TAG_IDS |
| :---: | :-- | :---- | :----- | :------- | :--- |
| Identifier | URL of the article | Title of the article| Topics generated by the Topic Modeling algorithm | Most common words specific to the article (without: this, it, and, etc.)| TAG_IDS of tags applied by the user |

| TAG_ID | Name | Description |
| :----: | :--- | :---------- |
| Identifier | Name of the tag (e.g. climate) | An optional description of the tag|




## Frontend
### Languages and Tools
**Python**
  - [bokeh](https://docs.bokeh.org/en/latest/) as visualisation tool
  - [pandas](https://pandas.pydata.org/docs/) to manipulate the data we fill into bokeh

**HTML**
  - HTML for the general layout of the webapp

### Bokeh for Visualisation
  Bokeh is a python libary that renders its graphics by using JavaScrip and HTML. This is a contrast to Mathplotlib and Seaborn, which are often used to visualize code written in python. A big advantage of bokeh is it's possibility to include interactions, which makes it a great tool for exploring and understanding data.
  By using JavaScript and HTML for the rendering of the visualization and webpage and python for datamanipulation, bokeh lets one profit from the best of both languages.
  Bokeh also offers another great feature: The bokeh server makes it possible to also write callbacks in python and to show the plots directly in a webapp.

  - Visualization
    - Cluster:
      - cluster visualizes the topics in a two dimensional graph
      - each cluster has a topic consisting of three "identifying words"
         

    - Text and Tags
      - selecting only one article: information about the single article including an URL to the wikipedia page
    	- selection of multiple articles: shows the add tags menu
      - without selection: text that explains function
      - Tags:
        - used to manually classify the documents
        - via checkboxes tags can be added to the documents
        - the tags menu consists of a list of existing tags and a button to add new tags
        - existing tags can be filtered via the filter bar

    - Barcharts:
      - two barcharts with one being visible at a time
      - the visible barchart can be switched via the button above
      - keyword barchart:
        - without selection: shows the most common keywords (y-axis) sorted by amount
        - on selection: additionally shows the keywords of the selection in relation to the absolute amount
        - sorted by keyword count in the selection as first factor and then general amount
      - tags barchart:
        - same as keywords but just with tags
        - initally empty


## Getting started
### Preprocessing
First you need to build the docker image for the preprocessing:
```
# docker build -t idt-preprocessing /path/to/repo/source/preprocessing
```
Replace the `/path/to/repo` with a path to your local version of this repository.
The build process of this image may take multiple minutes. In the meantime, you can
customize the docker-compose-preprocessing.yml located in the application directory
of this repository. Change the command line parameters in line 23 after `idt-preprocessing.py` 
to fit your needs. Usage:
```
itd-preprocessing.py [-h] (-w SUBSET | -j JSON FILE | -p MANIFEST.JSON) [-n n] [-t t]
      [-k k] [--stop-words STOP_WORDS] [--min MIN] [--max MAX] [-l LANGUAGE] [-L]

options:
  -h, --help            show this help message and exit
  -w SUBSET, --wikipedia SUBSET
                        The subset of the Wikipedia dataset 
                        (https://huggingface.co/datasets/wikipedia)
  -j JSON FILE, --json JSON FILE
                        A file path from the import directory to a json from which
                        the Data should be parsed
  -p MANIFEST.JSON, --paperless MANIFEST.JSON
                        A file path relative to the import directory to a manifest.json
                        created by a paperless export. See (https://docs.paperless-ngx.com)
  -n n, --number-data-points n
                        Select only the first n datapoints of the dataset. Set to
                        0 to use all (Default)
  -t t, --topics t      If there BERTopic genereates more than t Topics let BERTopic
                        iteratively merger the to most similar topics until there
                        are only t Topics left.Set to 0 for a dynamic ammount (Default)
  -k k, --keywords k    Specifies that k keywords are to be created per document.
                        Default: 5
  --stop-words STOP_WORDS
                        File path, relative to the import directory, to a space
                        seperated list of stop words or the string 'english' for
                        a pre defined list of english stop words which should be
                        removed before the keywords are extracted or the topic 
                        representation is created. Default: None (don\'t remove stop
                        words)
  --min MIN             The minimal number of words per keywords for the keyword
                        extraction. Default: 1
  --max MAX             The maximal number of words per keywords for the keyword
                        extraction. Default: 1
  -l LANGUAGE, --language LANGUAGE
                        The language of the documents. E.g. 'english', 'german',
                        'multilingual'. Default: 'english'
  -L, --lemmatization   Should lemmatization be applied before the creation of the
                        topic representation. Default: False
```
Once the docker image is built, and you have customized the command for the preprocessing
in the `docker-compose-preprocessing.yml`, create an import, export and database directory
inside the application directory and run the following command to start preprocessing.
```
# docker compose -f <path/to/repository>/application/docker-compose-preprocessing.yml up
```
Preprocessing, depending on the amount of data to be processed, can take anywhere
from a few minutes to several days. After the preprocessing is finished successfully
indicated by the line
```
preprocessing exited with code 0
```
you can remove the docker container with
```
# docker compose -f <path/to/repository>/application/docker-compose-preprocessing.yml down 
```

### Web Application
As with preprocessing, the docker image must first be built:
```
# docker build -t idt-app /path/to/repo/source/web-app 
```
While building the docker image you can modify the `docker-compose.yml` located
in the `application` directory. All you need to do here is to change the path before
the colon in line 14 to the absolute path to the `application/database` directory.

Once the docker image is built and you have finished customizing the `docker-compose.yml`,
be sure that the docker container from the preprocessing is not running. You can check
that by running
```
# docker ps
```
If the database was successfully filled with data using the Docker container of
the preprocessing and the container of the preprocessing is no longer running, you
can start the Docker container for the frontend with the following command:
```
# docker compose -f <path/to/repository>/application/docker-compose.yml up -d
```
The database container needs approximately 10 seconds to start, after that, the web
application should be accessible via [http://localhost](http://localhost).