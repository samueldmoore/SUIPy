# -*- coding: utf-8 -*-
""" suipy: GUI toolkit for scientific computational simulations

This module contains the classes to implement the factory method design
pattern to generate a GUI, give it functionality, read its data, manipulate
the generated elements' properties, and work with JSON-formatted
configurations. 

To use its classes, it is reccomended that the developer inherit from the
GUI class and add whatever functions are needed for the user interface at
hand.

Additional builders, getters, managers, etc. may be written and
registered with the respective factory-level class for use in a particular
script.

"""
import json
import os
from typing import Dict, Tuple
from collections import OrderedDict
# Import GUI elements classes from the tkinter package.
from tkinter import (Tk, Label, Entry, Button, Checkbutton, messagebox, Grid,
                     Pack, BaseWidget, Frame, Menu, Text, filedialog, END,
                     StringVar, DoubleVar, IntVar, ttk)


class GUIData:
    """ This is a class of data-storage objects to hold GUI set up data

    """

    def __init__(self, filepath, configuration_data_key="configuration_data",
                 builder_keys_key="builder_keys"):
        """ Take read in GUI data in json and initialize mapping dicts.

        Args:
            filepath (str): Path to file from which to read data
            configuration_data_key (str): Key used to access configuration
                data in json-serialized object.
            builder_keys_key (str): Key used to access builder key
                data in json-serialized object.

        Returns:
            GUIData: Initialized object containing all data needed to set up
                a GUI.

        """

        self.set_data_from_file(filepath, configuration_data_key,
                                builder_keys_key)

        self._builder_mapping = {
            "NoneType": GenericBuilder(),
            "window": WindowBuilder(),
            "menu_bar": MenuBarBuilder(),
            "drop_down_menu": DropDownMenuBuilder(),
            "menu_command": MenuCommandBuilder(),
            "frame": FrameBuilder(),
            "tab_binder": TabBinderBuilder(), 
            "tab": TabBuilder(), "text_line": TextLineBuilder(),
            "text_box": TextEntryBoxBuilder(),
            "entry": ValueEntryBuilder(),
            "drop_down": DropDownBuilder(),
            "button": ButtonBuilder()}

        self._getter_mapping = {
            "NoneType": NoneGetter(),
            "entry": StringVarGetter(),
            "drop_down": StringVarGetter(),
            "text_box": TextGetter(),
            "window": LiteralGetter()}

        self._binder_mapping = {
            "NoneType": GenericBinder(),
            "button_press": CommandBinder(),
            "window_close": ExitButtonBinder()}

        self._manager_mapping = {
            "other": DummyManager(),
            "start_event_loop": RunManager(),
            "style": StyleManager(),
            "content_edit": EditContentManager(),
            "quit_close": QuitManager(),
            "hide_show": HideShowManager(),
            "set_entry_defaults": EntryDefaultsManager(),
            "set_drop_down_defaults": DropDownDefaultsManager(),
            "set_text_box_defaults": TextDefaultsManager()}

        self._pop_up_mapping = {
            "other": GenericPopUp(),
            "ok_cancel": GenericPopUp(),
            "yes_no": YesNoPopUp(),
            "yes_no_cancel": YesNoCancelPopUp(),
            "file_open": FileOpenPopUp(),
            "file_save_as": FileSaveAsPopUp()}

    def read_json(self, file_to_read, file_encoding="utf8"):
        """ Read in json file as string and return json object

        Args:
            file_to_read (str): Path to file from which to read data.

        Returns:
            dict or list: Python object containing json-decoded data

        Raises:
            ValueError: If the inputted file does not have .json extension.

        """

        # Check that it's got a .json extension.
        if os.path.splitext(file_to_read)[1] == ".json":
            # Read in the file contents and load that as an object to return.
            with open(file_to_read, "r", encoding=file_encoding) as file_handle:
                return json.loads(file_handle.read())
        else:
            raise ValueError("The file is not recognized as .json")

    def set_data_from_file(self, file_to_read,
                           configuration_data_key="configuration_data",
                           builder_keys_key="builder_keys"):
        """ Set the object's data equal to the json data from file_to_read

        Args:
            file_to_read (str): Path to file from which to read data.
            configuration_data_key (str): Key used to access configuration
                data in json-serialized object.
            builder_keys_key (str): Key used to access builder key
                data in json-serialized object.

        Returns:
            None

        """
        all_data = self.read_json(file_to_read)
        self._config_data = all_data[configuration_data_key]
        self._builder_keys = all_data[builder_keys_key]

    def write_json(self, filepath, json_data_to_write, file_encoding="utf8"):
        """ Write json-serializable data to a specified file

        Args:
            filepath (str)
            json_data_to_write: A python object to serialize to json and write
                to the file.

        Returns:
            None

        """

        with open(filepath, "w", encoding=file_encoding) as data_file:
            data_file.write(json.dumps(json_data_to_write, indent=4))

    def write_data_to_file(self, filepath):
        """ Write the object's config data and key data into a json file

        Args:
            filepath (str) the path to a file to which to write the data.

        Returns:
            None

        """

        savable_data = {"configuration_data": self._config_data,
                        "builder_keys": self._builder_keys}

        self.write_json(filepath, savable_data)

    def get_builder_keys(self):
        return self._builder_keys
    
    def set_builder_keys(self, builder_keys):
        self._builder_keys = builder_keys

    def get_config_data(self):
        return self._config_data

    def set_config_data(self, config_data):
        self._config_data = config_data

    def get_action_mapping(self):
        return self._action_mapping

    def set_action_mapping(self, action_mapping):
        self._action_mapping = action_mapping

    def get_builder_mapping(self):
        return self._builder_mapping
    
    def set_builder_mapping(self, builder_mapping):
        self._builder_mapping = builder_mapping

    def get_getter_mapping(self):
        return self._getter_mapping

    def set_getter_mapping(self, getter_mapping):
        self._getter_mapping = getter_mapping

    def get_binder_mapping(self):
        return self._binder_mapping

    def set_binder_mapping(self, binder_mapping):
        self._binder_mapping = binder_mapping

    def get_manager_mapping(self):
        return self._manager_mapping

    def set_manager_mapping(self, manager_mapping):
        self._manager_mapping = manager_mapping

    def get_pop_up_mapping(self):
        return self._pop_up_mapping

    def set_pop_up_mapping(self, pop_up_mapping):
        self._pop_up_mapping = pop_up_mapping



class GenericBuilder:
    """ This is a base class for all the GUI element builders.

    Builder classes are lower level classes for the initial set-up of the GUI.
    They deal directly with tkinter ojbects and methods. If necessary, they
    may be re-written to generate a GUI using a different library, but
    hopefully retain the same interface (type of input parameters and output
    data).

    """

    _default_position = (0, 0)
    _parameter_and_variable_types = {"string": (StringVar, str), "integer": (
        IntVar, int), "decimal": (DoubleVar, float)}
    _data_keys = {}

    def __init__(self, default_aesthetics=(15, "arial 14", 1.25, 2.5),
                 **kwargs):
        """ Take parameters for and initialize default appearance settings.

        Args:
            default_aesthetics (tuple): 4-tuple containing the entry box
                character width, str specifying font type and size and bold or
                unbold (normal), default horizontal external padding
                for each element, and default vertical padding.
            **kwargs: Ignored parameters.

        """

        self._name = "GenericBuilder"
        GenericBuilder._default_aesthetics = default_aesthetics

    def __call__(self, name=None, level=0, **kwargs):
        """ Print the name and each property of the passed element data.

        Print the element's name and each value in **kwargs, with its key.
        The __call__() method is called whenever parentheses are placed after
        an object.

        Args:
            name (str, optional)
            level (int, optional): indentation level for printing.
            **kwargs: Properties (strings) such as
                **{"type": "some_type_of_element", "parameter": "param1"}.

        Returns:
            dict: Configuration data (user-specifiable) and object initialized
                using tkinter (which is None in this case).

        """

        print((level) * "    ", name)

        for kw in kwargs:
            print((level) * "    ", kw, "is", kwargs[kw])
        print("")

        return self._return_data(element_name=name,
                                 element_type="Nonetype",
                                 element_widget=None,
                                 element_parameter=None,
                                 element_specific_properties=kwargs)

    def get_name(self):
        return self._name

    def _place(self, widget, vertical_pos=0, horizontal_pos=0, side="w",
               horiz_external_padding=5, vert_external_padding=2.5,
               horiz_internal_padding=0, vert_internal_padding=0):
        """ Grid-position a widget in a given location on its master widget.

        This only works on elements within a window or other container.
        It does not work on windows themselves.

        Args:
            widget (tkinter object, e.g. ttk.Label()): Widget to position on
                layout.
            vertical_pos (int, optional): Where to place the widget in the
                vertical direction; the row number from the top (row 0).
            horizontal_pos (int, optional): Where to place the widget in the
                horizontal direction; the row number from the left (column 0).
            side (str, optional): Either "n", "s", "e", "w" or a concatanation
                of two of these.
            horiz_external_padding (int): How much padding [pixels] to place
                left and right around the outside of the placed widget.
            vert_external_padding (int): How much padding [pixels] to place
                above and below around the outside of the placed widget.
            horiz_internal_padding (int): How much padding [pixels] to place
                left and right just inside of the placed widget's perimeter.
            vert_internal_padding (int): How much padding [pixels] to place
                above and below just inside of the placed widget's perimeter.

        Returns:
            None

        """

        widget.grid(row=vertical_pos, column=horizontal_pos,
                    padx=horiz_external_padding, pady=vert_external_padding,
                    ipadx=horiz_internal_padding, ipady=vert_internal_padding,
                    sticky=side)

    def _return_data(self, element_type, element_name,
                     element_specific_properties,
                     element_widget, element_parameter,
                     parameter_name=None, activator="always_readable",
                     required_value=True, event_type="NoneType",
                     action="print", visible=True,
                     on_new_row=False, column=0, **kwargs):
        """ Build and return a nested dict with all element data.

        Args:
            element_type (str): The type of the element.
            element_name (str)
            element_specific_properties (dict): Any additional properties,
                besides those specified in the other args, for this element.
            parameter_name (str): Name of the parameter associated
                        with or controlled by the widget.
            activator (str): Name of the parameter which must have a
                certain value for this element's parameter to
                be readable (have accessible value) by the GUIReader
            required_value (bool): The value that the "activator" must
                have for this element's parameter to be
                readable.
            event_type (str): Identifier for type of event to trigger
                any action associated to the this element.
            action (str): String mapped to a action defined at the
                time of this element's generation. The action is
                performed when the element's event_type occurs, and
                the action itself must be a callable Python function
                or object. An object's callable function is its
                special __call__() method.
            visible (bool): Whether or not the element is visible when
                first initialized. This might be changed later when a
                manager object makes the element invisible.
            **kwargs: Unpacked dictionary of data keys, plus ignored
                parameters.

        Returns:
            dict: A data structure containing all data necessary to manipulate
                and re-generate the element, including the element's widget
                object itself, which is passed as a parent to any child
                elements.
                sub-dict config_data contains:
                    element_type: The type of the element
                    element_name (str): The name associated with the element
                        and used by other methods, such as to find the data
                        for the element.
                    properties (dict): All passed properties used to
                        initialize the element plus the defaults for those
                        that where unspecified
                        It contains:
                            parameter_name (str)
                            activator (str)
                            required_value (bool)
                            event_type (str)
                            action (str)
                            visible (bool)
                            plus any specific properties in
                                element_specific_properties
                    list: List of element's children. Only some elements can
                        have children. For others, it is an empty list.
                sub-dict objects_data contains:
                    element_widget (ttk object): primary widget for this
                        element, which is used as the parent for any children.
                    element_parameter (type varies): Can be a ttk Variable,
                        a widget, or a literal value such as a bool or str.

        """
        properties = {kwargs["parameter_name_key"]: parameter_name,
                      kwargs["activator_key"]: activator,
                      kwargs["required_value_key"]: required_value,
                      kwargs["event_type_key"]: event_type,
                      kwargs["action_key"]: action,
                      kwargs["visible_key"]: visible,
                      kwargs["on_new_row_key"]: on_new_row,
                      kwargs["column_key"]: column,
                      **element_specific_properties}

        config_data = {kwargs["type_key"]: element_type,
                       kwargs["name_key"]: element_name,
                       kwargs["properties_key"]: properties,
                       kwargs["children_key"]: []}
        objects_data = {kwargs["widget_key"]: element_widget,
                        kwargs["parameter_key"]: element_parameter}

        element_data = {kwargs["config_data_key"]: config_data,
                        kwargs["objects_key"]: objects_data}

        return element_data

    def get_aesthetics(self):
        """ Return the currently set default aesthetic settings for builders.

        This method is available to all builders unless overridden.


        Returns:
            tuple: 4-tuple containing the entry box character
                width, str specifying font type and size and bold or
                unbold (normal), default horizontal external padding
                for each element, and default vertical padding.

        """

        return GenericBuilder._default_aesthetics


