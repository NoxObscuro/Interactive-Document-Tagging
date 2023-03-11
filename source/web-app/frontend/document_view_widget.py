#!/usr/bin/env python3
from bokeh.plotting import curdoc
from bokeh.models.widgets import Div
from bokeh.layouts import column


class DocumentViewWidget():
    """
    A class that creates textboxes with the documents texts and title.
    The goal is to visualize a single selected document to see its content.
    """

    def __init__(self, document_client: 'DocumentClient', document_view_name: str):
        """
        @param DocumentumentClient document_client
        @param str document_view_name: The name of the teaxtarea, for the HTML file
        """
        self.help_message = "Select a single article in the Cluster Plot to display the title and text of the article.<br><br>Select multiple Articles to add or remove Tags to them."
        self.help_title = "Nothing Selected"
        self.document_client = document_client
        self.document_view_name = document_view_name
        self.article_text = self.create_article_text()


    def create_article_text(self) -> column:
        """
        Create to divs to display title and content of the selected article or 
        a help message if none is selected.
        @return column
        """
        self.article_text_headline = Div(text=self.help_title,
                                         styles={'font-size': '200%', 'margin-bottom': '20px', 'margin-top': '20px', 'width': '100%'})
        self.article_text_body = Div(text=self.help_message, height_policy="fit",
                                     styles={'overflow-y': 'scroll', 'width': '100%', 'padding': '10px'})

        return column(name=self.document_view_name, children=[self.article_text_headline, self.article_text_body])


    def update_article_text(self, text: str, title: str, url: str):
        """
        Update the text and title to show, text and heading of the selected article.
        @param str text: the body of the document
        @param str title: the headline of the document
        @param str url: the link to the document
        """
        if url is None or url == "":
            self.article_text_headline.update(text=title)
        else:
            self.article_text_headline.update(text=f'<a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a>')
        self.article_text_body.update(text=text)


    def reset_article_text(self):
        """
        Reset the displayed Text to a help message.
        """
        self.article_text_headline.update(text=self.help_title)
        self.article_text_body.update(text=self.help_message)


    def set_visible(self, visibility: bool):
        """
        Sets the visibility of the document view widget
        @param bool visibility
        """
        self.article_text.visible = visibility


    def give_to_curdoc(self):
        """
        Give the doument view widget to curdoc to be displayed in the browser.
        """
        curdoc().add_root(self.article_text)
