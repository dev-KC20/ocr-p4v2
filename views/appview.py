#! /usr/bin/env Python3
# coding: utf-8
""" tournament view.
    """
from typing import List
import datetime
from utils.constants import CLEAR_TERMINAL, YESORNO, GENDER, CONTROLS, SCORE, ESCAPE_KEY

# use models for typing of classes
from models.player import Player
from models.tournament import Tournament

# from models.player import Player, Players


class View:
    def prompt(self, text, type_response, default_response=None, closed_response=None):
        """Attend une réponse conforme de l'utilisateur à l'input.
        text: le texte d'invite à afficher à l'utilisateur
        type_response: si test de valeur (int)>0 ou (date) attendu
        default_response:  si rien n'est saisi, cette valeur sera retournée
        closed_response: la réponse doit être une des valeurs de la liste

        Pour "échapper" la saisie en cours, le caractère unique est "@" pour abandonner

        """
        if not isinstance(text, str):
            raise Exception("Merci de vérifier le texte passé à prompt()")
        if closed_response is not None and not isinstance(closed_response, list):
            raise Exception("Merci de vérifier la liste passée à prompt()")
        if isinstance(default_response, str):
            default_response_print = default_response
        else:
            default_response_print = str(default_response)
        input_text = (
            text + " @ pour Esc " + " défaut=" + default_response_print + "):"
            if default_response is not None
            else " :"
        )
        while True:
            prompt_result = input(input_text)
            if prompt_result == ESCAPE_KEY:
                return None
            if default_response is not None and len(prompt_result) == 0:
                return default_response
            if len(prompt_result) != 0:
                # check and change the type of reply
                if type_response == "int":
                    if not prompt_result.isdigit():
                        print(
                            "Ce chiffre n'est pas valide, \
                            Merci de recommencer."
                        )
                    try:
                        prompt_result = int(prompt_result)
                    except ValueError:
                        print(
                            "Ce chiffre n'est pas valide, \
                            Merci de recommencer."
                        )
                        return None
                if type_response == "float":
                    # if isinstance(type(prompt_result), str):
                    if not prompt_result.replace(".", "", 1).isdigit():
                        print(
                            "Ce chiffre n'est pas valide, \
                            Merci de recommencer."
                        )
                    else:
                        try:
                            prompt_result = float(prompt_result)
                        except ValueError:
                            raise Exception(
                                "Ce chiffre n'est pas valide, \
                                Merci de recommencer."
                            ) from ValueError()
                        except RuntimeError:
                            raise Exception(
                                "Ce chiffre n'est pas valide, \
                                Merci de recommencer."
                            )
                if type_response == "date":
                    try:
                        j_j, m_m, aaaa = prompt_result.split("/")
                        datetime.datetime(int(aaaa), int(m_m), int(j_j))
                    except ValueError:
                        print(
                            "Cette date n'est pas valide, \
                                Merci de recommencer.",
                            ValueError(),
                        )
                # at this point the type was successfully checked
                if closed_response is not None:
                    if prompt_result in closed_response:
                        break
                # no error was raised previously, leave the loop
                else:
                    break
        return prompt_result

    def prompt_to_exit(self, text=None):

        exit_reply = View().prompt(
            text if text else "(Y + Enter) pour valider",
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
            print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print(" Créer un joueur ")
            print("*" * line_len)
            print()

            name = View().prompt("tapez le nom du joueur", "str", "Martin")
            firstname = View().prompt("tapez le prénom du joueur : ", "str", "Paul")
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

    def prompt_for_new_ranking(self):
        """Prompt for details."""
        while not self.play_once:
            # print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print(" Mettre à jour ELO ")
            print("*" * line_len)
            print()
            player_id = View().prompt("entrez l'id du joueur", "int", 1)
            player_elo = View().prompt("entrez le nouvel ELO du joueur : ", "int", 0)
            print()
            print("*" * line_len)
            self.play_once = View().prompt_to_exit()

        return player_id, player_elo


class PlayersView(View):
    def __init__(self):
        self.play_once = False

    def print_players(self, player_set: List[Player], ask_confirm=True):
        """ """
        while not self.play_once:
            print(" Liste des joueurs de la base")
            # move to models & call in controllers
            # player_set.sort(reverse=False)
            for joueur in player_set:
                if joueur is not None:
                    print(joueur)
            if ask_confirm:
                self.play_once = View().prompt_to_exit("(Entrée) pour continuer")
            else:
                self.play_once = True


class TournamentView(View):
    def __init__(self):
        self.play_once = False

    def prompt_for_tournament(self):
        """Prompt for details."""
        self.play_once = False
        while not self.play_once:
            print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print(" Créer un tournoi ")
            print("*" * line_len)
            print()

            name = View().prompt("tapez le nom du tournoi : ", "str", "Paris grand tournoi")
            description = View().prompt(
                "tapez une description du tournoi : ",
                "str",
                "Nous acceuillons nos voisins du 20eme.",
            )
            location = View().prompt("le lieu du tournoi : ", "str", "Paris 18e")
            start_date = View().prompt(
                "la date du tournoi (JJ/MM/AAAA): ",
                "date",
                datetime.date(2021, 12, 29).strftime("%d/%m/%Y"),
            )
            closing_date = View().prompt(
                "la date du tournoi (JJ/MM/AAAA): ",
                "date",
                datetime.date(2021, 12, 29).strftime("%d/%m/%Y"),
            )
            round_number = View().prompt("le nombre de ronde (défaut=4): ", "int", 4)
            time_control = View().prompt(
                "le type de partie : ",
                "str",
                CONTROLS[0],
                CONTROLS,
            )

            print()
            print("*" * line_len)
            self.play_once = View().prompt_to_exit()

        return (
            name,
            description,
            location,
            start_date,
            closing_date,
            round_number,
            time_control,
        )

    def prompt_for_tournament_id(self, tournament_set: List[Tournament]):
        """Prompt for id."""
        self.play_once = False
        tournament_id_set = []
        for tournoi in tournament_set:
            tournament_id_set.append(tournoi.get_tournament_id())

        while not self.play_once:
            print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print(" Choisir un tournoi ")
            print("*" * line_len)
            print()
            TournamentsView().print_tournaments(tournament_set, ask_confirm=False)

            tournament_id = View().prompt("entrez l'id du tournoi", "int", "", tournament_id_set)

            print()
            print("*" * line_len)
            # not asking confirmation to speed up UI

            if tournament_id is None:
                self.play_once = True

            if tournament_id in tournament_id_set:
                self.play_once = True
            # self.play_once = View().prompt_to_exit("Entrer pour valider")

        return tournament_id

    def prompt_for_player_id(self, player_set: List[Player]):
        """Prompt for id."""
        self.play_once = False
        while not self.play_once:
            print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print(" Choisir un joueur ")
            print("*" * line_len)
            print()
            PlayersView().print_players(player_set)
            player_id = View().prompt("entrez l'id du joueur", "int", 1)
            print()
            print("*" * line_len)
            # not asking confirmation to speed up UI
            self.play_once = True
            # self.play_once = View().prompt_to_exit("Entrer pour valider")

        return player_id


class TournamentsView(View):
    def __init__(self):
        self.play_once = False

    def print_tournaments(
        self,
        tournament_set: List[Tournament],
        player_set=None,
        ask_confirm=True,
    ):
        """ """
        while not self.play_once:
            print(" Liste des tournois de la base")
            tournament_set.sort(reverse=False)
            for tournoi in tournament_set:
                if tournoi is not None:
                    print(tournoi)
                    tournament_player_set = tournoi.get_tournament_players_by_rank()
                    registred_show = True
                    for joueur in tournament_player_set:
                        # find the player object based on player_id in tournament
                        if player_set is not None:
                            if joueur in player_set:
                                if registred_show:
                                    print("inscrits:")
                                    registred_show = False
                                # for participant in player_set:
                                #     if participant == joueur:
                                print(f" -> {joueur}")
                    for ronde, match_list in tournoi.get_tournament_rounds_matchs():
                        print(f" ==> {ronde}")
                        for jeu in match_list:
                            print(jeu)

            if ask_confirm:
                self.play_once = View().prompt_to_exit("(Entrée) pour continuer")
            else:
                self.play_once = True


class RoundView(View):
    def __init__(self):
        self.play_once = False

    def prompt_for_round_name(self, round_list):
        """Prompt for details."""
        self.play_once = False
        while not self.play_once:
            print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print("Choisir la ronde ")
            print("*" * line_len)
            print()
            # default to 1st element of the given list
            round_name = View().prompt("Entrée pour clore la ronde", "str", round_list[0], round_list)
            if round_name is None:
                self.play_once = True
            print()
            print("*" * line_len)
            self.play_once = True
            # self.play_once = View().prompt_to_exit()

        return round_name


class MatchView(View):
    def __init__(self):
        self.play_once = False

    def prompt_for_match_result(self, match_list):
        """Prompt for details."""
        self.play_once = False
        while not self.play_once:
            print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print(" Saisir le résultat des matchs ")
            print("*" * line_len)
            print()
            results_player1 = []
            for jeu in match_list:
                print(jeu)
                match_score1 = View().prompt(
                    "Saisir le resultat du joueur des blancs: " + str(jeu.get_match_player1()) + " : ",
                    "float",
                    SCORE[1],
                    SCORE,
                )

                results_player1.append(match_score1)

            print()
            print("*" * line_len)
            self.play_once = View().prompt_to_exit()

        return results_player1


class PlayersReportView(View):
    def __init__(self):
        self.play_once = False

    def print_players(self, player_set: List[Player], ask_confirm=True):
        """ """
        while not self.play_once:
            print(" Liste des joueurs de la base")
            # move to models & call in controllers
            # player_set.sort(reverse=False)
            for joueur in player_set:
                if joueur is not None:
                    print(joueur)
            if ask_confirm:
                self.play_once = View().prompt_to_exit("(Entrée) pour continuer")
            else:
                self.play_once = True


class TournamentsReportView(View):
    def __init__(self):
        self.play_once = False

    def prompt_for_tournament_id(self, tournament_set: List[Tournament]):
        """Prompt for id."""
        self.play_once = False
        tournament_id_set = []
        for tournoi in tournament_set:
            tournament_id_set.append(tournoi.get_tournament_id())

        while not self.play_once:
            print(CLEAR_TERMINAL)
            line_len = 50
            print("*" * line_len)
            print(" Choisir un tournoi ")
            print("*" * line_len)
            print()
            TournamentsReportView().print_tournaments(tournament_set, ask_confirm=False)

            tournament_id = View().prompt("entrez l'id du tournoi", "int", "", tournament_id_set)

            print()
            print("*" * line_len)
            # not asking confirmation to speed up UI

            if tournament_id is None:
                self.play_once = True

            if tournament_id in tournament_id_set:
                self.play_once = True
            # self.play_once = View().prompt_to_exit("Entrer pour valider")

        return tournament_id

    def print_tournaments_players(self, player_set=None, ask_confirm=True):
        """ """
        while not self.play_once:
            print(" Liste des joueurs du tournoi")
            registred_show = True
            for joueur in player_set:
                if registred_show:
                    print("inscrits:")
                    registred_show = False
                if isinstance(joueur, tuple):
                    print(f" -> {joueur[0]} à ce tournoi ==> {joueur[1]}")
                else:
                    print(f" -> {joueur} ")

            if ask_confirm:
                self.play_once = View().prompt_to_exit("(Entrée) pour continuer")
            else:
                self.play_once = True

    def print_tournaments_rounds(self, round_set=None, ask_confirm=True):
        """ """
        while not self.play_once:
            print(" Liste des rondes du tournoi")
            show_header = True
            for ronde in round_set:
                if show_header:
                    print("rondes:")
                    show_header = False
                if isinstance(ronde, tuple):
                    print(f" -> {ronde[0]} avec {len(ronde[1])} matchs")
                else:
                    print(f" -> {ronde} ")

            if ask_confirm:
                self.play_once = View().prompt_to_exit("(Entrée) pour continuer")
            else:
                self.play_once = True
    def print_tournaments_matchs(self, round_set=None, player_set=None, ask_confirm=True):
        """ """
        while not self.play_once:
            print(" Liste des rondes du tournoi")
            show_header = True
            for ronde in round_set:
                if show_header:
                    print("rondes:")
                    show_header = False
                if isinstance(ronde, tuple):
                    print(f" -> {ronde[0]} avec : ")
                    for jeu in ronde[1]:
                        print(jeu)
                else:
                    print(f" -> {ronde} ")

            if ask_confirm:
                self.play_once = View().prompt_to_exit("(Entrée) pour continuer")
            else:
                self.play_once = True

    def print_tournaments(
        self,
        tournament_set: List[Tournament],
        ask_confirm=True,
    ):
        """ """
        while not self.play_once:
            print(" Liste des tournois de la base")
            tournament_set.sort(reverse=False)
            for tournoi in tournament_set:
                if tournoi is not None:
                    print(f"{tournoi}")
                    print(
                        "Clos" if tournoi.get_tournament_score_status() else "Ouvert",
                        f" avec {len(tournoi.get_tournament_players())} inscrits",
                    )
                    if len(tournoi.get_tournament_rounds()) > 0:
                        print(f" joué en {len(tournoi.get_tournament_rounds()) } rondes ",
                              f" soient {len([j for i in tournoi.get_tournament_rounds() for j in i.get_matchs()]) } matchs.")

            if ask_confirm:
                self.play_once = View().prompt_to_exit("(Entrée) pour continuer")
            else:
                self.play_once = True
