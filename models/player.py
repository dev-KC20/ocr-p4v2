#! /usr/bin/env Python3
# coding: utf-8
""" Player who will participate to the tournament.
    """
from utils.database import Database
from utils.constants import DB_TABLE_PLAYER


class Player:
    """Person attending a chess tournament."""

    def __init__(
        self,
        name,
        firstname,
        birthdate,
        gender,
        initial_ranking,
        point_earned=0,
        opponent_met=None,
        player_id=0,
    ):
        self.__name = name
        self.__firstname = firstname
        self.__birthdate = birthdate
        self.__gender = gender
        self.__initial_ranking = initial_ranking
        self.__score = point_earned
        self.__id = player_id
        self.__opponent_met = opponent_met
        self._formated_player = f"""id: {self.__id}: {self.__firstname} {self.__name},\
             né {self.__birthdate} {self.__initial_ranking} ELO, score: {self.__score} genre:\
                  {self.__gender} """

    def get_name(self):
        """name getter"""
        return self.__name

    def get_id(self):
        """player_id getter"""
        return self.__id

    def get_ranking(self):
        """player rank getter"""
        return self.__initial_ranking

    def set_ranking(self, ranking):
        """The player rank is updated according to match result."""
        self.__initial_ranking = ranking

    def get_opponent_met(self):
        """list of opponent the player already met getter"""
        return self.__opponent_met

    def set_opponent_met(self, opponent):
        """The player rank is updated according to match result."""
        self.__opponent_met = opponent

    def set_score(self, score):
        """The player rank is updated according to match result."""
        self.__score += score

    def __str__(self):

        return self._formated_player

    def serialize_player(self):
        """provide serialized version of one player"""
        return {
            "name": self.__name,
            "firstname": self.__firstname,
            "birthdate": self.__birthdate,
            "gender": self.__gender,
            "initial_ranking": self.__initial_ranking,
            "score": self.__score,
            "opponent_met": self.__opponent_met,
            "player_id": self.__id,
        }

    def save_player(self, new_player, player_id=None):
        """Save one player
        Save uses the fact that a class has a description as dictionnary
        the meta structure record is avoided.
        """
        if player_id is None:
            Database().set_table(
                DB_TABLE_PLAYER, new_player.serialize_player()
            )
        else:
            Database().set_table(
                DB_TABLE_PLAYER, new_player.serialize_player(), player_id
            )


class Players:
    """List of know chess players."""

    def __init__(self):
        self.__players_known = []

    def add_player_to_list(self, new_player: Player):
        """register a player to the local list of player."""
        self.__players_known.append(new_player)
        return True

    def get_number_of_players(self):
        """number of player."""
        return len(self.__players_known)

    def get_list_of_players(self):
        """list of all players"""
        return self.__players_known

    def get_player_by_id(self, player_id):
        """return one player based on his id"""
        found_player = None
        for player in self.__players_known:
            if player.get_id() == player_id:
                found_player = player
        return found_player

    def load_players(self):
        """Load saved players into Players()"""
        __serialized_players = []
        __serialized_players = Database().get_table_all(DB_TABLE_PLAYER)
        for joueur in __serialized_players:
            self.__players_known.append(
                Player(
                    joueur["name"],
                    joueur["firstname"],
                    joueur["birthdate"],
                    joueur["gender"],
                    joueur["initial_ranking"],
                    joueur["score"],
                    joueur["opponent_met"],
                    joueur["player_id"],
                )
            )
        print(f" {len(self.__players_known)} joueurs chargés")

    def serialize_players(self):
        """Serialize list of players"""

        _serialized_players = []
        for joueur in self.__players_known:
            # only append data records
            if joueur.__dict__.get("_name"):
                _serialized_players.append(joueur.__dict__)
        return _serialized_players

    # def save_players(self):
    #     """Save players
    #     Save uses the fact that a class has a description as dictionnary
    #     the meta structure record is avoided.
    #     """

    #     _serialized_players = []
    #     # _self.players_table.truncate()
    #     for joueur in self.__players_known:
    #         # only append data records
    #         if joueur.__dict__.get("_name"):
    #             _serialized_players.append(joueur.__dict__)
    #     Database().set_table_all(DB_TABLE_PLAYER, _serialized_players)
    #     print(f" {len(_serialized_players)} joueurs sauvés")
