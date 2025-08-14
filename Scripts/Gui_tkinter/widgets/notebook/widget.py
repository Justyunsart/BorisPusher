"""
Will define the widget that is created in the nested nested notebook tab.

GOAL:
Constructor for a preset configuration of a nested notebook tab.
Provide the name of the notebook tab, alongside a class (child of a tk.Frame) to display.
Save automatically to the state dictionary
"""
import tkinter as tk
from tkinter import ttk
from system.temp_manager import TEMPMANAGER_MANAGER, read_temp_file_dict, write_dict_to_temp
from system.temp_file_names import param_keys, m1f1
import settings.palettes as p
from settings.configs.funcs.config_reader import runtime_configs
import os
from Gui_tkinter.funcs import data_helpers


class Field_Notebook(ttk.Notebook):
    """
    Parameters:
        master: the parent widget that owns this notebook
        tab_names, tab_widgets: lists that contain the respective notebook tab names, alongside their displayed widgets.
    """
    def __init__(self, master, tab_names:list, tab_widgets:list, collection_key, tab_key, dataclasses,
                 dir_names=["bob_e"], path_key="", field="", **kwargs):
        def _check_notebook_inputs() -> None:
            """
            Function that is just a container for all the assert statement for this class
            """
            assert len(tab_names) == len(tab_widgets), f"{len(tab_names)} != {len(tab_widgets)}"

        # define style for tabs
        style1 = ttk.Style()
        style1.theme_use('default')
        style1.configure('Nested.TNotebook.Tab',
                         font=('Arial', 18),
                         padding=8,
                         borderwidth=0,
                         foreground='black',
                         background=p.Drapion.Text.value)

        style1.configure('Nested.TNotebook',
                         tabposition="n",
                         borderwidth=0,
                         background='white')

        style1.map(
            'Nested.TNotebook.Tab',
            background=[("selected", p.Drapion.Text_Bright.value)],
            foreground=[("selected", 'black')],
            font=[("selected", ('Arial', 18, 'bold'))]
        )

        # PRE-CREATION
        # init the super
        super().__init__(master, style='Nested.TNotebook', padding="0 12 2 0", **kwargs)
        # check the legality of inputs
        _check_notebook_inputs()
        # define instance attributes
        self.tab_names = tab_names
        self.tab_widgets = tab_widgets
        #self.e_collection_key = (param_keys.field_methods.name, 'e', param_keys.params.name, 'collection')
        self.collection_key = collection_key
        self.tab_key = tab_key

        # CONFIGURE STRUCTURE
        def _add_notebook_tabs() -> None:
            # get the dir of the input folder to look at
            #dir = os.path.join(runtime_configs['Paths']['inputs'], dir_names[i])
            for i in range(len(self.tab_names)):
                self.add(self.tab_widgets[i](self, collection_key=self.collection_key, dataclass=dataclasses[i],
                                             dir_name=dir_names[i], path_key=path_key, field=field),
                         text=self.tab_names[i])

        _add_notebook_tabs()
        self.bind('<<NotebookTabChanged>>', self.on_tab_change)
        self.select_last_used_tab()

    def update(self, keys, value):
        """
        Function call triggered from relevant 'write' events called from tab_content widgets.
        is supposed to call out the program (this function) to update the internal runtime dictionary.

        :params:
        keys: a list of keys mapping the nested structure (if any) of the value to be changed
        value: the updated value itself
        """
        def set_nested_value(d, keys, value):
            """Set a value in a nested dictionary given a list of keys."""
            for key in keys[:-1]:
                d = d.setdefault(key, {})  # ensures intermediate dicts exist
            d[keys[-1]] = value

        # read the dictionary
        d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])

        # set the nested key to the updated value
        set_nested_value(d, keys, value)

        # write the updated dict to the file
        write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)

    def select_tab_by_name(self, tab_name):
        """Selects a tab in a ttk.Notebook by its displayed text name."""
        for tab_id in self.tabs():
            if self.tab(tab_id, 'text') == tab_name:
                self.select(tab_id)
                return True  # Tab found and selected
        return False  # Tab not found

    def select_last_used_tab(self):
        d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])
        try:
            tab_name = data_helpers.get_nested_value(d, self.tab_key)
            self.select_tab_by_name(tab_name)
            tab_id = self.select()  # reference to the active tab
            tab_widget = self.nametowidget(tab_id)
            text = self.tab(tab_id, "text")  # get the name of the tab (what u see on GUI)
            tab_widget.onActive(self.tab_key, self.collection_key, text, is_init=True)
        except KeyError:
            pass

    def on_tab_change(self, event, *args):
        """
        When these tabs are changed, you have to update that the respective method names have changed
        """
        def set_nested_value(d, keys, value):
            """Set a value in a nested dictionary given a list of keys."""
            for key in keys[:-1]:
                d = d.setdefault(key, {})  # ensures intermediate dicts exist
            d[keys[-1]] = value
        # get the widget tab name
        tab_id = self.select() # reference to the active tab
        text = self.tab(tab_id, "text") # get the name of the tab (what u see on GUI)

        # read the dictionary
        d = read_temp_file_dict(TEMPMANAGER_MANAGER.files[m1f1])

        # set the nested key to the updated value
        set_nested_value(d, list(self.tab_key), text)

        # write the updated dict to the file
        write_dict_to_temp(TEMPMANAGER_MANAGER.files[m1f1], d)

        # also, run logic for the tabs (that they should upon becoming active)
        try:
            tab_widget = self.nametowidget(tab_id)
            tab_widget.onActive(self.tab_key, self.collection_key, text)
        except AttributeError:
            pass
