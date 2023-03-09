FROM python:3.10-slim-bullseye

ARG USERNAME=itd
ARG UID=1000
ARG GID=1000
RUN groupadd -g $GID -o $USERNAME
RUN useradd -m -u $UID -g $GID -o $USERNAME

WORKDIR /app

RUN bash -c "apt update && apt install -y gcc 2>&1 1> /dev/null"

COPY requirements.txt /tmp/
RUN pip install --no-warn-script-location --no-cache-dir -qqq -r/tmp/requirements.txt

COPY backend/backend.py ./
COPY frontend/main.py ./
COPY frontend/bar_chart_widget.py ./
COPY frontend/cluster_widget.py ./
COPY frontend/document_view_widget.py ./
COPY frontend/tags_widget.py ./
COPY frontend/templates ./templates
COPY frontend/static ./static
RUN chown -R $USERNAME:$USERNAME /app

USER $USERNAME


RUN sed -i -e "s|localhost:9200|elasticsearch:9200|g" backend.py
RUN sed -i -e "s|document_tagger|app|g" templates/index.html

CMD ["python", "-m", "bokeh", "serve", "--port", "80", "--show", "/app"]
