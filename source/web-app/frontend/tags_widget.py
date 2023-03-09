#!/usr/bin/env python3
from bokeh.plotting import figure, curdoc
from bokeh.models import Button, CheckboxGroup, TextInput, TextAreaInput
from bokeh.events import ButtonClick
from bokeh.layouts import column


class TagsWidget:
    """
    A class to make the UI-elemnts, which make it possible to add or delete a tag
    from a given group of documents. The class also provide UI-elements to make.
    completly new tags.
    """

    def __init__(self, document_client: 'DocumentClient', bar_chart_widget: 'BarChartWidget', tags_name=None, ids=[]):
        """
        @param DocumentClient document_client
        @param BarChartWidget bar_chart_widget
        @param str tag_name: The name of the UI, used in the HTML file (default: None)
        @param list ids: ids of the selected documents (deafault: [])
        """
        self.document_client = document_client
        self.bar_chart_widget = bar_chart_widget
        self.tags_name = tags_name
        self.ids = ids
        self.active_label_indices = list()

        self.add_button = self.create_add_button()
        self.search_bar = self.create_search_bar()
        self.checkbox_group = self.create_checkbox_group()
        self.search_tag_group = self.create_search_tag_group()

        self.tag_name_input = self.create_tag_name_input()
        self.description_input = self.create_description_input()
        self.save_button = self.create_save_button()
        self.add_tag_group = self.create_add_tag_group()

        self.column = column(name=self.tags_name, children=[
                             self.search_tag_group, self.add_tag_group])
        self.set_visible(False)

    def create_add_button(self) -> Button:
        """
        Creates and returns a button which displays, on click, a menu for creating
        new tags.
        @return Button
        """
        button = Button(label="Add Tag", button_type="success")
        button.on_event(ButtonClick, self.add_button_callback)
        return button

    def add_button_callback(self, event):
        """
        Calls the funktion that opens the window to add new tags.
        """
        self.add_tag_group.visible = True

    def create_search_bar(self) -> TextInput:
        """
        Creates and returns a textfield, which filters the list of tags on input.
        @return TextInput
        """
        text_input = TextInput(placeholder="Filter for a tag")
        text_input.on_change("value_input", self.tagsearch_callback)
        return text_input

    def create_checkbox_group(self) -> CheckboxGroup:
        """
        Creates and returns a CheckboxGroup, where tags from selected documents
        are activated.
        @return CheckboxGroup
        """
        label_list = self.document_client.get_all_tags()
        checkbox_group = CheckboxGroup(labels=label_list, active=[])
        checkbox_group.on_change('active', self.checkbox_callback)
        checkbox_group.styles = {'overflow-y': 'scroll',
                                 'height': '200px', 'width': '170px'}
        return checkbox_group

    def create_tag_name_input(self) -> TextInput:
        """
        Creates and returns a textfield to enter name of a new tag.
        @return TextInput
        """
        text_input = TextInput(
            placeholder="e.g. artificial intelligence", title="Enter a new tag:")
        return text_input

    def create_description_input(self) -> TextAreaInput:
        """
        Creates and returns a textarea to enter a description for a new tag.
        @return TextAreaInput
        """
        text_area_input = TextAreaInput(
            placeholder="Your description here...", rows=6, title="Description:")
        return text_area_input

    def create_save_button(self) -> Button:
        """
        Creates and returns a button to save a new tag and apply it to the current
        selection.
        @return Button
        """
        button = Button(label="Save", button_type="success")
        button.on_event(ButtonClick, self.save_tag_callback)
        return button

    def create_add_tag_group(self) -> column:
        """
        Groups and returns the elements as column that are used to add new tags.
        @return column
        """
        add_tag_group = column(
            children=[self.tag_name_input, self.description_input, self.save_button])
        add_tag_group.visible = False
        return add_tag_group

    def create_search_tag_group(self) -> column:
        """
        Groups and returns a column object of the elements which are shown if a
        group of documents is selected.
        @return column
        """
        search_tag_group = column(
            children=[self.search_bar, self.checkbox_group, self.add_button])
        return search_tag_group

    def compute_indices_from_lables(self) -> list:
        """
        Returns a list of the indices of the tags, which are applied to at least
        one document from the current selection of documents.
        @return list of ints
        """
        indices = []
        active_labels = self.document_client.get_tags_by_ids(self.ids)
        for label in active_labels:
            if label in self.checkbox_group.labels:
                i = self.checkbox_group.labels.index(label)
                indices.append(i)
        return indices

    def tagsearch_callback(self, attr, old, new):
        """
        Filters the displayed tags in the CheckboxGroup based on the given input
        in the textfield.
        """
        filtered_tag_list = self.document_client.get_tags_by_partial_words(
            new.lower())
        active_tag_list = self.document_client.get_tags_by_ids(self.ids)
        filtered_active_tag_indices = []
        for tag in active_tag_list:
            if tag in filtered_tag_list:
                filtered_active_tag_indices.append(
                    filtered_tag_list.index(tag))
        self.checkbox_group.update(
            labels=filtered_tag_list, active=filtered_active_tag_indices)

    def save_tag_callback(self, event):
        """
        Saves the new tag with decription and calls the update method of the bar
        chart widget. If the tagname is empty then a warning is displayed.
        """
        tag_name = self.tag_name_input.value
        if tag_name != "":
            self.tag_name_input.value = ""
            tag_description = self.description_input.value
            self.description_input.value = ""
            # add new tag to checkbox group
            self.document_client.add_new_tag(tag_name, tag_description)
            self.document_client.add_tag_to_articles(tag_name, self.ids)

            # make new tag selected
            sorted_labels, active_indices = self.sort_checkbox_options(self.document_client.get_all_tags(),
                                                                       self.document_client.get_tags_by_ids(self.ids))
            self.checkbox_group.update(
                labels=sorted_labels, active=active_indices)
            self.add_tag_group.visible = False
            self.tag_name_input.placeholder = "e.g. artificial intelligence"
            self.bar_chart_widget.add_tag(tag_name, len(self.ids))
        else:
            self.tag_name_input.placeholder = "Please enter a tag name!"

    def sort_checkbox_options(self, all_tags: list, active_tags: list) -> tuple[list, list]:
        """
        Sorts the list of tags used by the checkboxlist so that the active tags
        are always on top and the active and inactive ones are additionally sorted
        alphabetically.  
        @param list all_tags: the list of all tags.
        @param list active_tags: a list of indices which indicate which tags from
            the all tags list are active (selected).
        @return tuple(list, list)
        """
        diff_tags = list(set(all_tags).symmetric_difference(set(active_tags)))
        active_tags.sort()
        diff_tags.sort()
        sorted_tags = active_tags + diff_tags
        num_active_indices = len(active_tags)
        active_indices = [i for i in range(0, num_active_indices)]
        return sorted_tags, active_indices

    # checkbox callbacks
    def checkbox_callback(self, attr, old, new):
        """
        Adds or removes tags from a given group of documents.
        """
        diff_tag_indices = list(set(old).symmetric_difference(set(new)))
        for diff_tag_index in diff_tag_indices:
            if len(self.checkbox_group.labels) > diff_tag_index:

                diff_tag = self.checkbox_group.labels[diff_tag_index]
                if len(new) > len(old) and diff_tag not in self.document_client.get_tags_by_ids(self.ids):
                    self.document_client.add_tag_to_articles(
                        diff_tag, self.ids)
                    self.bar_chart_widget.update_tag_count(
                        diff_tag, len(self.ids))
                elif len(new) < len(old) and diff_tag in self.document_client.get_tags_by_ids(self.ids):
                    self.document_client.delete_tag_from_articles(
                        diff_tag, self.ids)
                    self.bar_chart_widget.update_tag_count(diff_tag, 0)

    def update_tags_in_checkbox(self):
        """
        Updates which checkboxes are active, when the checkboxes shown are changed.
        """
        active_labels = self.document_client.get_tags_by_ids(self.ids)
        active_list = []
        for label in active_labels:
            if label in self.checkbox_group.labels:
                i = self.checkbox_group.labels.index(label)
                active_list.append(i)
        labels_sorted, active_list = self.sort_checkbox_options(
            self.checkbox_group.labels, active_labels)
        self.checkbox_group.labels = labels_sorted
        self.checkbox_group.active = active_list

    def set_visible(self, visibility: bool):
        """
        Sets the visibility of the entire widget with all it components.
        """
        self.column.visible = visibility

    def give_to_curdoc(self):
        """
        Gives the widget to curdoc to be diplayed in the browser.
        """
        curdoc().add_root(self.column)
