FROM python:3.10-slim-bullseye

ARG USERNAME=itd
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID -o $USERNAME
RUN useradd -m -u $UID -g $GID -o $USERNAME

WORKDIR /data
RUN mkdir /data/import
RUN mkdir /data/export

RUN bash -c "apt update && apt install -y gcc 2>&1 1> /dev/null"

COPY requirements.txt /tmp/
RUN bash -c "pip install -qqq --upgrade pip 2> /dev/null"
RUN bash -c "pip install -qqq --no-dependencies apache_beam==2.45.0 2> /dev/null"
RUN bash -c "pip install -qqq --no-cache-dir -r /tmp/requirements.txt 2> /dev/null"
RUN bash -c "pip install -qqq --upgrade dill==0.3.6 2> /dev/null"
RUN bash -c "pip install -qqq --upgrade multiprocess==0.70.14 2> /dev/null"

COPY ./main.py ./main.py
COPY ./key_word_extraction.py ./key_word_extraction.py
COPY ./topic_modeling.py ./topic_modeling.py
COPY ./create_dataset.py ./create_dataset.py
COPY ./create_database.py ./create_database.py

RUN chown -R $USERNAME:$USERNAME /data

USER $USERNAME

RUN sed -i -e "s|localhost:9200|elasticsearch:9200|g" create_database.py
RUN sed -i -e 's|load_from_disk("article_data")|load_from_disk("/data/export/article_data")|g' create_database.py
