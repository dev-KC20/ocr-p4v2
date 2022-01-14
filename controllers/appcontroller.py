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
    PlayersReportView,
    TournamentsReportView,
)


class AppController:
    """Manage the menu sytem."""

    def __init__(self):
        """Class init to hold current views."""
        self.controller = None
        self.players_view = None
        self.tournament_view = None

    def run(self):
        """Manage current active menu."""
        self.controller = MenuController().run()
        while self.controller:
            self.controller = self.controller.run()


class MenuController:
    """Manage the Home menu."""

    def __init__(self):
        """Class init to hold the menu instance."""
        self.menu = None

    def run(self):
        """Manage the menu system & option chosen."""
        self.menu = Menu("Accueil")
        for key, value in MENU_HOME.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()
        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuPlayerController:
    """Manage the Player menu."""

    def __init__(self):
        """Class init to hold the menu instance."""
        self.menu = None

    def init_player(self):
        """Initiate the DB connection to Player table."""
        player_list = Players()
        player_list.load_players()
        return player_list

    def run(self):
        """Manage the Player menu & option chosen."""
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
    """Manage the Tournament menu."""

    def __init__(self):
        """Class init to hold the menu instance."""
        self.menu = None

    def init_player(self):
        """Initiate the DB connection to Player table."""
        player_list = Players()
        player_list.load_players()
        return player_list

    def init_tournament(self):
        """Initiate the DB connection to Tournament table."""
        tournament_list = Tournaments()
        tournament_list.load_tournaments()

        return tournament_list

    def open_tournament_create_first_round(self):
        """Open tournament, create first round & matchs == pairing step 1."""
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
            # TODO: if odd too many matchs for the oddp player
            # if odd_winner_id:
            #     # will be granted victory later
            #     winner_match = (odd_winner_id, odd_winner_id)
            #     # create a match against himself for the odd player
            #     round_first.add_match(winner_match)
            # add the round with its matches to the tournament
            selected_tournament.add_round(round_first)
            # and save them into DB
            selected_tournament.save_tournament(selected_tournament, selected_tournament.get_tournament_id())

    def create_next_round_and_match(self):
        """Create the next round & matchs == pairing step 2."""
        tournament_list_db = self.init_tournament()
        new_tournament_view = TournamentView()
        # remove tournaments w/o first round over & their rounds not yet reached & the previous round not closed
        tournament_list_with_players = [
            x
            for x in tournament_list_db.get_list_of_tournaments()
            if (
                len(x.get_tournament_rounds()) > 0
                and len(x.get_tournament_rounds()) < x.get_tournament_round_number()
                and x.get_tournament_last_closed_round() is not None
            )
        ]
        # prompt the user for what tournament its next round is to be created
        tournament_id = new_tournament_view.prompt_for_tournament_id(tournament_list_with_players)
        if tournament_id is not None:
            tournament_id = int(tournament_id)
            selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
            # do the next pairing of players == pairing step2
            (list_paired_match, odd_winner_id) = selected_tournament.pair_players_next_time()
            # get the previous round name
            former_round = selected_tournament.get_tournament_last_closed_round()
            # and its name
            former_round_name = former_round.get_round_name()
            # and the planned number of rounds
            number_rounds_tournament = selected_tournament.get_tournament_round_number()
            # how many digits for the numbering
            indice = 2 if number_rounds_tournament > 9 and number_rounds_tournament < 99 else 1
            # retrieve the nummer of the former round
            former_round_number = former_round_name[(len(former_round_name) - indice):]
            # check if its numerical & add 1
            next_round_number = int(former_round_number) + 1 if former_round_number.isdigit() else 2
            next_round_name = former_round_name[: len(former_round_name) - indice] + str(next_round_number)
            # create the new round
            next_round = Round(
                next_round_name,
                datetime.date.today(),
                datetime.datetime.now().time(),
            )
            # Generate matches from pairing -1 if odd player #
            for i in range(len(list_paired_match)):
                new_match = list_paired_match[i]
                next_round.add_match(new_match)
            # odd player plays against himself and scores 1
            # if odd_winner_id:
            #     # will be granted victory later
            #     winner_match = (odd_winner_id, odd_winner_id)
                # # create a match against himself for the odd player
                # next_round.add_match(winner_match)
            # add the round with its matches to the tournament
            selected_tournament.add_round(next_round)
            # and save them into DB
            selected_tournament.save_tournament(selected_tournament, selected_tournament.get_tournament_id())

    def show_the_tournament(self):
        """Show the tournaments."""
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

    def run(self):
        """Manage the Tournament menu & option chosen."""
        self.menu = Menu("Gérer les tournois")

        for key, value in MENU_TOURNAMENT.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()

        # Show the tournaments
        if chosen_option == "10":
            self.show_the_tournament()

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
            self.open_tournament_create_first_round()

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
            self.create_next_round_and_match()

        # close a tournament by computing the score and update the participant's
        if chosen_option == "75":

            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            new_tournament_view = TournamentView()

            # remove tournaments not having all their expected rounds closed
            # & the previous round not closed
            tournament_list_with_players = [
                x
                for x in tournament_list_db.get_list_of_tournaments()
                if len(x.get_tournament_rounds()) > 0
                and len(x.get_tournament_rounds()) == x.get_tournament_round_number()
                and x.get_tournament_last_closed_round() is not None
                and x.get_tournament_score_status() is False
            ]

            # prompt the user for what tournament its next round is to be created
            tournament_id = new_tournament_view.prompt_for_tournament_id(tournament_list_with_players)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
                # compute the player's former score & update the related tournament
                selected_tournament.update_players_score()

                # and save the tournament status into DB
                selected_tournament.save_tournament(selected_tournament, selected_tournament.get_tournament_id())

        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuReportController:
    """Manage the Report menu."""

    def __init__(self):
        """Class init to hold the menu instance."""
        self.menu = None

    def init_player(self):
        """Initiate the DB connection to Player table."""
        player_list = Players()
        player_list.load_players()
        return player_list

    def init_tournament(self):
        """Initiate the DB connection to tournament table."""
        tournament_list = Tournaments()
        tournament_list.load_tournaments()

        return tournament_list

    def run(self):
        """Manage the Report menu & option chosen."""
        self.menu = Menu("Gérer les rapports")

        for key, value in MENU_REPORT.items():
            self.menu.add_menu(key, value)
        chosen_option = MenuView(self.menu).get_user_input()

        # Show the players - by name sort
        if chosen_option == "10":
            # # get the tournaments from DB
            # tournament_list_db = self.init_tournament()
            # get the players from DB
            player_list_db = self.init_player()
            # prepare the  view of the list of tournaments
            report_view = PlayersReportView()
            # show the tournaments and their players
            report_view.print_players(
                player_list_db.get_players_by_name(),
            )
        # Show the players - by ranking
        if chosen_option == "20":
            player_list_db = self.init_player()
            report_view = PlayersReportView()
            # show the tournaments and their players
            report_view.print_players(
                player_list_db.get_players_by_rank(),
            )
        # Show the players of a tournament - by name
        if chosen_option == "30":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            tournament_list = tournament_list_db.get_list_of_tournaments()
            # prompt the user for what tournament its next round is to be created
            tournament_report_view = TournamentsReportView()
            tournament_id = tournament_report_view.prompt_for_tournament_id(tournament_list)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)
                report_view = TournamentsReportView()
                # show the tournaments and their players
                report_view.print_tournaments_players(selected_tournament.get_tournament_players_by_name())

        # Show the players of a tournament - by ranking
        if chosen_option == "40":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            tournament_list = tournament_list_db.get_list_of_tournaments()
            # prompt the user for what tournament its next round is to be created
            tournament_report_view = TournamentsReportView()
            tournament_id = tournament_report_view.prompt_for_tournament_id(tournament_list)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)

                report_view = TournamentsReportView()
                # show the tournaments and their players
                report_view.print_tournaments_players(selected_tournament.get_tournament_players_by_rank())

        # Show the players of a tournament - by the result they made in tournament
        if chosen_option == "45":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            tournament_list = tournament_list_db.get_list_of_tournaments()
            # prompt the user for what tournament its next round is to be created
            tournament_report_view = TournamentsReportView()
            tournament_id = tournament_report_view.prompt_for_tournament_id(tournament_list)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)

                report_view = TournamentsReportView()
                # show the tournaments and their players
                report_view.print_tournaments_players(selected_tournament.get_tournament_players_by_score())

        # Show the tournaments
        if chosen_option == "50":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            tournament_list = tournament_list_db.get_list_of_tournaments()
            # prompt the user for what tournament its next round is to be created
            tournament_report_view = TournamentsReportView()
            tournament_report_view.print_tournaments(tournament_list)

        # Show the rounds of a tournament
        if chosen_option == "60":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            tournament_list = tournament_list_db.get_list_of_tournaments()
            # prompt the user for what tournament its next round is to be created
            tournament_report_view = TournamentsReportView()
            tournament_id = tournament_report_view.prompt_for_tournament_id(tournament_list)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)

                report_view = TournamentsReportView()
                # show the tournaments and their players
                report_view.print_tournaments_rounds(selected_tournament.get_tournament_rounds_matchs())

        # Show the matchs of a tournament
        if chosen_option == "70":
            # get the tournaments from DB
            tournament_list_db = self.init_tournament()
            tournament_list = tournament_list_db.get_list_of_tournaments()
            # prompt the user for what tournament its next round is to be created
            tournament_report_view = TournamentsReportView()
            tournament_id = tournament_report_view.prompt_for_tournament_id(tournament_list)
            if tournament_id is not None:
                tournament_id = int(tournament_id)
                selected_tournament = tournament_list_db.get_tournament_by_id(tournament_id)

                report_view = TournamentsReportView()
                # show the tournaments and their players
                report_view.print_tournaments_matchs(
                    selected_tournament.get_tournament_rounds_matchs(),
                    selected_tournament.get_tournament_players_by_score(),
                )

        next_menu = self.menu.get_action(chosen_option)
        return next_menu


