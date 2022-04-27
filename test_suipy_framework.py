# -*- coding: utf-8 -*-
""" Tests for the SUIPy framework implemented using a variety of strategies.

First, the intermediate-level classes such as the GUI are to be tested using a
logic criteria like correlated active clause coverage.

"""

import tkinter
import suipy_framework, pytest, unittest.mock, random

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
    "default_value_key": "default_value",
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
    "exit": None,
    "test_callback": lambda: print("Test callback print")
}

MOCK_TYPE = "mock_type"
# This made-up type is used in config_GUIFactory_build_element.

CHAR_CODE_RANGE = (0, 1114111)

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
# Tests for GUIFactory
#------------------------------------------------------------------------------

def get_GUIFactory_fixture():
    return suipy_framework.GUIFactory(**KEYS)

# For the __init__ method in suipy_framework.GUIFactory, there is no explicit
# conditional logic, so only one test case is needed to exercise all the
# possibilities. This doesn't really test anything since the passed-in KEYS are
# not directly retrievable.
def test_GUIFactory___init__():
    get_GUIFactory_fixture()

# GUIFactory.register_builder
#
# There is also no explicit conditional logic, just a key-value assignment.
# Only one test seems needed.
def test_GUIFactory_register_builder():
    get_GUIFactory_fixture().register_builder(
        "window", BUILDERS["window"])

# GUIFactory._locate_element
#
# The following is an analysis of the if-else conditional, showing the needed
# clause values to make the denoted "active clause" the determining one in
# control of the entire predicate, where the determining clause is marked with
# an asterick *
#
#          1: Test requirements for GUIFactory._locate_element
#________________________________________________________________________
#  TR  | (new_row == True) | (new_row == "True") | (new_row == "Yes")  |
# 1.01 |         T*        |         F           |          F          |
# 1.02 |         F*        |         F           |          F          |
# 1.03 |         F         |         T*          |          F          |
# 1.04 |         F         |         F*          |          F          |
# 1.05 |         F         |         F           |          T*         |
# 1.06 |         F         |         F           |          F*         |
#      |___________________|_____________________|_____________________|
@pytest.fixture(params=[
    (True, 1, 0),      # 1.01
    (False, 0, 0),     # 1.02
    ("True", 1, 0),    # 1.03
    ("False", 0, 0),   # 1.04
    ("Yes", 1, 0),     # 1.05
    ("No", 0, 0)])     # 1.06
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

def test_GUIFactory_locate_element(config_GUIFactory_locate_element):
    """Use the config_GUIFactory_locate_element fixture to test the function
    GUIFactory._locate_element by passing it different settings for on_new_row
    and making sure that the resulting placement matches that specified.

    :param config_GUIFactory_locate_element:
        the fixture function generating different layouts, some on_new_row
        and others not
    """
    actual = suipy_framework.GUIFactory(**KEYS)._locate_element(
        config_GUIFactory_locate_element[0])
    expected = (
        config_GUIFactory_locate_element[1],
        config_GUIFactory_locate_element[2],
        config_GUIFactory_locate_element[3])

    assert actual == expected

# GUIFactory._build_element
#
# The only predicate is part of the error handling logic. A single clause
# determines the result in all cases.
#
#  2: Test requirements
#  for GUIFactory._build_element
#________________________
#  TR  |  (not builder) |
# 2.01 |        T*      |
# 2.02 |        F*      |
#      |________________|
@pytest.fixture(params=[
    MOCK_TYPE, # 2.01
    "wacko"])           # 2.02
# "wacko" is an invalid widget type without a registered builder
def config_GUIFactory_build_element(request):
    """Generate a fixture for the build_element test using a real type of
    element and a fake for different instances, registering a mock_builder
    under the real "type" in each case.

    :param request:
        object from fixture allowing access to fixture param for this run
    :return:
        a tuple containing
            [0] arguments to pass to _build_element, including the config dict
            [1] the factory object with a mocked builder registered under
            MOCK_TYPE
            [2] arguments to expect passed to the mocked builder object
            [3] the mocked builder object
    """
    factory_fixture = get_GUIFactory_fixture()

    mock_builder = unittest.mock.Mock(spec=suipy_framework.ValueEntryBuilder)
    # For some reason, mocking suipy_framework.TextLineBuilder passes,
    # but mocking suipy_framework.ValueEntryBuilder,
    # suipy_framework.ButtonBuilder, and suipy_framework.DropDownBuilder
    # doesn't pass. I am not sure if it's a bug in my test or suipy_framework.

    config_fixture = {
        KEYS["type_key"]: request.param,
        KEYS["name_key"]: "some_widget",
        KEYS["children_key"]: [],
        KEYS["properties_key"]: {}
    }

    build_args = dict(
        element_config_data=config_fixture,
        action_mapping=SIMPLE_ACTIONS,
        parent=None,
        row=0,
        default_column=0,
        level=0,
    )
    # These are the keyword arguments that _build_element takes.

    builder__call__args = dict(
        current_row=build_args["row"],
        current_column=factory_fixture._locate_element(
            element_config_data=config_fixture,
            row=build_args["row"],
            default_column=build_args["default_column"])[2],
        level=build_args["level"],
        parent=build_args["parent"],
        **config_fixture,
        **build_args["action_mapping"],
        **KEYS
    )
    # These are the arguments expected to be passed to the builder.

    factory_fixture.register_builder(MOCK_TYPE, mock_builder)
    # For all iterations, register the mock builder under the valid key
    # used in config_fixture in only one instance of this fixture.
    # This makes the builder findable in one instance of the fixture but not
    # in the other.

    return (build_args, factory_fixture, mock_builder, builder__call__args)

