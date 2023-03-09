# Interactive Document Tagging 
This project was created as part of the project "Anwendungen der künstlichen Intelligenz"
in the winter semester 2022/2023 at the University of Hamburg. Authors of this project
are Alan Kniep, Julia Janßen, Maja Lingl, Valerie Bartel and Vanessa Maeder.

## Use case and functionality
The goal of our project is to cluster large quantities of documents or articles
according to their content, and to visualize these clusters to get a fast overview
of a document collection. Additionally, the application should enable the user to
tag documents in an interactive way. 

For the visualization, we represented the clustered articles in a scatter plot in
the center of our web application. On the left side, the user can toggle between
two bar charts: a representation of the keywords or the tags. On the right side,
the document text and title (including a direct link to the article) are displayed,
if only one article is selected. If several documents are selected, user-created
tags are shown, with an option to filter the tags and create a new tag.

![Screenshot of the web application](images/screenshot.png "Screenshot of the web application")

This project is divided into three parts: the [preprocessing](#Preprocessing), the 
[backend](#Backend) and the [frontend](#Frontend). 

In preprocessing, the corpus of documents is loaded, clustered according to their
content, and a fixed number of keywords is extracted for each document. This information
is then written to an elasticsearch database.

The backend provides an interface to the database, which is used by the frontend
to present the data visually to the user. The user can interactively view the data,
create tags and assign them to a set of documents.

## Getting started
### Preprocessing
First you need to build the docker image for the preprocessing:
```
# docker build -t idt-preprocessing /path/to/repo/source/preprocessing
```
Replace the `/path/to/repo` with a path to your local version of this repository.
The build process of this image may take multiple minutes. In the meantime, you can
customize the docker-compose-preprocessing.yml located in the application directory
of this repository. You need to change the path before the colon in line 15, 22 and
23 to an absolute path to the `application/database`, `application/import` and the
`application/export` directory of this repository.
You can also change the command line parameters in line 20 after `idt-preprocessing.py` 
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
Once the docker image is built, and you have finished customizing the `docker-compose-preprocessing.yml`,
run the following command to start preprocessing.
```
# docker compose -f <path/to/repository>/application/docker-compose-preprocessing.yml up
```
Preprocessing, depending on the amount of data to be processed, can take anywhere
from a few minutes to several days. After the preprocessing is finished successfully
indicated by the line:
```
preprocessing exited with code 0
```
You can remove the docker container with.
```
# docker compose -f <path/to/repository>/application/docker-compose-preprocessing.yml down 
```

### Web Application
As with preprocessing, the docker image must first be built:
```
# docker build -t idt-app /path/to/repo/source/frontend 
```
While building the docker image you can modify the `docker-compose.yml` located
in the `application` directory. All you need to do here is to change the path before
the colon in line 14 to the absolute path to the `application/database` directory.

Once the docker image is built, and you have finished customizing the `docker-compose.yml`
be sure that the docker container from the preprocessing isn't running. You can check
that by running:
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

## Preprocessing
The goal of preprocessing is to cluster a data set of documents or articles based
on their content. Each cluster then corresponds to a topic, which is described with
a set of keywords. 


  
 - Document loading (Dataset: Wikipedia)
 - Dataset preparation
    - filter most common words
    - Stopword filtering
 - Keyword extraction via KeyBert
 - Topic modeling (BERTopic)
    - Document embeding via Sentence transformer
    - Dimension reduction via umap (keeps lcoal and global structure quiet well)
    - Clustering via HDBScan (density-based approach)
    - Create Topic representation
      - Merge all Documents of a Cluster to a single document
      - Create a Bag-Of-Words from this document
      - Use c-TF-IDF to identefy the words that are important to the specific Cluster/Topic

## Backend
 - Elasticsearch

| ID    | url | Titel | Topics | Keywords | TAGS |
| :---: | :-- | :---- | :----- | :------- | :--- |
| Identifier | The URL of the article | Title of the article| Topics generated by the Topic Modeling algorithm | Most common words, specific to the article (without: this, it, and, etc.| TAGS applied by the user) |

| TAG_ID | Name | Description |
| :----: | :--- | :---------- |
| Identifier | Name of the Tags (for example. Climate) | Optional a description of the TAG|

- SQL

| ID    | url | Titel | Topics | Keywords |
| :---: | :-- | :---- | :----- | :------- |
| Identifier | The URL of the article | Title of the article | Topics generated by the Topic Modeling algorithm | Most common words, specific for the article (without: this, it, and, ...) |

| TAG_ID | Name | Discription |
| :----: | :--- | :---------- |
| Identifier | Name of the TAG (for example Climate) | Optional a description of the TAG |


 - Interface for the Frontend
 - Manages the Database access

## Frontend
### Languages and Tools
**Python**
  - [bokeh](https://docs.bokeh.org/en/latest/) as visualisation tool
  - [pandas](https://pandas.pydata.org/docs/) to manipulate the data we fill into bokeh

**HTML**
  - HTML for the general layout of the webapp

### bokeh for Visualisation
  Bokeh is a python libary that renders it graphics by using JavaScrip and HTML. This is a contrast to Mathplotlib and Seaborn, which are often used to visualize python written code. A big advantage of bokeh is its possibility to include interactions, which makes it to a great tool for exploring and understanding data.
  By only using JavaScript and HTML for the rendering of the visualization, bokeh also profits from the huge amount of python packages for datamanipulations, which makes python to a great tool to extract information from data. So bokeh gave us the the possibility to combine the best from both coding languages.
  Bokeh also offers another great ... .The bokeh Server makes it possible to also wirte callbacks in python and to show the plots directly in a webapp.
  - Visualization
    - Cluster:
      - cluster visualises the topic modelling in a two dimensional graph
      - each cluster has a topic consisting of three "identifying words"
      - funktionen des clusters:
         

    - Text and Tags
      - on click: Information about a single article
    	- Selection of multiple articles: shows tags menu
      - Article:
        - without selection: filler text that explains function
        - on selection: shows the selected articles title, contents and links to its wikipedia page 
      - Tags:
        - are used to manually classify the documents
        - the tags menu consists of: list of existing tags and button to add tags
        - existing tags:
          - can be filtered via the filter bar
          - on click: tag is added to all selected documents

    - Barcharts:
      - there are two barcharts with exactly one being visible at a time
      - the visible barchart can be switched via the button above
      - keyword barchart:
        - without selection: shows the hunderd most common keywords (y-axis) sorted by amount
        - on selection: additionally shows the keywords of the selection
        - sorted by the keyword counts in the selection as a first factor and the general amount second
      - tags barchart:
        - shows the 
