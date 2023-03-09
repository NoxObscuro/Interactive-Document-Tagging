#!/usr/bin/env python3

import pandas as pd

from bar_chart_widget import BarChartWidget
from tags_widget import TagsWidget
from document_view_widget import DocumentViewWidget
from cluster_widget import ClusterWidget

from backend import DocumentClient


COLOR_MAP = ("#c0c0c0", "#f44336", "#E91E63",  "#9C27B0", "#673AB7", "#3F51B5",
             "#2196F3", "#00BCD4", "#009688", "#4CAF50", "#8BC34A", "#CDDC39",
             "#FFEB3B", "#FFC107", "#FF9800", "#FF5722", "#b71c1c", "#880E4F",
             "#4A148C", "#311B92", "#1A237E", "#0D47A1", "#006064", "#004D40",
             "#1B5E20", "#33691E", "#827717", "#F57F17",  "#FF6F00", "#E65100",
             "#BF360C", "#ef9a9a", "#F48FB1", "#CE93D8", "#B39DDB", "#9FA8DA",
             "#90CAF9", "#80DEEA", "#80CBC4", "#A5D6A7", "#C5E1A5", "#E6EE9C",
             "#FFF59D", "#FFE082", "#FFCC80", "#FFAB91")

document_client = DocumentClient()

tags = pd.Series(document_client.get_all_tags(), dtype='object').value_counts() - 1
tag_count = pd.Series(document_client.get_all_tags(filter=False), dtype='object').value_counts()
tag_count = tag_count.add(tags, fill_value=0)
keywords = document_client.get_all_keywords()
keyword_count = pd.Series(keywords).value_counts()

bar_chart_widget = BarChartWidget(
    kw_bar_chart_name="keywords_bar_chart",
    tag_bar_chart_name="tag_bar_chart",
    button_name="bar_chart_toggle",
    tags=tag_count,
    keywords=keyword_count
)

tags_widget = TagsWidget(
    document_client=document_client,
    bar_chart_widget=bar_chart_widget,
    tags_name="tags_menu"
)

document_view_widget = DocumentViewWidget(
    document_client=document_client,
    document_view_name="document_view"
)
cluster_widget = ClusterWidget(
    document_client=document_client,
    document_view_widget=document_view_widget,
    tags_widget=tags_widget,
    bar_chart_widget=bar_chart_widget,
    cluster_widget_name="cluster_plot",
    color_map=COLOR_MAP
)

bar_chart_widget.give_to_curdoc()
cluster_widget.give_to_curdoc()
document_view_widget.give_to_curdoc()
tags_widget.give_to_curdoc()
