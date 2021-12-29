#! /usr/bin/env python
# coding: utf-8
"""Manage chess tournaments after swiss rules.

But also manage a list of known players

The Controllers communicate with the user by sending prompt to the Views and getting back the user selection.
A methode to the view may pass list of values to show/chose from as well errors as per Business rules


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
    """manage the Home menu"""

    def __init__(self):
        self.menu = None

    def run(self):
        """ """
        self.menu = Menu("Accueil")
        for key, value in MENU_HOME.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()
        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuPlayerController:
    def __init__(self):
        self.menu = None

    def init_player(self):
        player_list = Players()
        player_list.load_players()
        return player_list

    def run(self):
        """ """
        self.menu = Menu("Gérer les joueurs")

        for key, value in MENU_PLAYER.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()
        if chosen_option == "10":
            # Show all the players in DB
            player_list_db = self.init_player()
            PlayersView().print_players(player_list_db.get_players_by_rank())

        if chosen_option == "20":
            # Add a player to the list of player
            player_list_db = self.init_player()
            player_view = PlayerView()
            # Prompt the user for the player details
            new_player = Player(*player_view.prompt_for_player())
            # Add the player to the instance of player list
            player_list_db.add_player_to_list(new_player)
            # Save the new player in DB
            new_player.save_player(new_player)

        if chosen_option == "30":
            # Update a player's ELO Ranking
            player_list_db = self.init_player()
            players_view = PlayersView()
            # Show the list of palyer to the user
            players_view.print_players(player_list_db.get_list_of_players())
            # Prompt the user for which player to update
            (player_id, new_ranking) = PlayerView().prompt_for_new_ranking()
            player_id = int(player_id)
            new_player = player_list_db.get_player_by_id(int(player_id))
            # Update the player ranking
            new_player.set_ranking(new_ranking)
            # Save the player in DB
            new_player.save_player(new_player, player_id)
        # move to next menu
        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuTournamentController:
    def __init__(self):
        self.menu = None

    def init_player(self):
        player_list = Players()
        player_list.load_players()
        return player_list

    def init_tournament(self):
        tournament_list = Tournaments()
        tournament_list.load_tournaments()

        return tournament_list

    def run(self):
        """ """
        self.menu = Menu("Gérer les tournois")

        for key, value in MENU_TOURNAMENT.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()

        # Show the tournaments
        if chosen_option == "10":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            # get the players from DB
            player_list_db = self.init_player()
            # prepare the  view of the list of tournaments
            tournaments_view = TournamentsView()
            # show the tournaments and their players
            tournaments_view.print_tournaments(
                tournament_list_db.get_list_of_tournaments(),
                player_list_db.get_players_by_rank(),
            )

        # Create a tournament
        if chosen_option == "20":
            # prepare the prompt for tournament View
            tournament_view = TournamentView()
            # ask and create the tournament object
            new_tournament = Tournament(*tournament_view.prompt_for_tournament())
            # save the newly created tournament
            new_tournament.save_tournament(new_tournament)

        # Add players to one tournament
        if chosen_option == "30":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            # prepare the  view for selecting one tournament
            new_tournament_view = TournamentView()
            # remove tournament having already round set as no player should be added
            tournament_list_wo_rounds = [
                x for x in tournament_list_db.get_list_of_tournaments() if len(x.get_tournament_rounds()) == 0
            ]
            tournament_id = int(new_tournament_view.select_tournament(tournament_list_wo_rounds))
            # get the players from DB
            player_list_db = self.init_player()
            # prepare the  view for selecting one player
            new_tournament_view = TournamentView()
            player_id = int(new_tournament_view.select_player(player_list_db.get_list_of_players()))
            # create a tournament object from its tournament id
            selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
            # save only player's id, not full Player class
            selected_tournament.add_player_to_tournament(player_id)
            # provide tournament_id to update existing tournament
            selected_tournament.save_tournament(selected_tournament, tournament_id)

        # open the tournament & create the first round & matchs
        if chosen_option == "40":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            new_tournament_view = TournamentView()
            # remove tournament having less than 2 players
            # also remove tournament having already rounds
            tournament_list_with_players = [
                x
                for x in tournament_list_db.get_list_of_tournaments()
                if len(x.get_tournament_players()) > 1 and len(x.get_tournament_rounds()) == 0
            ]
            tournament_id = int(new_tournament_view.select_tournament(tournament_list_with_players))
            selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
            # save only player's id, not full Player class
            # do the initial pairing of players
            (
                list_matchs,
                odd_winner_id,
            ) = selected_tournament.pair_players_first_time()
            # create the initial round
            num_ronde = 1
            round_first = Round(
                "Ronde" + str(num_ronde),
                datetime.date.today(),
                datetime.datetime.now().time(),
            )
            # Next generate matches from initial pairing
            for i in range(len(list_matchs)):
                new_match = list_matchs[i]
                round_first.add_match(new_match)
            # odd player plays against himself and scores 1
            if odd_winner_id:
                # will be granted victory later
                winner_match = (odd_winner_id, odd_winner_id)
                # create a match against himself for the odd player
                round_first.add_match(winner_match)
            # add the round with its matches to the tournament
            selected_tournament.add_round(round_first)
            # and save them into DB
            selected_tournament.save_tournament(selected_tournament, selected_tournament.get_id())

        # Closing of a given Round of a given Tournament
        if chosen_option == "50":
            # TODO ne fermer une ronde que si matchs
            tournament_list_db = self.init_tournament()
            new_tournament_view = TournamentView()
            # remove tournaments w/o round to close
            tournament_list_with_round = [
                x
                for x in tournament_list_db.get_list_of_tournaments()
                if x.get_tournament_to_close_round() is not None
            ]
            # tournament_list_with_round = [
            #     x
            #     for x in tournament_list_db.get_list_of_tournaments()
            #     if len(x.get_tournament_rounds()) > 0 and x.get_tournament_to_close_round() is not None
            # ]
            existing_rounds = []
            while not existing_rounds:
                tournament_id = int(new_tournament_view.select_tournament(tournament_list_with_round))
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
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
            selected_tournament.save_tournament(selected_tournament, selected_tournament.get_id())

        if chosen_option == "60":
            # given a Round & a Tournament, enter match results
            # load instances of tournaments to choose from
            tournament_list_db = self.init_tournament()
            new_tournament_view = TournamentView()

            # ask user to select tournament & retrieve it & its rounds
            existing_rounds = []
            while not existing_rounds:
                tournament_id = int(
                    new_tournament_view.select_tournament(tournament_list_db.get_list_of_tournaments())
                )
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
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
            result_player1 = new_match_view.prompt_for_match_result(waiting_result_matchs)
            # walk the match and apply set_match_score in sequence
            i = 0
            for jeu in waiting_result_matchs:
                jeu.set_match_score(float(result_player1[i]))
                i += 1
            # TODO: special odd number of player case
            # but if player1 == player2 then he wins

            selected_tournament.save_tournament(selected_tournament, selected_tournament.get_id())

        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuExitController:
    def __init__(self):
        self.menu = None

    def run(self):
        """ """
        self.menu = Menu("Quitter l'application")
        return MenuView(self.menu).good_bye()


MENU_HOME = {
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