class WindowBuilder(GenericBuilder):
    """ This is a class of builders to initialize window elements.

    """

    def __init__(self):
        """ Initialize the builder's name (class name)

        """

        self._name = "WindowBuilder"

    def __call__(self, name, visible_text_key,
                 size_and_position_key, properties, **kwargs):
        """ Take window properties and generate a window accordingly

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for window element (used by other classes, not
                display name).
            visible_text_key (str): String key to set and access static
                displayed text for elements.
            size_and_position_key (str): String key to set and access size
                and position on screen for elements.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                size_and_position (str): A string specifying the
                    width and height and horizontal and vertical
                    distance from the upper left corner of the
                    screen in pixels. The format is
                    "[width]x[height]+[x]+[y]" where each quantity
                    in brackets is a positive number. Note that y
                    is measured down from the top of the screen,
                    and x is measured to the right from the left
                    edge.
                visible_text (str): Read-only text displayed on the widget
                    itself. For a window it is in the title bar.

        """
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]

        size_and_position = properties.get(size_and_position_key,
                                           "1040x640+0+0")
        visible_text = properties.get(visible_text_key,
                                      "Default Window Title")
        parameter_name = properties.get(parameter_name_key,
                                        "always_readable")
        activator = properties.get(activator_key, "always_readable")
        event_type = properties.get(event_type_key, "window_close")
        required_value = False  # Windows do not have a parameter to be read.
        visible = True
        action = properties.get(action_key, "exit")

        window = Tk()
        window.geometry(size_and_position)
        window.title(visible_text)
        window.protocol("WM_DELETE_WINDOW", kwargs[action])

        spec_properties = {visible_text_key: visible_text,
                           size_and_position_key: size_and_position}

        data = self._return_data(element_type="window",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=window, element_parameter=True,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 event_type=event_type,
                                 required_value=required_value,
                                 visible=visible, action=action, **kwargs)

        return data


class MenuBarBuilder(GenericBuilder):
    """ This is a class of builders for menu bars at the top of windows.

    The menu bar is an exception to the norm of in-window placeable elements.
    It only goes at the top of a window, so the "on_new_row" and "column"
    properties are irrelevant and ignored by the builder.

    """

    def __init__(self):
        """ Initialize a builder with a name from its class

        """
        self._name = "MenuBarBuilder"

    def __call__(self, name, parent, properties, **kwargs):
        """ Take menu bar properties and generate a menu bar accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for menu bar element (used by other classes, not
                display name).
            parent (Tk()): A tkinter window object to hold the menu bar
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                There are no specific properties for a menu bar.

        """
        if not isinstance(parent, Tk):
            raise ValueError(
                "Attempted to create menu bar with parent other than window.")

        activator_key = kwargs["activator_key"]

        parameter_name = None
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        event_type = "NoneType"
        action = None
        visible = True

        # Initialize and place a Menu widget at the top of the parent window.
        menubar = Menu(master=parent)
        parent.config(menu=menubar)

        data = self._return_data(element_type="menu_bar", element_name=name,
                                 element_specific_properties={},
                                 element_widget=menubar,
                                 element_parameter=None,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 **kwargs)
        return data


class DropDownMenuBuilder(GenericBuilder):
    """ This is a class of builders to construct menus in a menu bar.

    """

    def __init__(self):
        """ Initialize a DropDownMenuBuilder with a name from its class

        """

        self._name = "DropDownMenuBuilder"

    def __call__(self, name, parent, visible_text_key, properties, **kwargs):
        """ Take menu properties and generate a drop-down menu accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for drop-down menu element (used by other
                classes; not the display name).
            parent (Menu()): A tkinter menu to hold the drop-down menu
            visible_text_key (str): String key to set and access static
                displayed text for elements.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                visible_text (str): Read-only text displayed on the widget
                    itself. For a drop-down menu, it is shown over the menu.

        """
        if not isinstance(parent, Menu):
            raise ValueError(
                "Attempted to create drop-down menu elsewhere than menu bar.")

        activator_key = kwargs["activator_key"]

        visible_text = properties.get(visible_text_key, "Menu")
        parameter_name = None
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        event_type = "NoneType"
        action = None

        # Initialize and place a Menu widget in the parenting Menu.
        menu = Menu(master=parent)
        parent.add_cascade(menu=menu, label=visible_text)

        spec_properties = {visible_text_key: visible_text}

        data = self._return_data(element_type="drop_down_menu",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=menu,
                                 element_parameter=None,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 **kwargs)
        return data


class MenuCommandBuilder(GenericBuilder):
    """ This is a class of builders to construct menus in a menu command.

    """
    def __init__(self):
        self._name = "MenuCommandBuilder"

    def __call__(self, name, parent, visible_text_key, properties, **kwargs):
        """ Take menu command properties and generate a command accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for menu command element (used by other classes, not
                display name).
            parent (Menu()): A tkinter menu to hold the menu_command
            visible_text_key (str): String key to set and access static
                displayed text for elements.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                visible_text (str): Read-only text displayed on the widget
                    itself. For a menu command it is shown over the command.

        """
        msg = "Attempted to create menu_command with parent otherthan menu bar."
        if not isinstance(parent, Menu):
            raise ValueError(msg)

        activator_key = kwargs["activator_key"]
        action_key = kwargs["action_key"]

        parameter_name = None
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        visible_text = properties.get(
            visible_text_key, "Default Command Label")
        event_type = "NoneType"
        action = properties.get(action_key, "print")

        # Initialize and place a menu command in the parenting menu.
        parent.add_command(label=visible_text, command=kwargs[action])

        spec_properties = {visible_text_key: visible_text}

        data = self._return_data(element_type="menu_command",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=None,
                                 element_parameter=None,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 **kwargs)

        return data


