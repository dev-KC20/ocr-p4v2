#! /usr/bin/env python
# coding: utf-8
"""Manage chess tournaments after swiss rules.

But also manage a list of known players
"""
from utils.menu import Menu
from models.player import Players, Player
from models.tournament import Tournament, Tournaments
from views.menuview import MenuView
from views.appview import PlayersView, PlayerView, TournamentView, TournamentsView


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
            # Afficher les joueurs en base
            player_list_db = Players()
            player_list_db.load_players()
            PlayersView().print_players(player_list_db.get_list_of_players())

        if chosen_option == "20":
            # Ajouter un joueur en base
            player_list_db = Players()
            player_list_db.load_players()
            player_view = PlayerView()
            new_player = Player(*player_view.prompt_for_player())
            player_list_db.add_player_to_list(new_player)
            new_player.save_player(new_player)

        if chosen_option == "30":
            # Mettre à jour ELO 
            player_list_db = Players()
            player_list_db.load_players()
            players_view = PlayersView()
            players_view.print_players(player_list_db.get_list_of_players())
            (player_id, new_ranking) = PlayerView().prompt_for_new_ranking()
            player_id = int(player_id)
            new_player = player_list_db.get_player_by_id(int(player_id))
            new_player.set_ranking(new_ranking)
            new_player.save_player(new_player, player_id)
        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuTournamentController:
    def __init__(self):
        self.menu = None

    def run(self):
        """ """
        self.menu = Menu("Gérer les tournois")

        for key, value in MENU_TOURNAMENT.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()
        if chosen_option == "10":
            # Afficher les tournois
            tournament_list_db = Tournaments()
            tournament_list_db.load_tournaments()
            tournaments_view = TournamentsView()
            tournaments_view.print_tournaments(tournament_list_db.get_list_of_tournaments())

        if chosen_option == "20":
            # Créer un tournoi
            tournament_view = TournamentView()
            new_tournament = Tournament(*tournament_view.prompt_for_tournament())
            new_tournament.save_tournament(new_tournament)

        if chosen_option == "30":
            # Ouvrir un tournoi == ajouter des joueurs
            tournament_list_db = Tournaments()
            tournament_list_db.load_tournaments()
            new_tournament_view = TournamentView()
            tournament_id = int(new_tournament_view.select_tournament(tournament_list_db.get_list_of_tournaments()))
            player_list_db = Players()
            player_list_db.load_players()
            new_tournament_view = TournamentView()
            player_id = int(new_tournament_view.select_player(player_list_db.get_list_of_players()))
            selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
            selected_tournament.add_player_to_tournament(player_list_db.get_player_by_id(player_id))
            # provide tournament_id to update existing tournament
            selected_tournament.save_tournament(selected_tournament, tournament_id)

        if chosen_option == "40":
            pass

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
    "20": ("Gérer les tournois", MenuTournamentController()),
    "90": ("Quitter l'application", MenuExitController()),
}

MENU_PLAYER = {
    "10": ("Afficher les joueurs en base", MenuPlayerController()),
    "20": ("Ajouter un joueur en base", MenuPlayerController()),
    "30": ("Mettre à jour ELO ", MenuPlayerController()),
    "80": ("Retour à l'accueil", MenuController()),
    "90": ("Quitter l'application", MenuExitController()),
}
MENU_TOURNAMENT = {
    "10": ("Afficher les tournois", MenuTournamentController()),
    "20": ("Créer un tournoi", MenuTournamentController()),
    "30": ("Ouvrir un tournoi", MenuTournamentController()),
    "40": ("Mettre à jour les résultats", MenuTournamentController()),
    "80": ("Retour à l'accueil", MenuController()),
    "90": ("Quitter l'application", MenuExitController()),
}
