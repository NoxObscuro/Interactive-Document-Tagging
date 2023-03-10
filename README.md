# Interactive Document Tagging 
This project was created as part of the project "Anwendungen der künstlichen Intelligenz"
in the winter semester 2022/2023 at the University of Hamburg. Authors of this project
are Alan Kniep, Julia Janßen, Maja Lingl, Valerie Bartel and Vanessa Maeder.

![Demo](images/demo.gif "Demo")

## Outline
1. [Use case and functionality](#use-case-and-functionality)
2. [Preprocessing](#preprocessing)
3. [Backend](#backend)
4. [Frontend](#frontend)
   * [Languages and Tools](#languages-and-tools)
   * [Bokeh for Visualisation](#bokeh-for-visualisation)
5. [Getting started](#getting-started)


## Use case and functionality
The goal of our project is to cluster large quantities of documents or articles
according to their content, and to visualize these clusters to get a fast overview
of a document collection. Additionally, the application should enable the user to
tag documents in an interactive way. 

For the visualization, we represent the clustered articles in a scatter plot in
the center of our web application. On the left side, the user can toggle between
two bar charts: one which visualizes the keywords of the documents and one which
visualizes the user applied tags. On the right side the document text and title
(including a direct link to the article) are displayed when selecting only one article.
If several documents are selected, user-created tags are shown with an option to
filter the tags, create new ones, apply tags to the selection or remove them.

![Mockup of application](images/mockup.jpg "Mockup of the application")

This project is divided into three parts: the [preprocessing](#Preprocessing), the 
[backend](#Backend) and the [frontend](#Frontend). 

In preprocessing, the corpus of documents is loaded, clustered according to their
contents, and a fixed number of keywords is extracted for each document. This information
is then written to an elasticsearch database.

The backend provides an interface to the database, which is used by the frontend
to visually present the data to the user. The user can view the data interactively,
create tags and assign them to a set of documents.


## Preprocessing
The goal of preprocessing is to load the documents, cluster them and extract a
given number of keywords for each document.

The first step is to load the documents, which can be done either by loading the
prebuilt [Wikipedia dataset](https://huggingface.co/datasets/wikipedia) from Hugging
Face or by parsing from a JSON file specified by the user, which should provide the
same features as the Wikipedia dataset:
 - title
 - text 
 - url
 - id

These features are then extended during preprocessing by a list of keywords and
information over the assigned topic, including the probability with which the document
belongs to which topic and the x and y coordinates for the clustering plot.

To do this, we first use a technique called *topic modelling* to determine which
topics can be extracted from the given corpus of documents. For this, we use the
`BERTopic` Python package by Maarten Grootendorst. The topic modelling process of
`BERTopic` can be divided into the following four steps:

1. **Document embedding**: First, the documents, which are represented by a string
of text, have to be transformed into a numeric vector space. For this purpose, `BERTopic`
uses so-called *Sentence Transformers*, which by default use the first 512 tokens
and generate vectors with several hundred dimensions.

2. **Dimension Reduction**: In order to cluster the documents in a meaningful way,
the vectors generated in the previous step have to be transformed into a smaller,
here two-dimensional, vector space. For this purpose, `UMAP` (**U**niform **M**anifold
**A**pproximation and **P**rojection) is used because, according to the author of
`BERTopic`, this algorithm keeps some of the local and the global structure of the
vectors which influences directly the quality of the Clustering.

3. **Clustering**: In this step, the two-dimensional vectors of the documents are
clustered using `HDBSCAN` (**H**ierarchical **D**ensity-**B**ased **S**patial **C**lustering
of **A**pplications with **N**oise). This is used for two main reasons: Firstly,
it is able to detect outliers and does not force them into a cluster where they may
not belong and secondly, it works with a density based approach which allows clusters
with different shapes.

4. **Topic Representation**: Each cluster is considered a topic. To show the user
what a given topic is about, a label is generated for each topic. To do this, all
documents in a cluster are first concatenated and converted into a vector of variable
length using the *bag of words* approach. With the *bag of words* approach, the nth
component of the resulting vector indicates how often the nth word occurs in the
document. Once such a vector has been generated for each topic, the `c-TF-IDF` formula
is used to determine which words of a topic best describes it and are as unique as
possible for the respective topic. This means that these words occur as often as
possible in the given topic and as rarely as possible in all others.

![Topic Modeling Pipeline](images/topic_modeling.png "Topic Modeling Pipeline")

For more details of `BERTopic` read the documentation [https://maartengr.github.io/BERTopic/algorithm/algorithm.html](https://maartengr.github.io/BERTopic/algorithm/algorithm.html)

After topic modelling, a given number of keywords is determined for each document
using the python package `keyBERT`. In doing so, `keyBERT` tries to find possible
words that have the highest similarity with the document according to cosine similarity.
For this purpose, the cosine of the angle between the vector of the respective word
and the vector of the corresponding document is calculated. The higher this value,
the better the word represents the corresponding document.

For more information on `keyBERT` check  [https://maartengr.github.io/KeyBERT/](https://maartengr.github.io/KeyBERT/)



## Backend
The backend should manage, persist and read data. It is the interface to the database
for the frontend.

As Elasticsearch is used for the Database, the [low-level python client for ES](https://elasticsearch-py.readthedocs.io/en/v8.6.2/)
is used in code to write queries.

Databasemodel:

| ID    | url | heading | topics | keywords | TAG_IDS |
| :---: | :-- | :------ | :----- | :------- | :------ |
| Identifier | URL of the article | Title of the article | Topics generated by the Topic Modeling algorithm | Most common words specific to the article | TAG_IDS of tags applied by the user |

| TAG_ID | Name | Description |
| :----: | :--- | :---------- |
| Identifier | Name of the tag (e.g. climate) | An optional description of the tag |



## Frontend
### Languages and Tools
**Python**
  - [bokeh](https://docs.bokeh.org/en/latest/) as visualisation tool
  - [pandas](https://pandas.pydata.org/docs/) to manipulate the data we fill into bokeh

**HTML and CSS**
  - HTML for the general layout of the webapp
  - CSS for the general styling 

### Bokeh for Visualisation
Bokeh is a python libary that renders its graphics by using JavaScrip and HTML. This
is in contrast to Mathplotlib and Seaborn, which are often used to visualize code
written in python. A big advantage of bokeh is its possibility to include interactions,
which makes it a great tool for exploring and understanding data. By using JavaScript
and HTML for the rendering of the visualization and webpage and python for data manipulation,
bokeh enables us to profit from the best of both languages. Bokeh also offers another
great feature: The bokeh server makes it possible to also write callbacks in python
and to show the plots directly in a webapp.

### Visualization
| ![Overview](images/screenshot-overview.png "Overview") | ![Keywords](images/screenshot-keywords.png "Keywords Bar Chart") |
| --- | --- |
| ![Tags](images/screenshot-tags.png "Tag Bar Chart") | ![Document_View](images/screenshot-document_view.png "Document View") |

- **The Cluster:** The cluster visualizes the topic modelling in a two dimensional
graph, where each cluster has a colour and topic consisting of three identifiers
and a probability, that describes the certainty with which a document is assigned
to a cluster. The topic can be seen by hovering over the document. Grey coloured
documents are outliers, that have not been assigned a topic. The cluster has a menu
with tools such as zoom and selection tools. The selection influences what is visible
on the right side of the page and what bars are shown in the bar charts to the left.

- **Tags and Text:** When more than a single article is selected, the tags menu
is shown. It gives users the option to manually assign a tag to certain documents,
as well as create new tags (while there is the option to add a tag describtion
it is not yet used). The tag list is sorted by active tags first and alphabetically
second. The existing tags can be filtered via the search bar above the menu. If
one article is selected, its title and text is shown instead of the tag menu.

- **The bar charts:** The two bar charts show keyword and tag statistics, with exactly
one being visible at a time. The keyword bar chart shows the hundred most common
keywords on the y-axis and each of its amounts on the x-axis, sorted by amount.
On selection, the bar chart changes to show the keywords of the selection, as well
as the remaining amount that is not selected. The bars are sorted by amounts in
the selection first and amounts overall second. The tag chart works accordingly.
It shows a maximum amount of one hundred tags on the y-axis and the amount of
documents that have the tag assigned on the x-axis. It changes each time a selection
is made, to show the tags in the selected documents and updates when the tags are
changed via the tag menu.


## Getting started
### Setup
Before you can use this tool you need the docker images for the web-app and the
preprocessing you also need a import, export and database directory which are
mounted by the preprocessing and web-app docker container. 

You can build the docker-images and directories by hand or use the provided `setup.sh`
script to do it for you. Use the `setup.sh` script if you don't need sudo privileges
to run `docker` (default on *macOS* and *windows*) or the `setup-sudo.sh` script
if you need sudo to run docker commands (default on *linux*), but don't run the script
with sudo or as root unless you want the import, export and database ddirectory
to be owned by the root user.

#### Manually setup
First you need to build the docker image for the preprocessing:
```
# docker build -t idt-preprocessing </path/to/repo>/source/preprocessing
```
Replace the `/path/to/repo` with a path to your local version of this repository.
The build process of this image may take multiple minutes. In the meantime you can
create the `import`, `export` and `database` directory inside the application directory
of your local Version of this repository. In theory you can create those three directories
anywhere you want and can name them as you see fit, but then you have to adjust
the path in the docker-compose.yml accordingly. 

Once the docker image is built you can start building the docker image for the
preprocessing:
```
# docker build -t idt-app </path/to/repo>/source/web-app 
```

### Preprocessing
Before you can start the web-app you need some data in your database. To achieve
this, you must first run the preprocessing. First, customize the docker-compose-preprocessing.yml
located in the application directory of this repository. Change the command line
parameters in line 23 after `idt-preprocessing.py` to fit your needs. Usage:
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
                        iteratively merges the two most similar topics until there
                        are only t Topics left.Set to 0 for a dynamic ammount (Default)
  -k k, --keywords k    Specifies that k keywords are to be created per document.
                        Default: 5
  --stop-words STOP_WORDS
                        File path, relative to the import directory, to a space
                        seperated list of stop words or the string 'english' for
                        a pre defined list of english stop words which should be
                        removed before the keywords are extracted or the topic 
                        representation is created. Default: None (don't remove stop
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
Second, after you are satisfied with the parameters, start the preprocessing with
the following command.
```
# docker compose -f <path/to/repository>/application/docker-compose-preprocessing.yml up
```
Depending on the amount of data to be processed, the preprocessing can take anywhere
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
Once the preprocessing is done and you have data in your database, be sure that the
docker container from the preprocessing is not running. You can check that by running
```
# docker ps
```
Once the preprocessing containers stop running, you can start the docker containers
for the web app with the following command.
```
# docker compose -f <path/to/repository>/application/docker-compose.yml up -d
```
The database container needs severeal seconds to start, after that, the web
application should be accessible via [http://localhost](http://localhost).