class FrameBuilder(GenericBuilder):
    """ This is a class of builders to construct labeled frames in a window.

    """
    def __init__(self):
        self._name = "FrameBuilder"

    def __call__(self, name, parent, current_row, current_column,
                 visible_text_key, width_key, height_key, properties,
                 **kwargs):
        """ Take frame properties and generate a frame accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for frame element (used by other classes, not
                display name).
            parent (type varies): A tkinter object to hold the frame.
            current_row (int): The row on which the frame is generated
            current_column (int): The column in which the frame is
                generated.
            visible_text_key (str): String key to set and access static
                displayed text for elements.
            width_key (str): String key to set and access widget width.
            height_key (str): String key to set and access widget height.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                width (int): The width in pixels.
                height (int): The height in pixels.
                visible_text (str): Read-only text displayed on the widget
                    itself. For a frame it is shown in the frame's border.

        """
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        column_key = kwargs["column_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]
        on_new_row_key = kwargs["on_new_row_key"]

        # Get given properties or defaults.
        parameter_name = None
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        event_type = "NoneType"
        action = None
        on_new_row = properties.get(on_new_row_key, False)
        visible_text = properties.get(visible_text_key, None)
        width = properties.get(width_key, 500)
        height = properties.get(height_key, 20)

        # Initialize and place a LabelFrame at the specified location.
        frame = ttk.LabelFrame(master=parent, width=int(
            width), height=int(height), text=visible_text)
        self._place(frame, vertical_pos=current_row,
                    horizontal_pos=current_column)

        spec_properties = {visible_text_key: visible_text, width_key: width,
                           height_key: height}

        data = self._return_data(element_type="frame",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=frame,
                                 element_parameter=None,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 on_new_row=on_new_row,
                                 column=current_column,
                                 **kwargs)

        return data


class TabBinderBuilder(GenericBuilder):
    """ This is a class of builders to construct containers for tabs.

    """
    def __init__(self):
        self._name = "TabBinderBuilder"

    def __call__(self, name, parent, current_row, current_column, properties,
                 **kwargs):
        """ Take tab binder properties and generate a tab binder accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for tab binder element (used by other classes, not
                display name).
            parent (type varies): A tkinter object to hold the tab binder.
            current_row (int): The row on which the tab binder is generated
            current_column (int): The column in which the tab binder is
                generated.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data

        """
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        column_key = kwargs["column_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]
        on_new_row_key = kwargs["on_new_row_key"]

        parameter_name = None
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        event_type = "NoneType"
        action = None
        on_new_row = properties.get(on_new_row_key, False)

        # Initialize a Notebook to hold tabs as defined later.
        binder = ttk.Notebook(master=parent)
        self._place(binder, vertical_pos=current_row,
                    horizontal_pos=current_column)


        data = self._return_data(element_type="tab_binder",
                                 element_name=name,
                                 element_specific_properties={},
                                 element_widget=binder,
                                 element_parameter=None,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 on_new_row=on_new_row,
                                 column=current_column,
                                 **kwargs)

        return data


class TabBuilder(GenericBuilder):
    """ This is a class of builders to construct tabs.

    """
    def __init__(self):
        self._name = "TabBuilder"

    def __call__(self, name, parent, visible_text_key, properties, **kwargs):
        """ Take tab properties and generate a tab accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for tab element (used by other classes, not
                display name).
            parent (type varies): A tkinter object to hold the tab.
            visible_text_key (str): String key to set and access static
                displayed text for elements.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                visible_text (str): Read-only text displayed on the widget
                    itself. It is shown on the tab.

        """
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        column_key = kwargs["column_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]

        parameter_name = None
        visible_text = properties.get(visible_text_key, "Default Tab Label")
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        event_type = "NoneType"
        action = None

        # Add a frame to a tab on the passed notebook object.
        frame = ttk.Frame(master=parent, relief="ridge")
        self._place(frame)

        msg1 = "You cannot add a tab to that parent."
        msg2 = "Ensure it's a \"tab_binder.\""
        try:
            parent.add(frame, text=visible_text)
        except AttributeError:
            raise AttributeError(msg1 + msg2)

        spec_properties = {visible_text_key: visible_text}

        data = self._return_data(element_type="tab",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=frame,
                                 element_parameter=None,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 on_new_row=False,
                                 column=parent.index(frame),
                                 **kwargs)

        return data



class TextLineBuilder(GenericBuilder):
    """ This is a class of builders to construct static, one-line text.

    """
    def __init__(self, **kwargs):
        self._name = "FrameBuilder"

    def __call__(self, name, parent, current_row, current_column,
                 visible_text_key, justification_key, properties,
                 **kwargs):
        """ Take text properties and generate a text accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for text element (used by other classes, not
                display name).
            parent (type varies): A tkinter object to hold the text.
            current_row (int): The row on which the text is generated
            current_column (int): The column in which the text is
                generated.
            justification_key (str): String key to set and access
                text justification.
            visible_text_key (str): String key to set and access static
                displayed text for elements.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                visible_text (str): Read-only text displayed on the widget
                    itself. It is shown in the text field on a single line.
                justification (str): Either "left", "right" or "center". The
                    justification of the text within the text line, if any
                    extra space is available in its column.

        """
        
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        column_key = kwargs["column_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]
        visible_key = kwargs["visible_key"]
        on_new_row_key = kwargs["on_new_row_key"]

        
        parameter_name = None
        visible_text = properties.get(visible_text_key, "Default text")
        justification = properties.get(justification_key, "left")
        visible = properties.get(visible_key, True)
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        event_type = "NoneType"
        action = None
        on_new_row = properties.get(on_new_row_key, False)

        # Initialize and place a Label at the specified location.
        text = ttk.Label(master=parent, text=visible_text,
                         justify=justification)
        self._place(text, vertical_pos=current_row,
                    horizontal_pos=current_column)

        if not ((visible == "True") or (visible == True) or (visible == "Yes")):
            text.grid_remove()
            initially_visible = False
        else:
            initially_visible = True
        spec_properties = {visible_text_key: visible_text,
                           justification_key: justification}

        data = self._return_data(element_type="text_line",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=text,
                                 element_parameter=None,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 visible=initially_visible,
                                 on_new_row=on_new_row,
                                 column=current_column,
                                 **kwargs)

        return data



class TextEntryBoxBuilder(GenericBuilder):
    """ This is a class of builders to construct dynamic text boxes.
    
    The field can be associated with a parameter. Its contents can be edited
    by the user or by the program.
    """
    def __init__(self):
        self._name = "TextEntryBoxBuilder"

    def __call__(self, name, parent, current_row, current_column, width_key,
                 height_key, default_text_key, has_scrollbar_key, properties,
                 **kwargs):
        """ Take text properties and generate a text accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for text element (used by other classes, not
                display name).
            parent (type varies): A tkinter object to hold the entry.
            current_row (int): The row on which the text is generated
            current_column (int): The column in which the text is
                generated.
            width_key (str): String key to set and access widget width.
            height_key (str): String key to set and access widget height.
            default_text_key (str): String key to set and access displayed
                text which might be edited by the user.
            has_scrollbar (bool): Whether or not a scrollbar is attached.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                default_text (str): Initial text displayed on the widget,
                    potentially over multiple lines. The user can edit it by
                    clicking in the box, typing or by copy-and-pasting.
                has_scrollbar (bool): Whether or not a scrollbar is attached.
                width (int): The width in characters.
                height (int): The height in lines.

        """
        
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        column_key = kwargs["column_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]
        visible_key = kwargs["visible_key"]
        on_new_row_key = kwargs["on_new_row_key"]

        parameter_name = None
        default_text = properties.get(default_text_key, "")
        width = properties.get(width_key, 40)
        height = properties.get(height_key, 5)
        has_scrollbar = properties.get(has_scrollbar_key, False)
        parameter_name = properties.get(
            parameter_name_key, "default_text_parameter_name")
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        event_type = "NoneType"
        action = None
        visible = properties.get(visible_key, True)
        on_new_row = properties.get(on_new_row_key, False)

        # Initialize text box with given parameters and place text in it.
        frame = ttk.Frame(master=parent)
        self._place(frame, vertical_pos=current_row,
                    horizontal_pos=current_column)

        text = Text(master=frame, width=width, height=height)
        text.config(wrap="word")
        text.insert(index=1.0, chars=default_text)
        self._place(text, vertical_pos=0, horizontal_pos=0,
                    horiz_external_padding=0)

        if ((has_scrollbar == True) or (has_scrollbar == "True")
            or (has_scrollbar == "Yes")):
            scroller = ttk.Scrollbar(master=frame,
                                     orient="vertical",
                                     command=text.yview)
            self._place(scroller, vertical_pos=0, horizontal_pos=1,
                        side="ns", horiz_external_padding=0)
            text.config(yscrollcommand=scroller.set)

        spec_properties = {default_text_key: default_text, width_key: width,
                           height_key: height,
                           has_scrollbar_key: has_scrollbar}

        data = self._return_data(element_type="text_box",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=text,
                                 element_parameter=text,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 on_new_row=on_new_row,
                                 column=current_column,
                                 **kwargs)

        return data



class ValueEntryBuilder(GenericBuilder):
    """ This is a class of builders to dynamic one-line text boxes.

    Each entry consists of a dynamic, one-line field alongside a static,
    one-line text label. The field can be associated with a parameter. Its
    contents can be edited by the user or by the program.
    """
    def __init__(self):
        self._name = "ValueEntryBuilder"

    def __call__(self, name, parent, current_row, current_column, width_key,
                 visible_text_key, default_value_key, properties, **kwargs):
        """ Take text properties and generate an entry element accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for entry element (used by other classes, not
                display name).
            parent (type varies): A tkinter object to hold the entry.
            current_row (int): The row on which the entry is generated.
            current_column (int): The column in which the entry is
                generated.
            width_key (str): String key to set and access widget width.
            visible_text_key (str): String key to set and access displayed
                text which cannot be edited by the user.
            default_value_key (str): String key to set and access displayed
                entry which might be edited by the user.
            has_scrollbar_key (str): String key to set and access whether or
                not a scrollbar is attached.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                visible_text (str): Read-only text displayed on the widget
                    itself. It is shown in the text field on a single line.
                default_value (str): Initial text displayed on the widget,
                    potentially over multiple lines. The user can edit it by
                    clicking in the box, typing or by copy-and-pasting.
                width (int): The width in characters.

        """
        
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        required_value_key = kwargs["required_value_key"]
        column_key = kwargs["column_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]
        visible_key = kwargs["visible_key"]
        on_new_row_key = kwargs["on_new_row_key"]

        
        
        parameter_name = properties.get(
            parameter_name_key, "default_parameter_name")
        activator = properties.get(activator_key, "always_readable")
        required_value = properties.get(required_value_key, True)
        event_type = "NoneType"
        action = None
        visible = properties.get(visible_key, True)
        on_new_row = properties.get(on_new_row_key, False)
        width = properties.get(width_key,
                               GenericBuilder._default_aesthetics[0])
        visible_text = properties.get(visible_text_key, "New Value Entry")
        default_value = properties.get(default_value_key, "0")

        # Initialize and place a containing frame for an entry box and a label.
        frame = ttk.Frame(master=parent)
        self._place(widget=frame, vertical_pos=current_row,
                    horizontal_pos=current_column)

        # Initialize and place an Entry widget with given parameters
        variable = StringVar()
        entry = ttk.Entry(master=frame,
                          textvariable=variable,
                          width=width,
                          font=GenericBuilder._default_aesthetics[1])
        entry.insert(0, string=str(default_value))
        self._place(widget=entry, vertical_pos=0, horizontal_pos=0)

        # Initialize and place a label next to it
        label = ttk.Label(master=frame, text=visible_text)

        self._place(widget=label, vertical_pos=0, horizontal_pos=1)
        spec_properties = {visible_text_key: visible_text,
                           default_value_key: default_value,
                           width_key: width}

        data = self._return_data(element_type="entry",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=frame,
                                 element_parameter=variable,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 on_new_row=on_new_row,
                                 column=current_column,
                                 **kwargs)

        return data



class DropDownBuilder(GenericBuilder):
    """ This is a class of builders to dynamic one-line drop-down boxes.

    Each drop-down consists of a dynamic, one-line field alongside a static,
    one-line text label. The field can be associated with a parameter. Its
    contents can be edited by the user or by the program.
    """
    def __init__(self):
        self._name = "DropDownBuilder"

    def __call__(self, name, parent, current_row, current_column, width_key,
                 visible_text_key, options_key, default_option_key,
                 only_selectable_key, properties, **kwargs):
        """ Take drop-down properties and generate an entry element accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for entry element (used by other classes, not
                display name).
            parent (type varies): A tkinter object to hold the entry.
            current_row (int): The row on which the entry is generated.
            current_column (int): The column in which the entry is
                generated.
            width_key (str): String key to set and access widget width.
            visible_text_key (str): String key to set and access displayed
                text which cannot be edited by the user.
            options_key (str): String key to set and access displayed
                options which might be selected or entered by the user.
            default_option_key (str): String key to set and access displayed
                option which might be edited by the user.
            only_selectable_key (str): String key to set and access whether
                or not the user can type in potentially arbitrary values and
                text.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs:button.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                visible_text (str): Read-only text displayed on the widget
                    itself. It is shown in the text field on a single line.
                width (int): The width in characters.
                options (str): String key to set and access displayed
                    options which might be selected or entered by the user.
                only_selectable (bool): Whether or not the user can type in
                    potentially arbitrary values and text.
                default_option (str): Initial option displayed on the widget,
                    potentially over multiple lines. The user can edit it by
                    clicking in the box, typing or by copy-and-pasting.

        """
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        required_value_key = kwargs["required_value_key"]
        column_key = kwargs["column_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]
        visible_key = kwargs["visible_key"]
        on_new_row_key = kwargs["on_new_row_key"]

        options = properties.get(options_key, "Default_Option")
        default_option = properties.get(default_option_key, None)
        only_selectable = properties.get(only_selectable_key, True)
        width = properties.get(width_key, "40")
        parameter_name = properties.get(
            parameter_name_key, "default_parameter_name")
        activator = properties.get(activator_key, "always_readable")
        required_value = properties.get(required_value_key, True)
        event_type = "NoneType"
        action = properties.get(action_key, None)
        visible = properties.get(visible_key, True)
        on_new_row = properties.get(on_new_row_key, False)
        visible_text = properties.get(visible_text_key, "Default drop-down text")

        variable = StringVar()
        frame = ttk.Frame(master=parent)
        text = ttk.Label(master=frame, text=visible_text)
        dropdown = ttk.Combobox(master=frame, values=options,
                                textvariable=variable,
                                width=width,
                                font=GenericBuilder._default_aesthetics[1])

        if default_option != None:
            dropdown.insert(0, string=str(default_option))
        else:
            dropdown.insert(0, string=str(options[0]))

        if ((only_selectable == True) or (only_selectable == "True")
            or (only_selectable == "Yes")):
            dropdown.config(state="readonly")

        if action is not None:
            dropdown.bind("<<ComboboxSelected>>", kwargs[action])
        
        self._place(dropdown, vertical_pos=0,
                    horizontal_pos=0)
        self._place(text, vertical_pos=0,
                    horizontal_pos=1)
        self._place(frame, vertical_pos=current_row,
                    horizontal_pos=current_column)

        spec_properties = {visible_text_key: visible_text, width_key: width,
                           options_key: options,
                           only_selectable_key: only_selectable,
                           default_option_key: default_option}

        data = self._return_data(element_type="drop_down",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=frame,
                                 element_parameter=variable,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 on_new_row=on_new_row,
                                 column=current_column,
                                 **kwargs)

        return data


class ButtonBuilder(GenericBuilder):
    """ This is a class of builders to buttons.

    Each button has an associated function callback it executes when clicked.
    """
    def __init__(self):
        self._name = "ButtonBuilder"

    def __call__(self, name, parent, current_row, current_column,
                 visible_text_key, properties, **kwargs):
        """ Take button properties and generate an button element accordingly.

        This method is called whenever the object's name is followed by 
        parentheses, as when calling a function. It uses the get() method's
        default return value option (2nd parameter) to specify defaults for
        all possible properties.

        Args:
            name (str): Name for button element (used by other classes, not
                display name).
            parent (type varies): A tkinter object to hold the button.
            current_row (int): The row on which the button is generated.
            current_column (int): The column in which the button is
                generated.
            visible_text_key (str): String key to set and access displayed
                text which cannot be edited by the user.
            properties (dict): Contains all properties for the element to be
                generated.
            **kwargs: Data keys to pass to self._return_data() plus ignored
                parameters.

        Returns:
            dict: The standard data described in GenericBuilder()._return_data
                plus the following specific properties:
                visible_text (str): Read-only text displayed on the widget
                    itself. It is shown in the text field on a single line.

        """
        
        parameter_name_key = kwargs["parameter_name_key"]
        activator_key = kwargs["activator_key"]
        column_key = kwargs["column_key"]
        event_type_key = kwargs["event_type_key"]
        action_key = kwargs["action_key"]
        visible_key = kwargs["visible_key"]
        on_new_row_key = kwargs["on_new_row_key"]

        
        parameter_name = None
        visible_text = properties.get(visible_text_key, "Default Button Text")
        activator = properties.get(activator_key, "always_readable")
        required_value = False
        event_type = "NoneType"
        action = properties.get(action_key, "print")
        visible = properties.get(visible_key, True)
        on_new_row = properties.get(on_new_row_key, False)

        # Initialize button with given parameters and place it.
        button = ttk.Button(master=parent, text=visible_text,
                            command=kwargs[action])
        self._place(button, vertical_pos=current_row,
                    horizontal_pos=current_column)

        spec_properties = {visible_text_key: visible_text}

        data = self._return_data(element_type="button",
                                 element_name=name,
                                 element_specific_properties=spec_properties,
                                 element_widget=button,
                                 element_parameter=None,
                                 parameter_name=parameter_name,
                                 activator=activator,
                                 required_value=required_value,
                                 event_type=event_type,
                                 action=action,
                                 on_new_row=on_new_row,
                                 column=current_column,
                                 **kwargs)

        return data


class GUIFactory:
    """ This is a class to call builders and pass them their parameters.

    This is an intermediate-level class in this module's object model.
    All the builders are low-level. They deal with tkinter objects and
    methods. The GUIFactory class does not. It just manages the builders.
    One of its responsibilities is to pass the keys used by the builders
    to access the configuration data.
    """

    def __init__(self, **kwargs):
        """ Initialize an empty list of builders and take unpacked data keys.

        Args:
            **kwargs: An unpacked dict containing all the required builder
                data keys.

        """

        self._builders = {}

        self._data_keys = kwargs

    def register_builder(self, type_key, builder):
        """ Take a type key and associate a builder with it internally.

        Args:
            type_key (str): The type of element for the builder to be assigned
                to build.
            builder (type varies): a callable function or object to build that
                type of element.
        
        Returns:
            None.
        """

        self._builders[type_key] = builder

    def _locate_element(self, element_config_data: dict, row=0,
                        default_column=0):
        """ Define element's position on the layout

        If on the same row as before, set current_column equal to itself
        if no custom column is specified.

        Args:
            element_config_data (dict): All data stored in an element data
                dict as that stored under config_data_key by builders.
            row (int): Row number currently being populated.
            default_column (int): Column which element will be placed on if no
                specific column is requested by the inputted config_data.
                The current column being populated.

        Returns:
            new_row (bool): Whether the element is placed on a new row or not.
            row (int): The row on which the element is actually placed (could
                be one more than the inputted row).
            column (int): The column on which the element is placed (could vary
                from the default column).
        """

        properties_key = self._data_keys["properties_key"]
        column_key = self._data_keys["column_key"]
        on_new_row_key = self._data_keys["on_new_row_key"]

        new_row = element_config_data[properties_key].get(on_new_row_key)

        if (new_row == True) or (new_row == "True") or (new_row == "Yes"):
            row += 1
            column = int(
                element_config_data[properties_key].get(column_key, 0))
        else:
            column = int(element_config_data[properties_key].get(
                column_key, default_column))

        return new_row, row, column

    def _build_element(self, element_config_data: dict, action_mapping: dict,
                       parent=None, row=0, default_column=0,
                       level=0):
        """ Build an element using the appropriate builder for its type.

        Args:
            element_config_data (dict): All data stored in an element data
                dict as that stored under config_data_key by builders.
            action_mapping (dict): All callable actions and their associated
                str names.
            row (int): Row number currently being populated.
            default_column (int): Column which element will be placed on if no
                specific column is requested by the inputted config_data.
                The current column being populated.
            level (int): The indentation level for textual printing feedback.

        Returns:
            element (type varies): The element data returned by the builder,
                including the widget object(s) itself/themselves.
            row (int): The row on which the element is actually placed (could
                be one more than the current row).
            column (int): The column on which the element is placed (could vary
                from the default column).
        """
        name_key = self._data_keys["name_key"]
        type_key = self._data_keys["type_key"]

        new_row, row, column = self._locate_element(
            element_config_data, row, default_column)

        builder = self._builders.get(element_config_data[type_key])
        if not builder:
            raise ValueError

        element = builder(current_row=row, current_column=column, level=level,
                          parent=parent, **element_config_data,
                          **action_mapping,
                          **self._data_keys)
        column += 1

        return (element, row, column)

    def create(
        self,
        configuration_data,
        action_mapping={"print": lambda: print("Default button callback")},
        inventory_list=[], parent_widget=None, level=0, **kwargs):
        """ Recursively loop through all element data dicts and build layout.

        Args:
            configuration_data (list): List of dicts as stored by GUIData.
                A list of all data stored in element data dicts as those
                stored under config_data_key by builders.
            action_mapping (dict): All callable actions and their associated
                str names.
            inventory_list: List to place element data into.
            parent_widget (type varies): The parenting tkinter widget for the
                currently generated element.
            level (int): The indentation level for textual printing feedback.

        Returns:
            inventory_list: List to of all element data.
        """
        # Define some names for convenience
        config_data_key = self._data_keys["config_data_key"]
        objects_key = self._data_keys["objects_key"]
        widget_key = self._data_keys["widget_key"]
        type_key = self._data_keys["type_key"]
        children_key = self._data_keys["children_key"]

        current_row = 0
        current_column = 0

        for element_config in configuration_data:
            (built_element_data,
             current_row,
             current_column) = self._build_element(
                 element_config_data=element_config,
                 action_mapping=action_mapping,
                 parent=parent_widget,row=current_row,
                 default_column=current_column,
                 level=level)

            inventory_list.append(built_element_data)
            children = element_config.get(children_key)

            # Recusively call create() on all the child elements.
            self.create(
                configuration_data=children,
                action_mapping=action_mapping,
                inventory_list=built_element_data.get(
                    config_data_key).get(children_key),
                parent_widget=built_element_data.get(
                    objects_key).get(widget_key),
                level=(level + 1))

        return inventory_list

    def get_builder_aesthetic_defaults(self):
        for type_key in self._builders:
            return self._builders[type_key].get_aesthetics()


class GenericBinder:
    def __init__(self):
        self._name = "GenericBinder"

    def __call__(self, single_element_data, GUI_action_mapping,
                 config_data_key, objects_key, name_key, properties_key,
                 event_type_key, action_key, level=0, **kwargs):

        self._print_action(element_data=single_element_data,
                           GUI_action_mapping=GUI_action_mapping,
                           config_data_key=config_data_key,
                           objects_key=objects_key,
                           name_key=name_key, properties_key=properties_key,
                           event_type_key=event_type_key,
                           action_key=action_key, level=level)
        return 0

    def _print_action(self, element_data,
                      GUI_action_mapping,
                      config_data_key, objects_key,
                      name_key, properties_key,
                      event_type_key,
                      action_key,
                      level=0):
        
        name = element_data.get(config_data_key).get(name_key)

        event_type = element_data.get(config_data_key).get(
            properties_key).get(event_type_key)

        action_name = element_data.get(config_data_key).get(
            properties_key).get(action_key)

        action = GUI_action_mapping.get(action_name)

        print(
            level*"   ",
            f"binding {name}'s {event_type} to function {action}")


class CommandBinder(GenericBinder):
    def __init__(self):
        self._name = "CommandBinder"

    def __call__(self, single_element_data, GUI_action_mapping,
                 config_data_key, objects_key, name_key, properties_key,
                 widget_key, event_type_key, action_key, level=0, **kwargs):

        self._print_action(element_data=single_element_data,
                           GUI_action_mapping=GUI_action_mapping,
                           config_data_key=config_data_key, objects_key=objects_key,
                           name_key=name_key, properties_key=properties_key,
                           event_type_key=event_type_key, action_key=action_key,
                           level=level)

        widget = single_element_data.get(objects_key).get(widget_key)
        action_name = single_element_data.get(
            config_data_key).get(properties_key).get(action_key)
        action = GUI_action_mapping.get(action_name)

        widget.config(command=action)


class ExitButtonBinder(GenericBinder):
    def __init__(self):
        self._name = "CommandBinder"

    def __call__(self, single_element_data, GUI_action_mapping,
                 config_data_key, objects_key, name_key, properties_key,
                 widget_key, event_type_key, action_key, level=0, **kwargs):

        self._print_action(element_data=single_element_data,
                           GUI_action_mapping=GUI_action_mapping,
                           config_data_key=config_data_key,
                           objects_key=objects_key,
                           name_key=name_key,
                           properties_key=properties_key,
                           event_type_key=event_type_key,
                           action_key=action_key, level=level)

        widget = single_element_data.get(objects_key).get(widget_key)
        action_name = single_element_data.get(
            config_data_key).get(properties_key).get(action_key)
        action = GUI_action_mapping.get(action_name)

        widget.protocol("WM_DELETE_WINDOW", action)


class GUIFunctionWorkshop:
    def __init__(self, **kwargs):
        self._function_binders = {}
        self._data_keys = kwargs

    def register_binder(self, event_type, binder_method):
        self._function_binders[event_type] = binder_method

    def _bind(self, single_element_data, GUI_action_mapping):
        func_binder = self._function_binders.get(
            single_element_data.get(
                self._data_keys.get(
                    "config_data_key")).get(
                        self._data_keys.get(
                            "properties_key")).get(
                                self._data_keys.get(
                                    "event_type_key")))
        if not func_binder:
            raise ValueError

        func_binder(
            single_element_data=single_element_data,
            GUI_action_mapping=GUI_action_mapping,
            **self._data_keys)

        return 0

    def set_up(self, element_data, GUI_action_mapping):
        for element_datum in element_data:
            self._bind(
                single_element_data=element_datum,
                GUI_action_mapping=GUI_action_mapping)

            child_element_data = element_datum.get(
                self._data_keys["config_data_key"]).get(
                    self._data_keys["children_key"])
            self.set_up(
                element_data=child_element_data,
                GUI_action_mapping=GUI_action_mapping)

        return 0


class NoneGetter:
    def __call__(self, var=None):
        return


class StringVarGetter(NoneGetter):
    def __call__(self, var):
        try:
            return var.get()
        except AttributeError:
            return str(var)


class TextGetter(NoneGetter):
    def __call__(self, txt):
        return txt.get(1.0, "end")


class LiteralGetter(NoneGetter):
    def __call__(self, var=False):
        return var


class GUIReader:
    """ This is a class to obtain values/text stored by elements of a layout.

    This is an intermediate-level class in this module's object model.
    All the builders are low-level. They deal with tkinter objects and
    methods. The GUIReader class does not. It just reads the parameters.
    This is a class on the same level as GUIFactory and GUISetterUpper.
    """
    def __init__(self, **kwargs):
        """ Initialize dicts to hold getters with their types and data keys.

        Args:
            **kwargs: An unpacked containing builder data keys.
        """

        self._getters = {}
        self._data_keys = kwargs

    def register_getter(self, key, getter):
        """ Take a type key and associate a getter with it internally.

        Args:
            type_key (str): The type of element for the getter to be assigned
                to get.
            getter (type varies): a callable function or object to get the
                value stored by that type of element.
        
        Returns:
            None.
        """
        self._getters[key] = getter

    def _is_active(self, data_to_search, activator_name, value_for_comparison):
        """ Determine whether the given activator has the specified value.
        
        Recursively loop through the data structure and try to find a
        parameter matching the required "activator" and compare its
        value with the given "value_for_comparison".

        Args:
            data_to_search (list): List of dicts as produced by
                GUIFactory.create().
                A list of all data stored in element data dicts as those
                stored under config_data_key by builders.
            activator_name (str): The parameter name of a paremeter to check
                for a value matching value_for_comparison
        
        Returns:
            bool
        """
        objects_key = self._data_keys["objects_key"]
        config_data_key = self._data_keys["config_data_key"]
        children_key = self._data_keys["children_key"]
        properties_key = self._data_keys["properties_key"]
        type_key = self._data_keys["type_key"]
        parameter_name_key = self._data_keys["parameter_name_key"]
        parameter_key = self._data_keys["parameter_key"]


        for potential_activator_element in data_to_search:
            element_properties = potential_activator_element[
                config_data_key][properties_key]
                
            element_objects = potential_activator_element[objects_key]

            if element_properties[parameter_name_key] == activator_name:
                potential_activator_type = potential_activator_element[
                    config_data_key][type_key]

                activator_getter = self._getters.get(potential_activator_type)
                if not activator_getter:
                    activator_getter = self._getters["NoneType"]

                potential_activator = element_objects[parameter_key]

                if (activator_getter(potential_activator) ==
                    value_for_comparison):
                    return True
                return False

            element_children = potential_activator_element[
                config_data_key][children_key]

            if self._is_active(element_children,
                               activator_name,
                               value_for_comparison):
                return True

        return False

    def _get_variable_value(self, target_element, getter_method,
                            output_container):

        objects_key = self._data_keys["objects_key"]
        config_data_key = self._data_keys["config_data_key"]
        properties_key = self._data_keys["properties_key"]
        parameter_name_key = self._data_keys["parameter_name_key"]
        parameter_key = self._data_keys["parameter_key"]

        parameter_name = target_element[config_data_key][properties_key].get(
            parameter_name_key)
        # Call the getter on the parameter of this element.
        parameter_value = getter_method(
            target_element[objects_key][parameter_key])
        # Make sure it's not a literal bool, and that its name isn't None.
        if not ((parameter_value is True) or (parameter_value is False)
                or (not parameter_name)):
            output_container[parameter_name] = parameter_value

        return output_container

    def _check_status_and_read_datum(self, data_element, all_data,
                                     output_data_container, read_all=False,
                                     **kwargs):

        config_data_key = self._data_keys["config_data_key"]
        properties_key = self._data_keys["properties_key"]
        type_key = self._data_keys["type_key"]
        activator_key = self._data_keys["activator_key"]
        required_value_key = self._data_keys["required_value_key"]
        element_type = data_element[config_data_key][type_key]
        element_properties = data_element[config_data_key][properties_key]

        getter = self._getters.get(element_type)
        if not getter:
            getter = self._getters.get("NoneType")

        # Only read out the data from an element if its parameter is "active."
        parameter_is_active = self._is_active(
            data_to_search=all_data,
            activator_name=element_properties[activator_key],
            value_for_comparison=element_properties[required_value_key])

        if parameter_is_active or read_all:
            output_data_container = self._get_variable_value(
                target_element=data_element,
                getter_method=getter,
                output_container=output_data_container)

        return output_data_container

    def read(self, data_to_read, all_data=[], output_data_container={},
             read_all=False, **kwargs):
        """ Obtain a dict or OrderedDict of all data stored in the layout.

        This is a recursive function like the GUIFactory.create() method.
        It operates on the output GUIFactory.create().

        Args:
            data_to_read (list): List of dicts as produced by
                GUIFactory.create().
                A list of all data stored in element data dicts as those
                stored under config_data_key by builders. The data to be
                scanned for retrievable values. Possibly a subset of all_data.
            all_data (list): Same type as data_to_read, but possibly a
                superset.
            output_data_container (associative, subscriptable container)
            read_all (bool): Whether or not to return all parameter values in
                data_to_read, or just those that are active as specified by
                their activator having the required_value or not.

        Returns:
            output_data_container (associative, subscriptable container): Data
                read from layout elements.
        """

        if len(all_data) == 0:
            all_data = data_to_read

        config_data_key = self._data_keys["config_data_key"]
        children_key = self._data_keys["children_key"]

        # Loop through each element of the data structure at every level of the parent-child heirarchy.
        for data_element in data_to_read:
            output_data_container = self._check_status_and_read_datum(
                data_element=data_element,
                all_data=all_data,
                read_all=read_all,
                output_data_container=output_data_container,
                **kwargs)

            child_element_data = data_element[config_data_key][children_key]
            self.read(data_to_read=child_element_data, all_data=all_data,
                      output_data_container=output_data_container, read_all=read_all, **kwargs)

        return output_data_container


class DummyManager:
    """ This is a base class for all the GUI managers that manipulate it.
    
    Manager classes are lower level classes for the post-set-up administrative
    functions of the GUI (e.g., re-configuring elements, hiding/showing).
    They deal directly with tkinter ojbects and methods. If necessary, they
    may be re-written to manage a GUI using a different library, but
    hopefully retain the same interface (type of input parameters and output
    data).
    """

    def __init__(self):
        """ Initialize a DummyManager and its name

        """

        self._name = "DummyManager"

    def __call__(self, **kwargs):
        self._callback(**kwargs)

    def _callback(self, level=0, **kwargs):
        print(level * "    ", f"Calling {self._name} on arguments:")
        for kw in kwargs:
            print(level * "    ", f"{kw} is {kwargs[kw]}")

    def _find_element_from_name(self, GUI_elements, name, config_data_key,
                                children_key, name_key):
        """ Find an element from its name.

        Args:
            GUI_elements (list): List of dicts as produced by
                GUIFactory.create().
                A list of all data stored in element data dicts as those
                stored under config_data_key by builders.
            name (str)
            config_data_key (str): String key used to access config data in
                the data structures returned GUI_elements.
            children_key (str): String key used to access list of children
                elements in config_data returned GUI_elements.
            name_key (str): String key used to access element names in config
                data in GUI_elements.
        
        Returns:
            (dict): Data of element to find and return.

        """

        for element in GUI_elements:
            if element[config_data_key][name_key] == name:
                return element
            child_element = self._find_element_from_name(
                GUI_elements=element[config_data_key][children_key],
                name=name,
                config_data_key=config_data_key,
                children_key=children_key,
                name_key=name_key)

            if child_element != None:
                return child_element


class RunManager(DummyManager):
    """ This is a manager runs the GUI by starting the event loop.
    
    It is necessarily called at the start of any GUI program.
    """
    def __init__(self):
        """ Initialize the mangar with a class-wide name
        """
        self._name = "RunManager"

    def __call__(self, GUI_data, objects_key, widget_key, **kwargs):
        """ Assuming all elements of GUI_data are top-level, run them.

        Args:
            GUI_data (list):  List of dicts as produced by
                GUIFactory.create().
                A list of all data stored in element data dicts as those
                stored under config_data_key by builders.
            objects_key (str): Key used to access tkinter objects generated by
                builders and stored in GUI_data.
            widget_key (str): Key used to access tkinter widgets instantiated
                by GUIFactory.create().
            
        """

        for window in GUI_data:
            window.get(objects_key).get(widget_key).mainloop()


class StyleManager(DummyManager):
    """ This is a manager styles the GUI by calling tkinter styles.
    
    It is possibly redundant given the potential of GUIFactory().create()
    builders to style widgets at instantiation.
    """
    def __init__(self):
        """ Initialize a StyleManager with a class-wide name
        """
        self._name = "StyleManager"

    def __call__(self, style_data, **kwargs):
        """ Make the labels, buttons, and other elements look nicer.

        Args:
            style_data (tuple): 4-tuple containing the entry box
                character width, str specifying font type and size and bold or
                unbold (normal), horizontal external padding for each element,
                and vertical padding.
            **kwargs: Ignored parameters

        Returns:
            None
        """

        style = ttk.Style()
        font_type_size = style_data[1]

        style.configure("TLabel", font=font_type_size)
        style.configure("TCombobox", font=font_type_size)
        style.configure("TButton", font=font_type_size)
        style.configure("TNotebook.Tab", font=font_type_size)


class EditContentManager(DummyManager):
    """ This is a manager edits the contents of dynamic fields in the GUI.
    
    This should possibly be re-written as another factory-method class.
    It currently works for ttk.Entry and Text only.
    """
    def __init__(self):
        """ Initialize a EditContentManager with a class-wide name
        """
        self._name = "EditContentManager"

    def _check_entry_text(self, element_widget):
        """ Determine whether the element is a entry or text_box.
        
        Args:
            element_widget: Tk Text or ttk.Entry object, hopefully.

        Returns:
            bool
        """
        return ((isinstance(element_widget, ttk.Entry))
                or (isinstance(element_widget, Text)))

    def __call__(self, GUI_elements, name, config_data_key, children_key,
                 name_key, objects_key, widget_key, action="insert", index=0,
                 content="0", **kwargs):
        """ Edit the contents of the given dynamic field as directed.

        Callable function called when manager is followed by parentheses.

        Args:
            GUI_elements (list): List of dicts as produced by
                GUIFactory.create().
            name (str): Name of element to edit contents of.
            children_key (str): String key used to access list of children
                elements in config_data returned GUI_elements.
            name_key (str): String key used to access element names in config
                data in GUI_elements.
            objects_key (str): Key used to access tkinter objects generated by
                builders and stored in GUI_data.
            widget_key (str): Key used to access tkinter widgets instantiated
                by GUIFactory.create().
            action (str): Identifier of type of edit to perform. Either
                "insert" or "replace_all"
            index (int or double or string): Integer index (0 to however many
                characters wide the entry field is) in single-line entry to
                insert at or line-character index in text_box element to
                insert at.
                The lines of text_box are numbered from top (1) to bottom.
                "end" may be used to specify the very end of the text.
            content (str): Whatever you want to insert.
            **kwargs: Ignored parameters.
        
        Returns:
            None

        Raises:
            ValueError: If GUI_element is neither entry nor text_box.
        """
        entry_data = self._find_element_from_name(
            GUI_elements=GUI_elements, name=name,
            config_data_key=config_data_key, children_key=children_key,
            name_key=name_key)

        entry_widget = entry_data[objects_key][widget_key]

        if isinstance(entry_widget, ttk.Frame):
            for widget in entry_widget.grid_slaves():
                if self._check_entry_text(widget):
                    entry_widget = widget

        if self._check_entry_text(entry_widget):
            self._insert_or_replace_content(
                action=action, index=index, widget=entry_widget,
                content=content)
        else:
            raise ValueError(
                "The element is of incorrect type (not an entry or text_box)")

    def _insert_or_replace_content(self, action, index, widget, content):
        if action == "replace_all":
            try:
                widget.delete(0, "end")
            except:
                widget.delete(1.0, "end")

        try:
            widget.insert(index, content)
        except:
            widget.insert(1.0, content)


class EntryDefaultsManager(DummyManager):
    """ Class to manage the default values of all entry elements.
    """

    def __init__(self):
        self._name = "EntryDefaultsManager"

    def __call__(self, GUI_elements, parameter_values, config_data_key,
                 children_key, **kwargs):
        """ Set the defaults of all entry elements equal to current values.
        
        Recursively loop through GUI_elements finding and setting defaults
        for entry widgets.

        Args:
            GUI_elements (list): List of dicts as produced by
                GUIFactory.create().
            parameter_values (associative, subscriptable container): Element
                parameters' current values by their names.
            config_data_key (str): String key used to access config data in
                the data structures returned GUI_elements.
            children_key (str): String key used to access list of children
                elements in config_data returned GUI_elements.
            **kwargs: Ignored parameters.
        
        Returns:
            None

        """
            
        for element in GUI_elements:
            self._set_default(element_data=element,
                              parameter_values=parameter_values,
                              config_data_key=config_data_key, **kwargs)

            children_data = element[config_data_key][children_key]
            self.__call__(GUI_elements=children_data,
                          parameter_values=parameter_values,
                          config_data_key=config_data_key,
                          children_key=children_key, **kwargs)

    def _set_default(self, element_data, parameter_values, config_data_key,
                     type_key, properties_key, default_value_key,
                     parameter_name_key, **kwargs):
        if element_data[config_data_key][type_key] != "entry":
            return

        element_properties = element_data[config_data_key][properties_key]

        parameter_name = element_properties.get(parameter_name_key)
        if not parameter_name is None:
            parameter_value = parameter_values[parameter_name]
            element_properties[default_value_key] = parameter_value


class DropDownDefaultsManager(EntryDefaultsManager):
    """ Class to manage the default values of all drop-down elements.

    Inherits from EntryDefaultsManager, so has the same __call__() method.
    """
    def __init__(self):
        self._name = "DropDownDefaultsManager"

    def _set_default(self, element_data, parameter_values, config_data_key,
                     type_key, properties_key, default_option_key,
                     parameter_name_key, **kwargs):
        if element_data[config_data_key][type_key] != "drop_down":
            return

        element_properties = element_data[config_data_key][properties_key]

        parameter_name = element_properties.get(parameter_name_key)
        if not parameter_name is None:
            parameter_value = parameter_values[parameter_name]
            element_properties[default_option_key] = parameter_value


class TextDefaultsManager(EntryDefaultsManager):
    """ Class to manage the default values of all text_box elements.

    Inherits from EntryDefaultsManager, so has the same __call__() method.
    """

    def __init__(self):
        self._name = "TextDefaultsManager"

    def _set_default(self, element_data, parameter_values, config_data_key,
                     type_key, properties_key, default_text_key,
                     parameter_name_key, **kwargs):
        if element_data[config_data_key][type_key] != "text_box":
            return

        element_properties = element_data[config_data_key][properties_key]

        parameter_name = element_properties.get(parameter_name_key)
        if not parameter_name is None:
            parameter_value = parameter_values[parameter_name]
            element_properties[default_text_key] = parameter_value


class HideShowManager(DummyManager):
    """ Class to manage the visiblity of all grid-placed elements.

    Inherits from EntryDefaultsManager, so has the same __call__() method.
    """
    def __init__(self):
        self._name = "QuitManager"

    def __call__(self, GUI_elements, name, config_data_key, children_key,
                 properties_key, name_key, visible_key, objects_key,
                 widget_key, **kwargs):
        """ Find the named element, and hide it if visible, or show it if not.

        Args:
            GUI_elements (list): List of dicts as produced by
                GUIFactory.create().
            config_data_key (str): String key used to access config data in
                the data structures returned GUI_elements.
            children_key (str): String key used to access list of children
                elements in config_data returned GUI_elements.
            properties_key (str): String key used to access dict of
                config_data element properties.
            name_key (str): String key used to access element names in config
                data in GUI_elements.
            visible_key (str): String key used to access element visiblity.
            objects_key (str): Key used to access tkinter objects generated by
                builders and stored in GUI_data.
            widget_key (str): Key used to access tkinter widgets instantiated
                by GUIFactory.create().
            **kwargs: Ignored parameters.
        
        Returns:
            None
        """

        widget_data = self._find_element_from_name(
            GUI_elements=GUI_elements,
            name=name,
            config_data_key=config_data_key,
            children_key=children_key,
            name_key=name_key)
        
        widget_object = widget_data[objects_key][widget_key]

        is_visible = widget_data[config_data_key][properties_key][visible_key]

        if is_visible:
            widget_object.grid_remove()
            widget_data[config_data_key][properties_key][visible_key] = False
        else:
            widget_object.grid()
            widget_data[config_data_key][properties_key][visible_key] = True

        for window in GUI_elements:
            window[objects_key][widget_key].update_idletasks()
        return


class QuitManager(DummyManager):
    """ This is a class to close the windows in the layout
    """

    def __init__(self):
        self._name = "QuitManager"

    def __call__(self, GUI_elements, objects_key, widget_key, **kwargs):
        """ Loop through GUI_elements and call the method to destroy them.
        """

        for window in GUI_elements:
            window[objects_key][widget_key].destroy()
        return


class GUIAdmin:
    """ This is a class to handle the management of layout after it's built.
    
    One of its responsibilities is to pass the keys used by the mangers
    to access the element data.
    """

    def __init__(self, **kwargs):
        self._managers = {}
        self._data_keys = kwargs

    def register_manager(self, duty_key, manager):
        """ Take a duty_key and associate a manager with it internally.

        Args:
            duty_key (str): The type of duty for the manager to be
                assigned to handle.
            manager (type varies): a callable function or object to manage
                that type of duty.
        
        Returns:
            None.
        """
        self._managers[duty_key] = manager

    def administrate(self, duty_key, admin_params={"arg": None}):
        """ Find the requested duty's manager and execute that job.

        Args:
            duty_key (str): Key unique to a manager.
            admin_params (dict): All the data that manager needs to do
                its job other than data keys.

        Returns:
            varies by manager. Returns the result of calling that manager.
        """
        try:
            manager = self._managers[duty_key]
        except KeyError:
            manager = self._managers["other"]

        return manager(**self._data_keys, **admin_params)


class GenericPopUp:
    """ This is a base class for all the GUI pop-up activators.

    Pop-up classes are lower level classes for the activation of dialogs
    between the user and the GUI. They deal directly with tkinter ojbects
    and methods. If necessary, they may be re-written to work with a GUI
    from a different library, but hopefully retain the same interface
    (type of input parameters and output data).
    """
    def __init__(self):
        self._name = "GenericPopUp"

    def __call__(self, title, message, **kwargs):
        """ Display a dialog requesting the user to click "Ok" or "Cancel"

        Args:
            title (str): Dialog window's title.
            message (str): What to show in the dialog.
        
        Return:
            bool: True if the user clicked "Ok", False otherwise.
        """

        ok_or_not = messagebox.askokcancel(title=title, message=message)
        return ok_or_not


class YesNoPopUp(GenericPopUp):
    """ This is a class to ask the user "Yes" or "No" to some prompt.

    It inherits from GenericPopUp.
    """
    def __init__(self):
        self._name = "YesNoPopUp"

    def __call__(self, title, message, **kwargs):
        """ Display a dialog requesting the user to click "Yes" or "No".

        Args:
            title (str): Dialog window's title.
            message (str): What to show in the dialog.
        
        Return:
            bool: True if the user clicked "Yes", False otherwise.
        """
        
        yes_or_no = messagebox.askyesno(title=title, message=message)
        return yes_or_no


class YesNoCancelPopUp(GenericPopUp):
    """ This is a class to ask the user to agree or disagree/cancel.

    It inherits from GenericPopUp.
    """
    def __init__(self):
        self._name = "YesNoCancelPopUp"

    def __call__(self, title, message, **kwargs):
        """ Display a dialog requesting the user to agree/disagree.

        Args:
            title (str): Dialog window's title.
            message (str): What to show in the dialog.
        
        Return:
            bool: True if the user clicked "Yes", False if "No" and
            None otherwise.
        """
        yes_or_no = messagebox.askyesnocancel(title=title, message=message)
        return yes_or_no


class FileOpenPopUp(GenericPopUp):
    """ This is a class to ask the user to select a file to open.

    It inherits from GenericPopUp. It uses the system file manager.
    """
    def __init__(self):
        self._name = "FileOpenPopup"

    def __call__(self, title="Open", initial_path="./",
                 file_types_extensions=[("All files", "*.*", "TEXT")],
                 **kwargs):
        """ Display a dialog requesting the user to choose a file.

        Args:
            title (str): Dialog window's title.
            initial_path (str): Relative or absolute path to start file
                manager in.
            file_types_extensions (list): List of tuples that contain
                strings. The first string is the text to display next
                to a certain type of suggested file, such as "All files",
                "JSON files", or "Text files". The remaining strings are the
                types of extensions to search for and show. One of these may
                be "TEXT" to tell the dialog to show files that have no
                extension.
            **kwargs: Ignored parameters.
        
        Return:
            filepath (str): if the user clicked "Open", the abosolute path
            to the selected file. If no file was selected or the User clicked
            "Cancel" the string is empty.
        """
        filepath = filedialog.askopenfilename(
            title=title, initialdir=initial_path,
            filetype=file_types_extensions)
        return filepath


class FileSaveAsPopUp(GenericPopUp):
    """ This is a class to ask the user to select a file to open.

    It inherits from GenericPopUp. It uses the system file manager.
    """
    def __init__(self):
        self._name = "FileSaveAsPopup"

    def __call__(self, title="Save As", initial_path="./",
                 file_types_extensions=[("All files", "*.*", "TEXT")],
                 **kwargs):
        """ Display a dialog requesting the user to choose a file.

        Args:
            title (str): Dialog window's title.
            initial_path (str): Relative or absolute path to start file
                manager in.
            file_types_extensions (list): List of tuples that contain
                strings. The first string is the text to display next
                to a certain type of suggested file, such as "All files",
                "JSON files", or "Text files". The remaining strings are the
                types of extensions to search for and show. One of these may
                be "TEXT" to tell the dialog to show files that have no
                extension.
            **kwargs: Ignored parameters.
        
        Return:
            filepath (str): if the user clicked "Save", the abosolute path
            to the selected file. If no file was selected or the User clicked
            "Cancel" the string is empty.
        """
        filepath = filedialog.asksaveasfilename(
            title=title, initialdir=initial_path,
            filetype=file_types_extensions)
        return filepath


class GUIPopupHeadquarters:
    """ This is a class to open pop-up dialogs.

    It is an upper level class like GUIFactory or GUIReader.
    """
    def __init__(self):
        self._pop_ups = {}

    def register_popup(self, pop_up_type, pop_up):
        """ Take a pop_up_type and associate a PopUp callable with it.

        Args:
            pop_up_type (str): The type of pop-up dialog for the PopUp to be
                assigned to handle.
            pop_up (type varies): a callable function or object to manage
                that type of pop_up.
        
        Returns:
            None.
        """
        self._pop_ups[pop_up_type] = pop_up

    def dialog(self, pop_up_type, pop_up_params):
        """ Initiate a pop-up dialog of the specified type, with params

        Args:
            pop_up_type (str): Type of pop-up dialog to initiate.
            pop_up_params (dict): All named parameters for the pop up to use.

        Return:
            varies by pop-up: Could be bool from query pop-ups or string
                filepath from file dialogs.
        """

        try:
            pop_up = self._pop_ups[pop_up_type]
        except KeyError:
            raise ValueError("Invalid pop-up type")

        dialog_result = pop_up(**pop_up_params)

        return dialog_result


class GUI:
    """ This class uses the other classes in this module to build a GUI.

    It takes the type of data stored in GUIData(). It builds the GUI, reads
    the values, and saves and opens other configurations internally.
    The other opened configurations can have the same functionality.

    """

    def __init__(self, *, builder_keys, GUI_config_data, GUI_action_mapping,
                 GUI_builder_mapping, GUI_binder_mapping, GUI_getter_mapping,
                 GUI_manager_mapping, GUI_pop_up_mapping):
        """ Take required data and build a GUI using the suipy classes.
        
        Args:
            builder_keys (dict): All the keys used by the builders and other
                classes to access GUI element data.
            GUI_config_data (dict): All the initialization config data
            GUI_action_mapping (dict): Associates each callable function used
                in the GUI with a string key to identify it to the
                GUIFactory()
            GUI_builder_mapping (dict): Associates each element type with a
                builder.
            GUI_binder_mapping (dict): Associates each event type with a
                binder.
            GUI_getter_data (dict): Associates each element type with a
                value getter.
            GUI_manager_mapping (dict): Associates each duty with a manager
            GUI_pop_up_mapping (dict): Associates each dialog type with a
                PopUp class or function.
        
        """

        data = GUI_config_data

        # For use by self.get_current_config_data():
        self._builder_keys = builder_keys

        self._GUI_factory = GUIFactory(**builder_keys)
        
        # Resgister builders in the factory.
        for element_type in GUI_builder_mapping:
            self._GUI_factory.register_builder(element_type,
                                               GUI_builder_mapping[element_type])

        self._default_aesthetics = (
            self._GUI_factory.get_builder_aesthetic_defaults())

        self._elements = self._GUI_factory.create(
            configuration_data=data,
            action_mapping=GUI_action_mapping,
            inventory_list=[])

        self._GUI_reader = GUIReader(**builder_keys)

        # Register getters for the data.
        for variable_type in GUI_getter_mapping:
            self._GUI_reader.register_getter(variable_type,
                                             GUI_getter_mapping[variable_type])
        
        self._GUI_function_workshop = GUIFunctionWorkshop(**builder_keys)

        self._GUI_administration = GUIAdmin(**builder_keys)
        # Register managers for the widgets.
        for manager_role in GUI_manager_mapping:
            self._GUI_administration.register_manager(
                duty_key=manager_role,
                manager=GUI_manager_mapping[manager_role])

        self._GUI_pop_up_hq = GUIPopupHeadquarters()
        for pop_up_type in GUI_pop_up_mapping:
            self._GUI_pop_up_hq.register_popup(
                pop_up_type=pop_up_type,
                pop_up=GUI_pop_up_mapping[pop_up_type])

    def style_elements(self, style_specs=None):
        if not style_specs:
            style_specs = self._default_aesthetics

        self._GUI_administration.administrate(
            duty_key="style",
            admin_params={"style_data": style_specs})

    def get_elements(self):
        return self._elements

    def _remove_all_except_key_onelevel(self, data={}, key=None):
        keys = [k for k in data]
        
        for k in keys:
            if k != key:
                data.pop(k)

    def _copy_config_data_except_children(self, built_data):
        built_config_data = built_data[self._builder_keys["config_data_key"]]
        
        config_data_element = {}

        for category in built_config_data:
            if category != self._builder_keys["children_key"]:
                config_data_element[category] = built_config_data[category]
            else:
                config_data_element[self._builder_keys["children_key"]] = []

        return config_data_element

    def _call_copier_on_data(self, container, data_to_copy):
        for element_data in data_to_copy:
            config_data_element = self._copy_config_data_except_children(
                element_data)

            container.append(config_data_element)

            children_list = config_data_element[
                self._builder_keys["children_key"]]
            
            child_data_to_copy = element_data[
                self._builder_keys["config_data_key"]][
                    self._builder_keys["children_key"]]

            self._call_copier_on_data(
                container=children_list,
                data_to_copy=child_data_to_copy)
        
        return container

    def get_current_config_data(self):
        all_config_data = self._call_copier_on_data(
            container=[],
            data_to_copy=self._elements)
        return all_config_data
    
    def set_entry_defaults(self):
        self._GUI_administration.administrate(
            duty_key="set_entry_defaults",
            admin_params={"GUI_elements": self._elements,
                "parameter_values": self.get_parameter_values(
                    get_all_parameters=True)})
    
    def set_drop_down_defaults(self):
        self._GUI_administration.administrate(
            duty_key="set_drop_down_defaults",
            admin_params={
                "GUI_elements": self._elements,
                "parameter_values": self.get_parameter_values(
                    get_all_parameters=True)})

    def set_text_entry_defaults(self):
        self._GUI_administration.administrate(
            duty_key="set_text_box_defaults",
            admin_params={
                "GUI_elements": self._elements,
                "parameter_values": self.get_parameter_values(
                    get_all_parameters=True)})
    
    def get_parameter_values(self, get_all_parameters=False):
        values = OrderedDict()
        return self._GUI_reader.read(
            data_to_read=self._elements,
            output_data_container=values,
            read_all=get_all_parameters)

    def insert_content(self, *, element_name, index_to_insert_at=0,
                       content="Some content"):
        self._GUI_administration.administrate(
            duty_key="content_edit",
            admin_params={
                "GUI_elements": self._elements,
                "name": element_name,
                "index": index_to_insert_at,
                "content": content})

    def replace_contents_with_content(self, *, element_name, index_to_insert_at=0,
                                      content="Some content"):
        self._GUI_administration.administrate(
            duty_key="content_edit",
            admin_params={
                "GUI_elements": self._elements,
                "name": element_name,
                "action": "replace_all",
                "index": index_to_insert_at,
                "content": content})

    def ask_user_yes_or_no(
        self,
        title_text="Query",
        message_text="Please click Yes to continue, or click No to go back"):

        return self._GUI_pop_up_hq.dialog(
            pop_up_type="yes_no",
            pop_up_params={"title": title_text, "message": message_text})

    def ask_user_file_open(
        self,
        title_text="Open",
        file_types_and_extensions=[("All files", "*.*", "TEXT")],
        initial_search_directory="./"):

        return self._GUI_pop_up_hq.dialog(
            pop_up_type="file_open",
            pop_up_params={
                "title": title_text,
                "file_types_extensions": file_types_and_extensions,
                "initial_path": initial_search_directory})

    def ask_user_file_save_as(
        self,
        title_text="Save As",
        file_types_and_extensions=[("All files", "*.*", "TEXT")],
        initial_search_directory="./"):

        return self._GUI_pop_up_hq.dialog(
            pop_up_type="file_save_as",
            pop_up_params={
                "title": title_text,
                "file_types_extensions": file_types_and_extensions,
                "initial_path": initial_search_directory})

    def hide_or_show(self, element_name):
        self._GUI_administration.administrate(
            duty_key="hide_show",
            admin_params={
                "GUI_elements": self._elements,
                "name": element_name})

    def read_in_config_json(self, filename, file_encoding="utf8"):
        with open(filename, "r", encoding=file_encoding) as config_file:
            raw_data = config_file.read()

            read_data = json.loads(raw_data)

            return read_data

    def write_out_current_config_json(self, filename, file_encoding="utf8"):
        with open(filename, "w", encoding=file_encoding) as config_file:
            configuration_data = self.get_current_config_data()
            data_to_write = {
                "configuration_data": configuration_data,
                "builder_keys": self._builder_keys}

            formatted_data = json.dumps(data_to_write, indent=4)

            config_file.write(formatted_data)

    def generate_elements(self, config_data, action_mapping):
        self._elements = self._GUI_factory.create(
            configuration_data=config_data,
            action_mapping=action_mapping,
            inventory_list=[])

    def open(self):
        self._GUI_administration.administrate(
            duty_key="start_event_loop",
            admin_params={"GUI_data": self._elements})
    
    def quit(self):
        quit_confirmed = self.ask_user_yes_or_no(
            title_text="Exit?", message_text="Are you sure you want to exit?")
        if quit_confirmed:
            self._GUI_administration.administrate(
                duty_key="quit_close",
                admin_params={"GUI_elements": self._elements})
        
        return quit_confirmed
