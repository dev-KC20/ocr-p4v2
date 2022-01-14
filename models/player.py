#! /usr/bin/env Python3
# coding: utf-8
"""Player who will participate to the tournament."""
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
        point_earned=0.0,
        player_id=0
    ):
        """Player class init is a name, its ELO ranking & last score."""
        self.__name = name
        self.__firstname = firstname
        self.__birthdate = birthdate
        self.__gender = gender
        self.__initial_ranking = initial_ranking
        self.__score = point_earned
        self.__player_id = player_id
        # self.__opponent_met = [opponent_met]
        self._formated_player = " ".join(
            [
                str(self.__player_id),
                self.__gender,
                self.__firstname,
                self.__name,
                # "né",
                # str(self.__birthdate),
                str(self.__initial_ranking),
                " ELO  and earned ",
                str(self.__score),
                " points ",
            ]
        )

    # sort by rank
    def __lt__(self, obj):
        """Less than to enable sorting btw players.

        input: obj is one player's id of type integer
        """
        return (self.__initial_ranking) < (obj)
        # return (self.__initial_ranking) < (obj.get_ranking())

    def __eq__(self, obj):
        """Equal to enable sorting btw players.

        input: obj is one player's id of type integer
        """
        return (self.__initial_ranking) == (obj)
        # return (self.__initial_ranking) == (obj.get_ranking())

    # sort by id
    # def __lt__(self, obj):
    #     return (self.__player_id) < (obj.get_player_id())

    # def __eq__(self, obj):
    #     return (self.__player_id) == (obj.get_player_id())

    def get_name(self):
        """Name getter."""
        return self.__name

    def get_player_id(self):
        """Player_id getter."""
        return self.__player_id

    def get_score(self):
        """Player score getter."""
        return self.__score

    def set_ranking(self, ranking):
        """Update the player rank according to match result."""
        self.__initial_ranking = ranking

    # def get_opponent_met(self):
    #     """list of opponent the player already met getter"""
    #     return self.__opponent_met

    # def set_opponent_met(self, opponent):
    #     """The player rank is updated according to match result."""
    #     self.__opponent_met.append(opponent)

    def get_ranking(self):
        """Player rank getter."""
        return self.__initial_ranking

    def set_score(self, score):
        """Update the player rank according to match result."""
        self.__score += score

    def __str__(self):
        """Improve readability when printed."""
        return self._formated_player

    def serialize_player(self):
        """Serialise one player."""
        return {
            "name": self.__name,
            "firstname": self.__firstname,
            "birthdate": self.__birthdate,
            "gender": self.__gender,
            "initial_ranking": self.__initial_ranking,
            "score": self.__score,
            # "opponent_met": self.__opponent_met,
            "player_id": self.__player_id
        }

    def save_player(self, new_player, player_id=None):
        """Save one player.

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
        """Players class init is just a list of players."""
        self.__players_known = []

    def add_player_to_list(self, new_player: Player):
        """Register a player to the local list of player."""
        self.__players_known.append(new_player)
        return True

    def get_number_of_players(self):
        """Get the number of players."""
        return len(self.__players_known)

    def get_list_of_players(self):
        """Get the list of players."""
        return self.__players_known

    def get_players_by_name(self):
        """Get the list of all players sorted by last name."""
        self.__players_known.sort(key=lambda x: x.get_name(), reverse=True)
        return self.__players_known

    def get_players_by_rank(self):
        """Get a list of all players sorted by initial_ranking."""
        self.__players_known.sort(key=lambda x: x.get_ranking(), reverse=True)
        return self.__players_known

    def get_players_by_score(self):
        """Get a list of all players sorted by score then rank."""
        self.__players_known.sort(
            key=lambda x: (x.get_score(), x.get_ranking()), reverse=True
        )
        return self.__players_known

    def get_player_by_id(self, player_id):
        """Get one player instance based on his id."""
        found_player = None
        for player in self.__players_known:
            if player.get_player_id() == player_id:
                found_player = player
        return found_player

    def load_players(self):
        """Load saved players into Players()."""
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
                    # float(joueur["score"]), # by default  it converts into float I believe
                    # joueur["opponent_met"],
                    joueur["player_id"]
                )
            )
        # print(f" {len(self.__players_known)} joueurs chargés")

    def serialize_players(self):
        """Serialize list of players."""
        _serialized_players = []
        for joueur in self.__players_known:
            # only append data records
            if joueur.__dict__.get("_name"):
                _serialized_players.append(joueur.__dict__)
            print(_serialized_players)
        return _serialized_players
