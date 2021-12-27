#! /usr/bin/env python
# coding: utf-8
"""Manage chess tournaments after swiss rules.

But also manage a list of known players
"""
import datetime

from utils.menu import Menu
from models.player import Players, Player
from models.tournament import Tournament, Tournaments, Round
from views.menuview import MenuView
from views.appview import (
    PlayersView,
    PlayerView,
    TournamentView,
    TournamentsView,
    RoundView,
    MatchView,
)


class AppController:
    """manage the menu sytem."""

    def __init__(self):
        self.controller = None
        self.players_view = None
        self.tournament_view = None

    def run(self):
        """manage menus"""
        self.controller = MenuController().run()
        while self.controller:
            self.controller = self.controller.run()


class MenuController:
    """ 
    """
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
            PlayersView().print_players(player_list_db.get_players_by_rank())

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
            # get the player from player_id
            player_list_db = Players()
            player_list_db.load_players()
            tournaments_view = TournamentsView()
            tournaments_view.print_tournaments(
                tournament_list_db.get_list_of_tournaments(),
                player_list_db.get_players_by_rank(),
            )

        if chosen_option == "20":
            # Créer un tournoi
            tournament_view = TournamentView()
            new_tournament = Tournament(
                *tournament_view.prompt_for_tournament()
            )
            new_tournament.save_tournament(new_tournament)

        if chosen_option == "30":
            # Ajouter des joueurs
            tournament_list_db = Tournaments()
            tournament_list_db.load_tournaments()
            new_tournament_view = TournamentView()
            tournament_id = int(
                new_tournament_view.select_tournament(
                    tournament_list_db.get_list_of_tournaments()
                )
            )
            player_list_db = Players()
            player_list_db.load_players()
            new_tournament_view = TournamentView()
            player_id = int(
                new_tournament_view.select_player(
                    player_list_db.get_list_of_players()
                )
            )
            selected_tournament = tournament_list_db.get_tournament_by_id(
                tournament_id
            )
            # save only player's id, not full Player class
            selected_tournament.add_player_to_tournament(player_id)
            # provide tournament_id to update existing tournament
            selected_tournament.save_tournament(
                selected_tournament, tournament_id
            )

        if chosen_option == "40":
            # Ouvrir un tournoi == associer les joueurs en match
            tournament_list_db = Tournaments()
            tournament_list_db.load_tournaments()
            new_tournament_view = TournamentView()
            tournament_id = int(
                new_tournament_view.select_tournament(
                    tournament_list_db.get_list_of_tournaments()
                )
            )
            selected_tournament = tournament_list_db.get_tournament_by_id(
                tournament_id
            )
            # save only player's id, not full Player class
            (
                list_matchs,
                odd_winner_id,
            ) = selected_tournament.pair_players_first_time()

            num_ronde = 1
            # for num_ronde in range(selected_tournament.get_tournament_round_number()):
            round_first = Round(
                "Ronde" + str(num_ronde),
                datetime.date.today(),
                datetime.datetime.now().time(),
            )
            # generate matches from initial pairing
            for i in range(len(list_matchs)):
                new_match = list_matchs[i]
                round_first.add_match(new_match)
            # isolate palyer plays against himself and scores 2 x 0.5=1
            if odd_winner_id:
                # will be granted victory later
                winner_match = (odd_winner_id, odd_winner_id)
                # winner_match.set_match_score(0.5)
                round_first.add_match(winner_match)
            print(round_first)
            selected_tournament.add_round(round_first)
            selected_tournament.save_tournament(
                selected_tournament, selected_tournament.get_id()
            )

        if chosen_option == "50":
            # Closing a given Round of a given Tournament
            tournament_list_db = Tournaments()
            tournament_list_db.load_tournaments()
            new_tournament_view = TournamentView()
            existing_rounds = []
            while not existing_rounds:
                tournament_id = int(
                    new_tournament_view.select_tournament(
                        tournament_list_db.get_list_of_tournaments()
                    )
                )
                selected_tournament = tournament_list_db.get_tournament_by_id(
                    tournament_id
                )
                # are rounds attached to selected tournament?
                existing_rounds = selected_tournament.get_tournament_rounds()

            new_round_view = RoundView()
            # is the selected round existing at all in the tournaments?
            search_round = True
            while search_round:
                round_to_close = new_round_view.prompt_for_round()
                # check if round exists
                existing_rounds = selected_tournament.get_tournament_rounds()
                if existing_rounds != []:
                    for ronde in existing_rounds:
                        if ronde[0].get_round_name() == round_to_close:
                            search_round = False
                            round_to_close = ronde[0]
            round_to_close.close_round()
            selected_tournament.save_tournament(
                selected_tournament, selected_tournament.get_id()
            )

        if chosen_option == "60":
            # given a Round & a Tournament, enter match results
            # load instances of tournaments to choose from
            tournament_list_db = Tournaments()
            tournament_list_db.load_tournaments()
            new_tournament_view = TournamentView()

            # ask user to select tournament & retrieve it & its rounds
            existing_rounds = []
            while not existing_rounds:
                tournament_id = int(
                    new_tournament_view.select_tournament(
                        tournament_list_db.get_list_of_tournaments()
                    )
                )
                selected_tournament = tournament_list_db.get_tournament_by_id(
                    tournament_id
                )
                # get the rounds attached to selected tournament?
                existing_rounds = selected_tournament.get_tournament_rounds()

            new_round_view = RoundView()
            # ask user to select a round & check if it exists at all in the tournament
            search_round = True
            while search_round:
                # ask which round to register results in
                round_to_register_in = new_round_view.prompt_for_round()
                # check if round exists
                existing_rounds = selected_tournament.get_tournament_rounds()
                if existing_rounds != []:
                    for ronde in existing_rounds:
                        if ronde[0].get_round_name() == round_to_register_in:
                            search_round = False
                            round_to_register_in = ronde[0]

            new_match_view = MatchView()
            # list of player1 scores for all matches of the round
            waiting_result_matchs = round_to_register_in.get_matchs()
            result_player1 = new_match_view.prompt_for_match_result(
                waiting_result_matchs
            )
            # walk the match and apply set_match_score in sequence
            i = 0
            for jeu in waiting_result_matchs:
                jeu.set_match_score(float(result_player1[i]))
                i += 1
            # TODO: special odd number of player case
            # but if player1 == player2 then he wins

            selected_tournament.save_tournament(
                selected_tournament, selected_tournament.get_id()
            )

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
    "30": ("Inscrire des joueurs à un tournoi", MenuTournamentController()),
    "40": ("Ouvrir un tournoi", MenuTournamentController()),
    "50": ("Fermer une ronde", MenuTournamentController()),
    "60": ("Mettre à jour les résultats", MenuTournamentController()),
    "80": ("Retour à l'accueil", MenuController()),
    "90": ("Quitter l'application", MenuExitController()),
}