def test_GUIFactory_build_element(config_GUIFactory_build_element):
    """Test that the GUIFactory._build_element method properly passes the con-
    figuration data to the (mocked) builder when correctly registered.
    """

    if (config_GUIFactory_build_element[0]["element_config_data"][
            KEYS["type_key"]] == MOCK_TYPE):
        # The widget "type" in the configuration should match the "type" a
        # builder was registered under
        config_GUIFactory_build_element[1]._build_element(
            **config_GUIFactory_build_element[0])

        config_GUIFactory_build_element[2].assert_called_once_with(
            **config_GUIFactory_build_element[3])

    else:
        with pytest.raises(ValueError):
            config_GUIFactory_build_element[1]._build_element(
            **config_GUIFactory_build_element[0])

# GUIFactory.create
#
# There are no explicit predicates, but a loop can be thought of as having a
# single predicate that tests whether there are remaining iterables.
# This test exercises this loop, evaluating this invisible predicate for when
# there are and when there are remaining elements and for when not. The final
# loop iteration satisfies the latter test requirement.
#
#  3: Test requirements
#  for GUIFactory.create
#_______________________________________________
#  TR  |  (more elements in configuration_data) |
# 3.01 |                    T*                  |
# 3.02 |                    F*                  |
#      |________________________________________|
@pytest.fixture()
def setup_test_GUIFactory_create():
    """Prepare configuration data, a GUIFactory fixture, and a set of mocked
    builders for the test of GUIFactory.create
    :return:
        A tuple containing:
            [0] configuration data
            [1] list of two-tuples, each consisting of:
                [0] keyword arguments (kwargs) to be passed to a builder
                [1] mocked builder corresponding to those kwargs
            [2] GUIFactory instance registered to use the mocked builders in
            return tuple value [1]
    """
    factory_fixture = get_GUIFactory_fixture()

    widget1_config = {
        KEYS["type_key"]: "text_line",
        KEYS["name_key"]: "some_text",
        KEYS["children_key"]: [],
        KEYS["properties_key"]: {KEYS["visible_text_key"]: "Test text"}
    }
    builder1__call__args = dict(
        current_row=0,
        current_column=0,
        level=0,
        parent=None,
        **widget1_config,
        **SIMPLE_ACTIONS,
        **KEYS
    )
    widget2_config = {
        KEYS["type_key"]: "entry",
        KEYS["name_key"]: "some_entry",
        KEYS["children_key"]: [],
        KEYS["properties_key"]: {KEYS["default_value_key"]: 2,
                                 KEYS["on_new_row_key"]: True}
    }
    builder2__call__args = dict(
        current_row=1,
        current_column=0,
        level=0,
        parent=None,
        **widget2_config,
        **SIMPLE_ACTIONS,
        **KEYS
    )
    widget3_config = {
        KEYS["type_key"]: "button",
        KEYS["name_key"]: "some_button",
        KEYS["children_key"]: [],
        KEYS["properties_key"]: {KEYS["action_key"]: "test_callback"}
    }
    builder3__call__args = dict(
        current_row=1,
        current_column=1,
        level=0,
        parent=None,
        **widget3_config,
        **SIMPLE_ACTIONS,
        **KEYS
    )
    # Can get away with parent=None for these normally-windowed widget types
    # because a mock is used, so no real widget is made

    config_fixture = [widget1_config, widget2_config, widget3_config]

    builder1_mock = unittest.mock.Mock(spec=suipy_framework.TextLineBuilder)
    builder2_mock = unittest.mock.Mock(spec=suipy_framework.ValueEntryBuilder)
    builder3_mock = unittest.mock.Mock(spec=suipy_framework.ButtonBuilder)
    # 

    factory_fixture.register_builder(widget1_config[KEYS["type_key"]], builder1_mock)
    factory_fixture.register_builder(widget2_config[KEYS["type_key"]], builder2_mock)
    factory_fixture.register_builder(widget3_config[KEYS["type_key"]], builder3_mock)


    args_and_mocks = [(builder1__call__args, builder1_mock), # 3.01
                      (builder2__call__args, builder2_mock),
                      (builder3__call__args, builder3_mock)] # 3.02
                      # (final iteration of loop in GUIFactory.create)

    return (config_fixture, args_and_mocks, factory_fixture)

