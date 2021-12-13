#! /usr/bin/env python
# coding: utf-8
"""Manage chess tournaments after swiss rules.

But also manage a list of known players
"""
from utils.menu import Menu
from models.player import Players, Player
from views.menuview import MenuView
from views.appview import PlayersView, PlayerView


class AppController:
    """manage the menu sytem."""

    def __init__(self):
        self.controller = None
        self.players_view = None
        self.tournament_view = None

    def run(self):
        # manage menus
        self.controller = MenuController().run()
        while self.controller:
            self.controller = self.controller.run()


class MenuController:
    def __init__(self):
        self.menu = None

    def run(self):
        """ """
        self.menu = Menu("Accueil")
        for key, value in MENU.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()
        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuPlayerController:
    def __init__(self):
        self.menu = None

    def run(self):
        """ """
        self.menu = Menu("Gérer les joueurs")

        for key, value in MENU_PLAYER.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()
        if chosen_option == "10":
            player_list_db = Players()
            player_list_db.load_players()
            PlayersView().print_players(player_list_db.get_list_of_players())
        if chosen_option == "20":
            player_list_db = Players()
            player_list_db.load_players()
            player_view = PlayerView()
            new_player = Player(*player_view.prompt_for_player())
            player_list_db.add_player_to_list(new_player)
            new_player.save_player(new_player)
        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuExitController:
    def __init__(self):
        self.menu = None

    def run(self):
        """ """
        self.menu = Menu("Quitter l'application")
        return MenuView(self.menu).good_bye()


MENU = {
    "10": ("Gérer les joueurs", MenuPlayerController()),
    "90": ("Quitter l'application", MenuExitController()),
}

MENU_PLAYER = {
    "10": ("Afficher les joueurs en base", MenuPlayerController()),
    "20": ("Ajouter un joueur en base", MenuPlayerController()),
    "80": ("Retour à l'accueil", MenuController()),
    "90": ("Quitter l'application", MenuExitController()),
}
