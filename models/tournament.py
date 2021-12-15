#! /usr/bin/env Python3
# coding: utf-8
""" tournament.
    """
import datetime
from utils.constants import ROUND_DEFAULT, CONTROLS, DB_TABLE_TOURNAMENT
from utils.database import Database
from .player import Player #, Players


class Match:
    """Match is the result of 2 players during one round."""

    def __init__(self):
        self._match_result = []

    def register_score(self, player_list, score_list):
        """Attach players and scores to the match."""
        self._match_result = list(zip(player_list, score_list))


class Round:
    """round is a list of matches"""

    def __init__(self, name, round_date, round_time):
        self._round_name = name
        self._round_start_date = round_date
        self._round_start_time = round_time
        self._round_end_date = None
        self._round_end_time = None
        self._matchs = [Match]

    def close_round(self):
        """closing a round."""
        self._round_end_date = datetime.date.today()
        self._round_end_time = datetime.datetime.now().time()

    def add_match(self, new_match: Match):
        """adding a match to a round."""
        self._matchs.append(new_match)

    def __str__(self):
        return f" Ronde {self._round_name} débuté\
             le {self._round_start_date} à {self._round_start_time} "


class Tournament:
    """tournament is a set of players and rounds they had."""

    def __init__(
        self,
        name,
        description,
        location,
        start_date: datetime,
        closing_date: datetime,
        round_number=ROUND_DEFAULT,
        time_control=CONTROLS[0],
        tournament_id=0,
    ):
        self._event_name = name
        self._event_description = description
        self._event_location = location
        self._event_start_date = start_date
        self._event_closing_date = closing_date
        self._round_number = int(round_number)
        self._time_control = time_control
        self._rounds = []
        self._players = []
        self.__id = tournament_id
        self._formated_tournament = f"""id: {self.__id} {self._event_name} à {self._event_location} du {self._event_start_date} au {self._event_closing_date} avec {self._round_number} rondes en mode {self._time_control} """

    def __str__(self):
        return self._formated_tournament

    def get_id(self):
        """player_id getter"""
        return self.__id

    def get_tournament_players(self):
        """list of participants getter"""
        return self._players

    def get_tournament_rounds(self):
        """list of rounds getter"""
        return self._rounds

    def add_player_to_tournament(self, new_player: Player):
        """ask for and register a player to the tournament."""
        self._players.append(new_player)

    def close_tournament(self):
        """close the tournament"""
        self._event_closing_date = datetime.date.today()

    def add_round(self, new_round: Round):
        """add a round to the tournament."""
        if len(self._rounds) <= self._round_number:
            self._rounds.append(new_round)

    def serialize_tournament(self):
        """provide serialized version of one tournament"""

        serialized_players = []
        for joueur in self._players:
            serialized_players.append(joueur.serialize_player())

         
        return {
            "tournament_id": self.__id,
            "tournament_name": self._event_name,
            "tournament_description": self._event_description,
            "tournament_location": self._event_location,
            "tournament_start_date": self._event_start_date,
            "tournament_closing_date": self._event_closing_date,
            "tournament_round_number": self._round_number,
            "tournament_time_control": self._time_control,
            "tournament_players": serialized_players,
            "tournament_rounds": self._rounds,
        }


    def save_tournament(self, new_tournament, tournament_id=None):
        """Save one tournament

        Save uses the fact that a class has a description as dictionnary
        the meta structure record is avoided.
        """
        if tournament_id is None:
            Database().set_table(
                DB_TABLE_TOURNAMENT, new_tournament.serialize_tournament()
            )
        else:
            Database().set_table(
                DB_TABLE_TOURNAMENT,
                new_tournament.serialize_tournament(),
                tournament_id,
            )


class Tournaments:
    """List of tournaments."""

    def __init__(self):
        self._tournaments = []

    def get_list_of_tournaments(self):
        """list of all tournaments"""
        return self._tournaments

    def get_tournament_by_id(self, tournament_id):
        """return one tournament based on its id"""
        found_tournament = None
        for tournament in self._tournaments:
            if tournament.get_id() == tournament_id:
                found_tournament = tournament
        return found_tournament

    def load_tournaments(self):
        """Load saved tournaments into Tournaments()"""
        __serialized_tournaments = []
        __serialized_tournaments = Database().get_table_all(
            DB_TABLE_TOURNAMENT
        )
        for tournoi in __serialized_tournaments:
            self._tournaments.append(
                Tournament(
                    tournoi["tournament_name"],
                    tournoi["tournament_description"],
                    tournoi["tournament_location"],
                    tournoi["tournament_start_date"],
                    tournoi["tournament_closing_date"],
                    tournoi["tournament_round_number"],
                    tournoi["tournament_time_control"],
                    tournoi["tournament_id"],
                )
            )
        print(f" {len(self._tournaments)} tournois chargés")
