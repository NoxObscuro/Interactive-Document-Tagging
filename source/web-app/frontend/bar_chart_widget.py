#!/usr/bin/env python3
import pandas as pd
from bokeh.plotting import figure, curdoc
from bokeh.models import Button, HoverTool, ColumnDataSource, FactorRange
from bokeh.events import ButtonClick


class BarChartWidget:
    """
    A class for making two bar charts (one for keywords, one for tags), 
    together with a Button to switch between the visibility of the bar charts.
    This class also provides functions to update the bar charts.
    """

    def __init__(self, kw_bar_chart_name: str, tag_bar_chart_name: str, button_name: str, tags: pd.Series, keywords: pd.Series):
        """
        @param str kw_bar_chart_name: The name of the figure, used in the HTML file
        @param str tag_bar_chart_name: The name of the figure, used in the HTML file
        @param str button_name: The name of the button, used in the HTML file
        @param pd.Series tags: number of documents for each tag
        @param pd.Series keywords: number of documents for each keyword
        """
        self.tag_data = self.create_data(tags)
        self.kw_data = self.create_data(keywords)

        self.tag_plot, self.tag_datasource, self.tag_y_range = self.create_bar_chart(
            self.tag_data, "Tags", tag_bar_chart_name)
        self.kw_plot, self.kw_datasource, self.kw_y_range = self.create_bar_chart(
            self.kw_data, "Keywords", kw_bar_chart_name)
        self.button = self.create_button(button_name)
        self.kw_plot.visible = False

    def create_button(self, button_name: str) -> Button:
        """
        Creates a Button which allows the user to toggle between the Tag Bar Chart
        and the Keywords Bar Chart
        @param str button_name: name for the button to be able to add the button in the html file
        @return Button
        """
        button = Button(label="Show Keywords",
                        button_type="success", name=button_name)

        def switch_tags_keywords_table_callback(event):
            if self.kw_plot.visible:
                self.kw_plot.visible = False
                self.tag_plot.visible = True
                self.button.label = "Show Keywords"
            else:
                self.tag_plot.visible = False
                self.kw_plot.visible = True
                self.button.label = "Show Tags"

        button.on_event(ButtonClick, switch_tags_keywords_table_callback)

        return button

    def create_data(self, number_per_word: pd.Series) -> pd.DataFrame:
        """
        Creates a panda Series object with the number of occurrences of words in
        words, a list of unique words and a pandas DataFrame with the unique keywords
        the number of occurrences per word and the number of selected documents mapped
        by word.

        @param pd.Series number_per_word: number of documents for each tag/keyword
        @return pd.DataFrame
        """

        # List of unique words from supplied pd.Series
        words_list = number_per_word.index.to_list()

        data_words = {
            "words": words_list,
            "selected_occ": [0] * len(words_list),  # List of 0
            "unselected_occ": number_per_word.to_list()  # List of counts per unique words
        }

        data = pd.DataFrame(data_words)
        data.set_index("words", inplace=True)
        data.sort_values(["selected_occ", "unselected_occ"], inplace=True)
        return data

    def create_bar_chart(self, data: pd.DataFrame, title: str, name: str) -> tuple[figure, ColumnDataSource, FactorRange]:
        """
        Creates a horizontal bar chart with possibly stacked bars.
        @param pd.DataFrame data: the data to be plotted
        @param str title: the title of the Plot
        @return figure
        @return ColumnDataSource
        @return FactorRange
        """
        stack_label = ["selected_occ", "unselected_occ"]
        color = ("#b2182b", "#2166ac")
        data_subset = data.tail(100)
        datasource = ColumnDataSource(data_subset)
        y_range = FactorRange(factors=data_subset.index, range_padding=0)
        hover = HoverTool(tooltips=[
                          (f"Unselected {title}", "@unselected_occ"), (f"Selected {title}", "@selected_occ")])

        p = figure(
            name=name,
            height=30*len(data_subset)+60,
            y_range=y_range,
            toolbar_location=None,
            title=title,
            sizing_mode="stretch_width",
            tools=[hover]
        )
        p.hbar_stack(
            stack_label,
            y="words",
            source=datasource,
            color=color,
            height=0.5
        )

        p.x_range.start = 0
        p.ygrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None

        return p, datasource, y_range

    def update_bar_chart(self, data: pd.DataFrame, datasource: ColumnDataSource, y_range: FactorRange):
        """
        Updates the given barc hart with the given Data
        @param DataFrame data: The Data which should be displayed in the bar chart
        @param ColumnDataSource: The datasource of the bar chart to be updated
        @param FactorRange y_range: The y_range of the bar chart to be updated
        """
        data_subset = data.tail(100)
        y_range.factors = list(data_subset.index)

        datasource.data = dict(ColumnDataSource(data_subset).data)

    def update_bar_charts(self, selected_kw, selected_tags):
        """
        Update the DataFrames with the provides selected_kw and the selected_tags
        list.
        @param list selected_kw: list of keywords-strings of selected documents
        @param list selected_tags: list of tag-strings of selected tags
        """
        self.update_data(self.kw_data, selected_kw)
        self.update_data(self.tag_data, selected_tags)
        self.update_bar_chart(
            self.kw_data, self.kw_datasource, self.kw_y_range)
        self.update_bar_chart(
            self.tag_data, self.tag_datasource, self.tag_y_range)

    def update_data(self, data: pd.DataFrame, selected_words: list):
        """
        Updates the data DataFrame for the given list of selected_word
        @param DataFrame data: The DataFrame to be updated
        @param list selected_words: List of words of selected documents
        """
        selected_words_count = pd.Series(
            selected_words, dtype='object').value_counts()
        data["unselected_occ"] = data.sum(axis=1)
        data["selected_occ"] = selected_words_count
        data.fillna(0, inplace=True)
        data["unselected_occ"] = data["unselected_occ"] - data["selected_occ"]

        data.sort_values(["selected_occ", "unselected_occ"], inplace=True)

    def add_tag(self, name: str, number: int):
        """
        Add a row to tag_data with name as index and number a row
        @param str name: Name of the tag
        @param int number: Number of documents that are getting this tag
        """
        df = pd.DataFrame([[number, 0]], columns=[
                          'selected_occ', 'unselected_occ'], index=[name])
        self.tag_data = pd.concat([self.tag_data, df])
        self.tag_data.index.names = ["words"]
        self.update_bar_chart(
            self.tag_data, self.tag_datasource, self.tag_y_range)
        self.tag_plot.update(height=30*len(self.tag_data.tail(100))+60)

    def update_tag_count(self, name: str, number: int):
        """
        Update the row with index name 
        @param str name: Name of the tag, whose number of selected documents is changing
        @param int number: number of documents selected for this tag
        """
        self.tag_data.at[name, 'selected_occ'] = number
        self.update_bar_chart(
            self.tag_data, self.tag_datasource, self.tag_y_range)

    def remove_tag(self, name: str):
        """
        Remove a row with name as index fron tag_data
        @param str name: Nmae of the tag to remove
        """
        self.tag_data.drop(name, axis="index", inplace=True)
        self.update_bar_chart(
            self.tag_data, self.tag_datasource, self.tag_y_range)
        self.tag_plot.update(height=30*len(self.tag_data.tail(100))+60)

    def give_to_curdoc(self):
        """
        Give created widgets to curdoc, to be displayed in the browser.
        """
        curdoc().add_root(self.tag_plot)
        curdoc().add_root(self.kw_plot)
        curdoc().add_root(self.button)
