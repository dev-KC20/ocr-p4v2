#! /usr/bin/env Python3
# coding: utf-8
""" tournament.
    """
from datetime import datetime, date
from utils.constants import ROUND_DEFAULT, CONTROLS, DB_TABLE_TOURNAMENT
from utils.database import Database
from .player import Players  # Player,


class Match:
    """Match is the result of 2 players during one round."""

    def __init__(self, player1_id, player2_id):
        self._player1_id = player1_id
        self._player2_id = player2_id
        self._score_1 = 0.0
        self._score_2 = 0.0
        self._formated_match = (
            [self._player1_id, self._score_1],
            [self._player2_id, self._score_2],
        )

    def __repr__(self):
        return (
            f"""([{self._player1_id}, {self._score_1}],"""
            f"""[{self._player2_id}, {self._score_2}])"""
        )

    def __str__(self):
        return (
            f""" ====>  blanc {self._player1_id}: {self._score_1},"""
            f"""noir {self._player2_id}: {self._score_2} """
        )

    def set_match_score(self, score_1):
        """score setter."""
        self._score_1 = float(score_1)
        self._score_2 = 1.0 - self._score_1

    def get_match(self):
        """returns match formatted."""
        return self._formated_match

    def get_match_score1(self):
        """returns score of player 1."""
        return self._score_1

    def get_match_score2(self):
        """returns score of player 2."""
        return self._score_2

    def get_match_player1(self):
        """returns match formatted."""
        return self._player1_id

    def get_match_player2(self):
        """returns match formatted."""
        return self._player2_id

    def is_match_closed(self):
        """Attach players and scores to the match."""
        if self._score_1 + self._score_2 == 1.0:
            match_closed = True
        else:
            match_closed = False
        return match_closed

    def serialize_match(self):
        """provide serialized version of one match"""

        return (
            [str(self._player1_id), str(self._score_1)],
            [str(self._player2_id), str(self._score_2)],
        )


