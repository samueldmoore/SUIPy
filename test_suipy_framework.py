# -*- coding: utf-8 -*-
""" Tests for the SUIPy framework implemented using a variety of strategies.

First, the intermediate-level classes such as the GUI are to be tested using a
logic criteria like correlated active clause coverage.

"""

import suipy_framework, pytest

# ============================================================================
# Hard-coded test fixture key-class mappings to avoid file I/O

BUILDERS = {
    "NoneType": suipy_framework.GenericBuilder(),
    "window": suipy_framework.WindowBuilder(),
    "menu_bar": suipy_framework.MenuBarBuilder(),
    "drop_down_menu": suipy_framework.DropDownMenuBuilder(),
    "menu_command": suipy_framework.MenuCommandBuilder(),
    "frame": suipy_framework.FrameBuilder(),
    "tab_binder": suipy_framework.TabBinderBuilder(), 
    "tab": suipy_framework.TabBuilder(),
    "text_line": suipy_framework.TextLineBuilder(),
    "text_box": suipy_framework.TextEntryBoxBuilder(),
    "entry": suipy_framework.ValueEntryBuilder(),
    "drop_down": suipy_framework.DropDownBuilder(),
    "button": suipy_framework.ButtonBuilder()
}

GETTERS = {
    "NoneType": suipy_framework.NoneGetter(),
    "entry": suipy_framework.StringVarGetter(),
    "drop_down": suipy_framework.StringVarGetter(),
    "text_box": suipy_framework.TextGetter(),
    "window": suipy_framework.LiteralGetter()
}

BINDERS = {
    "NoneType": suipy_framework.GenericBinder(),
    "button_press": suipy_framework.CommandBinder(),
    "window_close": suipy_framework.ExitButtonBinder()
}

MANAGERS = {
    "other": suipy_framework.DummyManager(),
    "start_event_loop": suipy_framework.RunManager(),
    "style": suipy_framework.StyleManager(),
    "content_edit": suipy_framework.EditContentManager(),
    "quit_close": suipy_framework.QuitManager(),
    "hide_show": suipy_framework.HideShowManager(),
    "set_entry_defaults": suipy_framework.EntryDefaultsManager(),
    "set_drop_down_defaults": suipy_framework.DropDownDefaultsManager(),
    "set_text_box_defaults": suipy_framework.TextDefaultsManager()
    }

POPUPS = {
    "other": suipy_framework.GenericPopUp(),
    "ok_cancel": suipy_framework.GenericPopUp(),
    "yes_no": suipy_framework.YesNoPopUp(),
    "yes_no_cancel": suipy_framework.YesNoCancelPopUp(),
    "file_open": suipy_framework.FileOpenPopUp(),
    "file_save_as": suipy_framework.FileSaveAsPopUp()
}

# Keys used by builders and other classes to access configuration data
KEYS = {
    "config_data_key": "config_data",
    "name_key": "name",
    "type_key": "type",
    "properties_key": "properties",
    "objects_key": "objects",
    "children_key": "children",
    "column_key": "column",
    "on_new_row_key": "on_new_row",
    "parameter_type_key": "parameter_type",
    "parameter_name_key": "parameter_name",
    "parameter_key": "parameter",
    "activator_key": "activator",
    "action_key": "action",
    "required_value_key": "required_value",
    "event_type_key": "event_type",
    "justification_key": "justification",
    "size_and_position_key": "size_and_position",
    "visible_text_key": "visible_text",
    "width_key": "width",
    "height_key": "height",
    "default_text_key": "default_text",
    "has_scrollbar_key": "has_scrollbar",
    "options_key": "options",
    "default_option_key": "default_option",
    "only_selectable_key": "only_selectable",
    "widget_key": "widget",
    "visible_key": "visible",
}
# ============================================================================

SIMPLE_LAYOUT = [{
    "type": "window",
    "name": "window 1",
    "children": [
        {
            "type": "text_line",
            "name": "text_line 1",
            "children": [],
            "properties": {"visible_text": "Some text"}
            }
        ],
    "properties": {}
    }]

SIMPLE_ACTIONS = {
    "exit": None
}


def test_initialization():

    gui = suipy_framework.GUI(
        builder_keys=KEYS,
        GUI_config_data=SIMPLE_LAYOUT,
        GUI_builder_mapping=BUILDERS,
        GUI_binder_mapping=BINDERS,
        GUI_getter_mapping=GETTERS,
        GUI_pop_up_mapping=POPUPS,
        GUI_manager_mapping=MANAGERS,
        GUI_action_mapping=SIMPLE_ACTIONS
        )

    #gui.open()

#==============================================================================
# Logic Coverage Test Requirements and Tests
#------------------------------------------------------------------------------
# GUIFactory
#------------------------------------------------------------------------------

# For the __init__ method in suipy_framework.GUIFactory, there is no explicit
# conditional logic, so only one test case is needed to exercise all the
# possibilities. This doesn't really test anything since the passed-in KEYS are
# not directly retrievable.
def test_GUIFactory___init__():
    suipy_framework.GUIFactory(**KEYS)

# GUIFactory.register_builder
#
# There is also no explicit conditional logic, just a key-value assignment.
# Only one test seems needed.
def test_GUIFactory_register_builder():
    suipy_framework.GUIFactory(**KEYS).register_builder(
        "window", BUILDERS["window"])

@pytest.fixture(params=[
    (False, 0, 0),
    (True, 1, 0),
    ("False", 0, 0),
    ("True", 1, 0),
    ("No", 0, 0),
    ("Yes", 1, 0)])
def config_GUIFactory_locate_element(request):
    """Set up a simple widget layout to test the _locate_element function with.

    :param request:
        object from fixture allowing access to fixture param for this run
    :return:
        tuple containing
            [0] the layout customized by whether the widget's on a new row or
            not
            [1] the bool telling if the widget's on a new row
            [2] the row number to expect
            [3] the column number to expect
    """
    layout = {
        KEYS["type_key"]: "text_line",
        KEYS["name_key"]: "test_text",
        KEYS["children_key"]: [],
        KEYS["properties_key"]: {
            KEYS["on_new_row_key"]: request.param[0]
        }}
    # Use the param for this run to customize the layout (new row or not)

    return (layout, request.param[0], request.param[1], request.param[2])

# GUIFactory._locate_element
#
# The following is an analysis of the if-else conditional, showing the needed
# clause values to make the denoted "active clause" the determining one in
# control of the entire predicate, where the determining clause is marked with
# an asterick *
#    _________________________________________________________________
#    | (new_row == "True") | (new_row == True) | (new_row == "True") |
#    |        True*        |       False       |        False        |
#    |        False*       |       False       |        False        |
#    |        False        |       True*       |        False        |
#    |        False        |       False*      |        False        |
#    |        False        |       False       |        True*        |
#    |        False        |       False       |        False*       |
#    |_____________________|___________________|_____________________|
def test_GUIFactory_locate_element(config_GUIFactory_locate_element):
    actual = suipy_framework.GUIFactory(**KEYS)._locate_element(
        config_GUIFactory_locate_element[0])
    expected = (
        config_GUIFactory_locate_element[1],
        config_GUIFactory_locate_element[2],
        config_GUIFactory_locate_element[3])

    assert actual == expected
