# -*- coding: utf-8 -*-
""" Tests for the SUIPy framework implemented using a variety of strategies.

First, the intermediate-level classes such as the GUI are to be tested using a
logic criteria like correlated active clause coverage.

"""

import suipy_framework

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

# ============================================================================


def prepare_keys():
    suipy_framework.GUIData()

def test_GUIFactory():
    suipy_framework.GUIFactory()