#! /usr/bin/env Python3
# coding: utf-8
""" tournament view.
    """
from typing import List
import datetime
from utils.constants import CLEAR_TERMINAL, YESORNO, GENDER
from models.player import Player

# from models.player import Player, Players


class View:

    def prompt(self,
        text, type_response, default_response=None, closed_response=None
    ):
        """Attend une réponse conforme de l'utilisateur à l'input.
        text: le texte d'invite à afficher à l'utilisateur
        type_response: si test de valeur (int)>0 ou (date) attendu
        default_response:  si rien n'est saisi, cette valeur sera retournée
        closed_response: la réponse doit être une des valeurs de la liste
        """
        if not isinstance(text, str):
            raise Exception("Merci de vérifier le texte passé à prompt()")
        if closed_response is not None and not isinstance(
            closed_response, list
        ):
            raise Exception("Merci de vérifier la liste passée à prompt()")
        if isinstance(default_response, str):
            default_response_print = default_response
        else:
            default_response_print = str(default_response)
        input_text = (
            text + " (defaut:" + default_response_print + "):"
            if default_response is not None
            else " :"
        )
        while True:
            prompt_result = input(input_text)
            if default_response is not None and len(prompt_result) == 0:
                return default_response
            if len(prompt_result) != 0:
                if type_response == "int":
                    try:
                        if int(prompt_result) > 0:
                            break
                    except ValueError:
                        raise Exception(
                            "Ce chiffre n'est pas valide, \
                            Merci de recommencer."
                        ) from ValueError()
                if type_response == "date":
                    try:
                        jj, mm, aaaa = prompt_result.split("/")
                        datetime.datetime(int(aaaa), int(mm), int(jj))
                    except ValueError:
                        raise Exception(
                            "Cette date n'est pas valide, \
                                Merci de recommencer."
                        ) from ValueError()
                    else:
                        break
                if closed_response is not None:
                    if prompt_result in closed_response:
                        break
                if type_response == "str" and isinstance(prompt_result, str):
                    break
        return prompt_result

    def prompt_to_exit(self):

        exit_reply = View().prompt(
            "Voulez-vous quittez? (Y/N)",
            "str",
            "Y",
            YESORNO,
        )
        print(exit_reply)
        return True if exit_reply == "Y" else False


class PlayerView(View):
    def __init__(self):
        self.play_once = False

    def prompt_for_player(self):
        """Prompt for details."""
        while not self.play_once:
            # print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print(" Créer un joueur ")
            print("*" * line_len)
            print()

            name = View().prompt("tapez le nom du joueur", "str", "Martin")
            firstname = View().prompt(
                "tapez le prénom du joueur : ", "str", "Paul"
            )
            birthdate = View().prompt(
                "sa date de naissance (JJ/MM/AAAA): ",
                "date",
                datetime.date(2000, 1, 1).strftime("%d/%m/%Y"),
            )
            gender = View().prompt(
                "si indispensable, préciser le genre: ",
                "str",
                GENDER[0],
                GENDER,
            )
            initial_ranking = View().prompt("son classement ELO : ", "int", 800)
            print()
            print("*" * line_len)
            self.play_once = View().prompt_to_exit()

        return name, firstname, birthdate, gender, initial_ranking


class PlayersView(View):
    def __init__(self):
        self.play_once = False

    def print_players(self, player_set: List[Player]):
        """ """
        while not self.play_once:
            print(" Liste des joueurs de la base")
            # print(player_set)
            for joueur in player_set:
                # if joueur is not None:
                print(joueur)
            self.play_once = View().prompt_to_exit()
