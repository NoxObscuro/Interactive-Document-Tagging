#!/usr/bin/env python3
import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.models import HoverTool, ColumnDataSource
from bokeh.transform import factor_cmap



class ClusterWidget:
    """
    A class to create the Scatterplot to desplay the clustering of the documents
    """

    def __init__(self, document_client:'DocumentClient', document_view_widget:'DocumentViewWidget', tags_widget:'TagsWidget', bar_chart_widget:'BarChartWidget', cluster_widget_name:str, color_map:tuple):
        """
        @param DocumentClient document_client
        @param DocumentViewWidget document_view_widget
        @param TagsWidget tags_widget
        @param BarChartWidget bar_chart_widget
        @param str cluster_widget_name: The name of the cluster, for the HTML file
        @param tuple color_map: a tuple of strings which defines colors in hex
        """
        self.document_client = document_client
        self.document_view_widget = document_view_widget
        self.bar_chart_widget = bar_chart_widget
        self.tags_widget = tags_widget
        
        self.tags_widget.visible = False
        self.cluster_widget_name = cluster_widget_name
        self.data = self.getPoints()
        self.alltags = self.document_client.get_all_tags()
        
        self.cluster_plot = self.scatterplot(color_map)

    
    def getPoints(self)->pd.DataFrame:
        """
        Gets the information needed for the cluster and returns it in the needed formation
        @return pd.DataFrame
        """
        df = pd.DataFrame(self.document_client.get_all_articles())
        df2 = pd.DataFrame(list(df["topic"]))
        df3 = pd.concat([df[['id', 'heading']], df2], axis=1, join='inner')
        return df3
        
    
    def scatterplot(self, color_map:tuple):
        """
        Creates the sactter plot to visualize the clustering
        @param tuple color_map: the color map which should be used
        """
        TOPICS = sorted(self.data.topic_name.unique()) 
        if "None" in TOPICS:
            TOPICS.remove('None')

        TOPICS = ['None'] + TOPICS
        self.source = ColumnDataSource(self.data)

        hover = HoverTool(tooltips=[
            ("Titel", "@heading"),
            ("Cluster", "@topic_name"),
            ("Propability","@probability{0:.0%}")
        ])

        fig = figure(name=self.cluster_widget_name, sizing_mode="stretch_both", title=None,
                tools=["pan", "tap", "box_select", "lasso_select", "wheel_zoom", "box_zoom", "zoom_in", "zoom_out", "reset", hover],
                toolbar_location='above', active_scroll="wheel_zoom",
                active_drag="box_select", active_tap="tap", background_fill_color="#ffffff")

        fig.scatter("x", "y", source=self.source,
            color=factor_cmap('topic_name', color_map, TOPICS))

        fig.toolbar.logo = None
        fig.xaxis.visible = False
        fig.yaxis.visible = False
        fig.xgrid.visible = False
        fig.ygrid.visible = False


        def scatter_callback(attr, old, new):
            """
            Scatter Plot callback if selection of Documents changes
            """
            ids = self.data['id'][self.source.selected.indices].to_list()
            # list of keywords of selected documents
            keywords = self.document_client.get_keywords_by_ids(ids)
            # list of tags of selected documents
            tags = self.document_client.get_tags_by_ids(ids,filter=False)
            
            # Document selection reseted
            if (len(self.source.selected.indices) == 0):
                # Reset the displayed Document text and title
                self.document_view_widget.reset_article_text()
                self.document_view_widget.set_visible(True)
                self.tags_widget.set_visible(False)
                self.bar_chart_widget.update_bar_charts(keywords, tags)

            else:
                # Single Document selected
                if (len(self.source.selected.indices) == 1):
                    index = self.source.selected.indices[0]
                    id = self.data['id'][index]
                    url = self.document_client.get_url_from_id([id])[0]
                    text = self.document_client.get_article_text(id)
                    title = self.data['heading'][index]
                    self.document_view_widget.update_article_text(text, title, url)
                    self.document_view_widget.set_visible(True)
                    self.tags_widget.set_visible(False)
                    self.bar_chart_widget.update_bar_charts(keywords, tags)

                # Multiple Documents selected
                else:
                    self.tags_widget.ids = ids
                    self.tags_widget.update_tags_in_checkbox()
                    self.document_view_widget.set_visible(False)
                    self.tags_widget.set_visible(True)
                    self.bar_chart_widget.update_bar_charts(keywords, tags)

        self.source.selected.on_change('indices', scatter_callback)
        return fig


    def give_to_curdoc(self):
        curdoc().add_root(self.cluster_plot)