class MenuExitController:
    """Manage the Exit menu."""

    def __init__(self):
        """Class init to hold the menu instance."""
        self.menu = None

    def run(self):
        """Manage the Exit menu."""
        self.menu = Menu("Quitter l'application")
        return MenuView(self.menu).good_bye()


MENU_HOME = {
    "10": ("Gérer les joueurs", MenuPlayerController()),
    "20": ("Gérer les tournois", MenuTournamentController()),
    "30": ("Gérer les rapports", MenuReportController()),
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
    "75": ("Clore un tournoi", MenuTournamentController()),
    "80": ("Retour à l'accueil", MenuController()),
    "90": ("Quitter l'application", MenuExitController()),
}

MENU_REPORT = {
    "10": ("Afficher les joueurs - ordre alphabétique", MenuReportController()),
    "20": ("Afficher les joueurs - classement ", MenuReportController()),
    "30": ("Afficher les joueurs d'un tournoi - ordre alphabétique", MenuReportController()),
    "40": ("Afficher les joueurs d'un tournoi - classement ", MenuReportController()),
    "45": ("Afficher les joueurs d'un tournoi - resultat ", MenuReportController()),
    "50": ("Afficher les tournois ", MenuReportController()),
    "60": ("Afficher les rondes d'un tournoi ", MenuReportController()),
    "70": ("Afficher les matchs d'un tournoi ", MenuReportController()),
    "80": ("Retour à l'accueil", MenuController()),
    "90": ("Quitter l'application", MenuExitController()),
}
