#! /usr/bin/env Python3
# coding: utf-8
"""Model of the menu which is a list of name, option & action."""


class Menu:
    """Hold the Menu model shown in the view."""

    def __init__(self, name):
        """Menu Class init to hold the name, option and action of one menu line."""
        self._options = {}
        self._name = name

    def add_menu(self, number, description_action):
        """Add a new menu line into the menu screen."""
        self._options[number] = (description_action)

    def items(self):
        """Add a new menu line into the menu screen."""
        return self._options.items()

    def get_name(self):
        """Get the name of the menu (not used in controller/view)."""
        return self._name

    def get_action(self, number):
        """Get the action related to the menu option."""
        description, action = self._options[number]
        return action

    def __contains__(self, option):
        """Check if the option is part of the menu."""
        return str(option) in self._options
