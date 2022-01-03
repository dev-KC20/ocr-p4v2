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
            # remove tournament having already rounds set as no more player should be added
            tournament_list_wo_rounds = [
                x for x in tournament_list_db.get_list_of_tournaments() if len(x.get_tournament_rounds()) == 0
            ]
            tournament_id = int(new_tournament_view.prompt_for_tournament_id(tournament_list_wo_rounds))
            # get the players from DB
            player_list_db = self.init_player()
            # prepare the  view for selecting one player
            new_tournament_view = TournamentView()
            player_id = int(new_tournament_view.prompt_for_player_id(player_list_db.get_list_of_players()))
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
            tournament_id = new_tournament_view.prompt_for_tournament_id(tournament_list_with_players)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
                # save only player's id, not full Player class
                # do the initial pairing of players
                (
                    list_paired_match,
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
                for i in range(len(list_paired_match)):
                    new_match = list_paired_match[i]
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
                selected_tournament.save_tournament(selected_tournament, selected_tournament.get_tournament_id())

        # Finishing of a given Round of a given Tournament : time's over!
        if chosen_option == "50":
            tournament_list_db = self.init_tournament()
            new_tournament_view = TournamentView()
            # remove tournaments w/o round to close == no end time
            tournament_list_with_round = [
                x
                for x in tournament_list_db.get_list_of_tournaments()
                if x.get_tournament_to_finish_round() is not None
            ]
            tournament_id = new_tournament_view.prompt_for_tournament_id(tournament_list_with_round)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
                selected_round_to_close = selected_tournament.get_tournament_to_finish_round()
                selected_round_to_close.close_round()
                selected_tournament.save_tournament(selected_tournament, selected_tournament.get_tournament_id())

        # Register matches results
        if chosen_option == "60":
            tournament_list_db = self.init_tournament()
            new_tournament_view = TournamentView()

            # keep only tournaments that are finished
            tournament_list_to_register = [
                x
                for x in tournament_list_db.get_list_of_tournaments()
                if x.get_tournament_to_close_round() is not None
            ]
            # ask user to select tournament & retrieve its rounds

            tournament_id = new_tournament_view.prompt_for_tournament_id(tournament_list_to_register)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
                # get the round attached to selected tournament?
                round_to_close = selected_tournament.get_tournament_to_close_round()
                round_name_to_close = [round_to_close.get_round_name()]
                new_round_view = RoundView()
                # ask user to select a round to register
                # normally there should be only one but who knows in the future ;)
                round_name_to_register_in = new_round_view.prompt_for_round_name(round_name_to_close)
                # no escape request
                if round_name_to_register_in is not None:
                    # get the full Round object
                    if round_to_close.get_round_name() == round_name_to_register_in:
                        # prepare the view for entering results
                        new_match_view = MatchView()
                        # list of player1 scores for all matches of the round
                        waiting_result_matchs = round_to_close.get_matchs()
                        result_player1 = new_match_view.prompt_for_match_result(waiting_result_matchs)
                        # walk the match and apply set_match_score in sequence
                        i = 0
                        for jeu in waiting_result_matchs:
                            jeu.set_match_score(float(result_player1[i]), 1.0 - float(result_player1[i]))
                            i += 1
                        # special odd number of player case :
                        # he is set as player1 == player2 then he wins
                        selected_tournament.save_tournament(
                            selected_tournament, selected_tournament.get_tournament_id()
                        )

        # create the next round & matchs == pairing step 2+
        if chosen_option == "70":

            # get the tournaments from DB
            # [M] possibilité de transformer ces 2 lignes en méthodes
            tournament_list_db = self.init_tournament()
            new_tournament_view = TournamentView()

            # remove tournaments not having the first round over
            # & their # of rounds not yet reached
            # & the previous round not closed
            tournament_list_with_players = [
                x
                for x in tournament_list_db.get_list_of_tournaments()
                if len(x.get_tournament_rounds()) > 0
                and len(x.get_tournament_rounds()) < x.get_tournament_round_number()
                and x.get_tournament_last_closed_round() is not None
            ]

            # TODO: when & how to inform the user when the # of rounds was reached : at result registration?
            # prompt the user for what tournament its next round is to be created
            tournament_id = new_tournament_view.prompt_for_tournament_id(tournament_list_with_players)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)

                # TODO: pairing_next take into account the already met opponents
                # do the next pairing of players == pairing step2
                (
                    list_paired_match,
                    odd_winner_id,
                ) = selected_tournament.pair_players_next_time()

                # get the previous round name
                former_round = selected_tournament.get_tournament_last_closed_round()
                # and its name
                former_round_name = former_round.get_round_name()
                # and the planned number of rounds
                number_rounds_tournament = selected_tournament.get_tournament_round_number()
                # how many digits for the numbering
                if number_rounds_tournament > 9 and number_rounds_tournament < 99:
                    indice = 2
                else:
                    indice = 1
                # retrieve the nummer of the former round
                former_round_number = former_round_name[len(former_round_name) - indice:]
                # check if its numerical & add 1
                if former_round_number.isdigit():
                    next_round_number = int(former_round_number) + 1
                else:
                    next_round_number = 2
                next_round_name = former_round_name[: len(former_round_name) - indice] + str(next_round_number)

                # create the new round
                next_round = Round(
                    next_round_name,
                    datetime.date.today(),
                    datetime.datetime.now().time(),
                )
                # Generate matches from pairing
                for i in range(len(list_paired_match)):
                    new_match = list_paired_match[i]
                    next_round.add_match(new_match)
                # odd player plays against himself and scores 1
                if odd_winner_id:
                    # will be granted victory later
                    winner_match = (odd_winner_id, odd_winner_id)
                    # create a match against himself for the odd player
                    next_round.add_match(winner_match)
                # add the round with its matches to the tournament
                selected_tournament.add_round(next_round)
                # and save them into DB
                selected_tournament.save_tournament(selected_tournament, selected_tournament.get_tournament_id())

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
    "70": ("Ouvrir ronde suivante", MenuTournamentController()),
    "80": ("Retour à l'accueil", MenuController()),
    "90": ("Quitter l'application", MenuExitController()),
}
