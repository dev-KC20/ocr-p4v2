#! /usr/bin/env python
# coding: utf-8
"""all constants for chess tournaments manager.


"""

import datetime

CLEAR_TERMINAL = " "
# CLEAR_TERMINAL = chr(27) + "[2J"
GENDER = ["No", "M", "F"]
YESORNO = ["Y", "N"]
CONTROLS = ["bullet", "blitz", "fast"]
TEST_FIRSTNAME_SLICE = 2
TEST_START_DATE = datetime.date(1940, 1, 1)
TEST_END_DATE = datetime.date(2000, 1, 1)
ROUND_DEFAULT = 4
DATEFORMATTER = "%d/%m/%Y"
DB_LOCATION = "./data/dbtest.json"
DB_TABLE_PLAYER = "players"
DB_TABLE_TOURNAMENT = "tournaments"
SCORE = [0.0, 0.5, 1.0]
ROUND_STATUS = {0: "encours", 1: "finie", 2: "close"}