def test_GUIFactory_create(setup_test_GUIFactory_create):
    """Test the loop in GUIFactory.create by passing it a list of widget
    configurations to iterate through.

    :param setup_test_GUIFactory_create:
        fixture instance with configuration data, mocked builders, and
        a mocked GUIFactory
    """
    setup_test_GUIFactory_create[2].create(
        configuration_data=setup_test_GUIFactory_create[0],
        action_mapping=SIMPLE_ACTIONS,
        inventory_list=[],
        parent_widget=None,
        level=0)

    for args_for_builder in setup_test_GUIFactory_create[1]:
        args_for_builder[1].assert_called_once_with(**args_for_builder[0])

#==============================================================================
# Fuzzing Tests
#------------------------------------------------------------------------------
class RandomStringGenerator:
    """This class provides methods for getting reproducibly pseudo-random
    strings of various lengths
    """
    def __init__(self, randomness_seed=1234567890):
        """Instantiate an instance using the given seed for the randomness.
        :param randomness_seed:
            the value to seed the random generator with, defaulting to a hard-
            coded int for reproducibility.
        :return:
            an instance ready to start generating pseudo-random strings
        """
        random.seed(randomness_seed)

    def get_random_char(self, code_point_range=CHAR_CODE_RANGE):
        """Generate a random 1-length consisting of a single codepoint in the
        given interval, inclusive.
        :param code_point_range:
            the interval over which to generate the code point
        :return:
            a pseudo-random char in the interval
        """

        random_code_point = random.randint(*code_point_range)

        return chr(random_code_point)

    def get_random_str(self, length=2, code_point_range=CHAR_CODE_RANGE):
        """Generate a random, arbitrary-length string with characters possibly
        ranging from that corresponding to the lowest code point in the given
        range up to and including that corresponding to the highest code point
        in the range.
        :param length:
            the length of string to generate
        :param code_point_range:
            the range of code points to possibly include in the returned string
        :return:
            string object of given length consisting of pseudo-random
            characters"""
        random_string = ""

        for i in range(length):
            random_string += self.get_random_char(code_point_range)

        return random_string

#------------------------------------------------------------------------------
# Tests for TextLineBuilder
#------------------------------------------------------------------------------
@pytest.fixture
def setup_test_builder():
    """Do some setup needed for multiple builder tests to follow: prepare a
    parent window, seed the fuzzer, and set up a base configuration to modify
    :return:
        tuple containing
            [0] the configuration for a generic widget to be modified as
            needed
            [1] an initialized (but not open) window widget to pass a parent
            [2] an instance of RandomStringGenerator to use to get random
            input
    """
    window_fixture = tkinter.Tk()
    fuzzer = RandomStringGenerator()
    base_config = {
        KEYS["type_key"]: "some_type",
        KEYS["name_key"]: "random_widget",
        KEYS["properties_key"]: {},
        KEYS["children_key"]: []
    }
    return (base_config, window_fixture, fuzzer)

@pytest.fixture
def setup_test_textlinebuilder(setup_test_builder):
    """Prepare to test the TextLineBuilder class by initializing a context
    for the widget and preparing a configuration data spec to pass the builder
    :return:
        tuple of
            [0] the configuration data to pass TextLineBuilder
            [1] the window as returned by setup_test_builder
            [2] the RandomStringGenerator as returned by setup_test_builder
    """
    text_line_config = setup_test_builder[0]

    text_line_config[KEYS["type_key"]] = "text_line"
    return (text_line_config, setup_test_builder[1], setup_test_builder[2])

def test_textlinebuilder(setup_test_textlinebuilder):
    """Pass random property key-value pairs into the TextLineBuilder.__call__
    method in the properties keyword argument
    :param setup_test_textlinebuilder:
        the fixture instance to do this test with
    """
    widget_config = setup_test_textlinebuilder[0]
    builder_fixture = suipy_framework.TextLineBuilder()

    for i in range(10000):
        random_key = setup_test_textlinebuilder[2].get_random_str(length=10)
        random_value = setup_test_textlinebuilder[2].get_random_str(length=10)

        widget_config[KEYS["properties_key"]][
            random_key] = random_value
    # Put a bunch of random properties in the textlinebuilder's input

    builder_fixture(
        **widget_config,
        parent=setup_test_textlinebuilder[1],
        current_row=0,
        current_column=0,
        **KEYS)
    # Call the builder with that data.
    # If there's an exception, the test fails.

#------------------------------------------------------------------------------
# Tests for TextLineBuilder
#------------------------------------------------------------------------------