class Round:
    """round is a list of matches"""

    def __init__(
        self,
        name,
        round_date,
        round_time,
        round_end_date=None,
        round_end_time=None,
        matchs=None,
    ):
        self._round_name = name
        self._round_start_date = round_date.strftime("%d/%m/%Y")
        self._round_start_time = round_time.strftime("%Hh%Mm%Ss")
        self._round_end_date = round_end_date
        self._round_end_time = round_end_time
        self._matchs = [] if not matchs else matchs
        self._round_status = "Vide"

    def get_round_name(self):
        """round name getter."""
        return self._round_name

    def get_round_status(self):
        """status of one round getter."""
        if self._round_start_date:
            self._round_status = "En cours"
        if self._round_end_date:
            # at leat one match has a score
            for jeu in self._matchs:
                if (
                    jeu.get_match_score1() == 0.0
                    and jeu.get_match_score2() == 0.0
                ):
                    self._round_status = "Finie"
                if (
                    jeu.get_match_score1() != 0.0
                    or jeu.get_match_score2() != 0.0
                ):
                    self._round_status = "Close"
        return self._round_status

    def close_round(self):
        """closing a round."""
        self._round_end_date = date.today().strftime("%d/%m/%Y")
        self._round_end_time = datetime.now().time().strftime("%Hh%Mm%Ss")

    def add_match(self, new_match):
        """adding a match to a round from a list."""
        self._matchs.append(Match(new_match[0], new_match[1]))

    def remove_matchs(self):
        """remove the list of match attached to the round."""
        self._matchs = []

    def get_matchs(self):
        """match list getter."""
        return self._matchs

    def serialize_datetime(self, date_time_object):
        """support json serialization of datatime objects"""
        if isinstance(date_time_object, datetime.datetime):
            return date_time_object.__str__()
        elif isinstance(date_time_object, datetime.date):
            return date_time_object.__str__()
        else:
            return date_time_object

    def __str__(self):
        return (
            f""" {self._round_name} état: {self.get_round_status()} """
            f""" a débuté {self._round_start_date} à {self._round_start_time} """
        )

    def serialize_round(self):
        """provide serialized version of one round"""
        matchs_serialized = []
        for match in self._matchs:
            matchs_serialized.append(match.serialize_match())
        return {
            "round_name": self._round_name,
            "round_start_date": self._round_start_date,
            "round_start_time": self._round_start_time,
            "round_end_date": self._round_end_date,
            "round_end_time": self._round_end_time,
            "round_matchs": matchs_serialized,
        }


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
        self._formated_tournament = (
            f"""id: {self.__id} {self._event_name} à {self._event_location}"""
            f""" du {self._event_start_date} au {self._event_closing_date} """
            f""" avec {self._round_number} rondes en mode {self._time_control} """
        )

    def __lt__(self, obj):
        return (self.__id) < (obj.get_id())

    def __eq__(self, obj):
        return (self.__id) == (obj.get_id())

    def __str__(self):
        return self._formated_tournament

    def get_id(self):
        """tournament_id getter"""
        return self.__id

    def get_tournament_players(self):
        """list of participant's id getter"""
        return self._players

    def get_tournament_round_number(self):
        """max of round  getter"""
        return self._round_number

    def get_tournament_rounds(self):
        """list of rounds & matchs getter

        output: list of tuples (ronde, list of matchs)
        """
        list_rounds = []
        for ronde in self._rounds:
            # appends a list of the matchs of ronde
            list_rounds.append((ronde, ronde.get_matchs()))
        # also print round date&time
        return list_rounds

    def get_tournament_players_by_rank(self):
        """list of participant's id sorted by rank getter"""
        list_players = []
        # get the full player from player_id
        player_list_db = Players()
        player_list_db.load_players()
        # build a list of Player class from the id's in tournament
        for player_id in self._players:
            player_object = player_list_db.get_player_by_id(player_id)
            # player removed from DB in meantime
            if player_object is not None:
                list_players.append(player_object)
        # sort the list of Player by rank
        if len(list_players) > 0:
            list_players.sort(key=lambda x: x.get_ranking(), reverse=True)

        return list_players

    def pair_players_first_time(self):
        """takes the list of player registred sort it by rank and split in two half"""
        list_players = []
        # get the full player from player_id
        player_list_db = Players()
        player_list_db.load_players()
        # build a list of player's attributs from the ones in tournament
        for player_id in self._players:
            player_object = player_list_db.get_player_by_id(player_id)
            # player removed from DB in meantime
            if player_object is not None:
                list_players.append(
                    [
                        player_id,
                        player_object.get_ranking(),
                        player_object.get_score(),
                        player_object.get_opponent_met,
                    ]
                )
        # sort the list of Player by rank
        number_participants = len(list_players)
        if number_participants > 0:
            list_players.sort(key=lambda x: x[1], reverse=True)
            pairing_list_first_half = list_players[
                : int(number_participants / 2)
            ]
            # participant # is odd
            participants_is_odd = False
            if (number_participants % 2) == 1:
                print("nombre de joueur impair, le dernier gagne un point")
                list_players[number_participants - 1][2] = 1
                participants_is_odd = True
                # pairing_list = list_players[number_participants - 1]
                pairing_list_second_half = list_players[
                    int(number_participants / 2) : number_participants - 1
                ]
            else:
                pairing_list_second_half = list_players[
                    int(number_participants / 2) : number_participants
                ]
            match_list = [
                (pairing_list_first_half[i][0], pairing_list_second_half[i][0])
                for i in range(len(pairing_list_first_half))
            ]
            print(match_list)

        return (
            match_list,
            list_players[number_participants - 1][0]
            if participants_is_odd
            else None,
        )

    def add_player_to_tournament(self, new_player: int):
        """ask for and register a player to the tournament."""
        if new_player not in self._players:
            self._players.append(new_player)

    def add_players_to_tournament(self, new_player: list):
        """ask for and register player's ids to the tournament."""
        self._players.extend(new_player)

    def close_tournament(self):
        """close the tournament"""
        self._event_closing_date = date.today()

    def add_round(self, new_round: Round):
        """add a round to the tournament."""
        if len(self._rounds) <= self._round_number:
            self._rounds.append(new_round)

    def serialize_tournament(self):
        """provide serialized version of one tournament"""
        rounds_serialized = []
        for ronde in self._rounds:
            rounds_serialized.append(ronde.serialize_round())

        return {
            "tournament_id": self.__id,
            "tournament_name": self._event_name,
            "tournament_description": self._event_description,
            "tournament_location": self._event_location,
            "tournament_start_date": self._event_start_date,
            "tournament_closing_date": self._event_closing_date,
            "tournament_round_number": self._round_number,
            "tournament_time_control": self._time_control,
            "tournament_players": self._players,
            "tournament_rounds": rounds_serialized,
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

    def load_round(self, serialized_rounds):
        """Load saved rounds into class Round()

        input: dict of one round
        """
        list_serialized_matchs = []
        # TODO: registred result to be included
        for i in serialized_rounds["round_matchs"]:
            list_serialized_matchs.append(Match(i[0][0], i[1][0]))
            # add scores str -> float to the serialized match
        # print("list_serialized_matchs", list_serialized_matchs)
        # print(
        #     "serialized_rounds['round_matchs']",
        #     serialized_rounds["round_matchs"],
        # )
        self._rounds.append(
            Round(
                serialized_rounds["round_name"],
                datetime.strptime(
                    serialized_rounds["round_start_date"], "%d/%m/%Y"
                ),
                datetime.strptime(
                    serialized_rounds["round_start_time"], "%Hh%Mm%Ss"
                ),
                serialized_rounds["round_end_date"],
                serialized_rounds["round_end_time"],
                list_serialized_matchs,
            )
        )

    def load_tournament(self, tournament_id):
        """Load one saved tournament into Tournament()"""
        __serialized_tournament = Database().get_table_id(
            DB_TABLE_TOURNAMENT, tournament_id
        )

        tournoi = Tournament(
            __serialized_tournament["tournament_name"],
            __serialized_tournament["tournament_description"],
            __serialized_tournament["tournament_location"],
            __serialized_tournament["tournament_start_date"],
            __serialized_tournament["tournament_closing_date"],
            __serialized_tournament["tournament_round_number"],
            __serialized_tournament["tournament_time_control"],
            __serialized_tournament["tournament_id"],
        )

        # [M] it looks weird here ; isn't there a better pythonic way?
        # access to the last appended Tournament & add its players
        tournoi.add_players_to_tournament(
            __serialized_tournament["tournament_players"]
        )
        # access to the last appended Tournament & add its rounds
        # "tournament_rounds" deserialized added 1by1 to former added class Tournaments
        for ronde in __serialized_tournament["tournament_rounds"]:
            tournoi.load_round(ronde)


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
            # first append one tournament to self._tournaments
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
            # [M] it looks weird here ; isn't there a better pythonic way?
            # access to the last appended Tournament & add its players
            self._tournaments[-1].add_players_to_tournament(
                tournoi["tournament_players"]
            )
            # access to the last appended Tournament & add its rounds
            # "tournament_rounds" deserialized added 1by1 to former added class Tournaments
            for ronde in tournoi["tournament_rounds"]:
                self._tournaments[-1].load_round(ronde)
