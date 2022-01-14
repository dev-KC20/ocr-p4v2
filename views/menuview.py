#! /usr/bin/env Python3
# coding: utf-8
"""Present to the user the menu and gets his option choice with terminal interface."""
from utils.constants import CLEAR_TERMINAL


class MenuView:
    """Provide a menu manager view."""

    def __init__(self, menu):
        """Class init to hold the menu description & actions."""
        self.menu = menu

    def show_menu(self):
        """Show menu option ."""
        print(CLEAR_TERMINAL)
        line_len = len(self.menu.get_name()) + 8
        print("*" * line_len)
        print(f" Menu {self.menu.get_name()}")
        print("*" * line_len)
        print()
        for option, description in self.menu.items():
            print(f"{option} {description[0]}")
            print()
        print("*" * line_len)

    def get_user_input(self):
        """Show menu and get the user's selection."""
        while True:
            self.show_menu()
            prompt_result = input("Votre choix: ")
            if prompt_result in self.menu:
                return prompt_result

    def good_bye(self):
        """Say good bye when user quits."""
        print(CLEAR_TERMINAL)
        line_len = len(self.menu.get_name()) + 8
        print("*" * line_len)
        print(f" Menu: {self.menu.get_name()}.")
        print("*" * line_len)
        print()
        print()
        print("Merci d'avoir utilisé notre application")
        print("A bientôt, ocr")
        print()
        print("*" * line_len)
        return None
