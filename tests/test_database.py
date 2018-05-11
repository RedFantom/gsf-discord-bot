"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from datetime import datetime
import os
from unittest import TestCase
# Project Modules
from database import DatabaseHandler
from database import create
from utils import utils
from utils.utils import DATE_FORMAT, TIME_FORMAT
utils.STDOUT = True


class TestDatabase(TestCase):
    CREATE_PREFIX = "CREATE_TABLE_"
    TEST_TAG = "@TestUser#1111"
    TEST_CHAR = "Test Character"
    TEST_SERVER = "DM"
    TEST_FACTION = "IMP"
    TEST_OWNER = TEST_TAG
    TEST_DATE = datetime.now().strftime(DATE_FORMAT)
    TEST_TIME = datetime.now().strftime(TIME_FORMAT)

    TABLE_SELECT = "SELECT name FROM sqlite_master WHERE type='table';"

    def setUp(self):
        self.db = DatabaseHandler()

    def test_exec_query(self):
        tables = self.db.exec_query(self.TABLE_SELECT)
        self.assertNotEqual(len(tables), 0)

    def test_initialization(self):
        tables = self.db.exec_query(self.TABLE_SELECT)
        tables = list(map(str.lower, [table[0] for table in tables]))
        attrs = dir(create)
        for attr in attrs:
            if not attr.startswith(self.CREATE_PREFIX):
                continue
            table = attr[len(self.CREATE_PREFIX):].lower()
            self.assertTrue(table in tables)

    def test_insert_user(self):
        self.db.insert_user(self.TEST_TAG, "123456")
        self.assertTrue(self.db.get_user_in_database(self.TEST_TAG))

    def test_insert_character(self):
        self.db.insert_character(
            self.TEST_CHAR, self.TEST_SERVER, self.TEST_FACTION, self.TEST_OWNER)
        char = self.db.get_character_id(self.TEST_SERVER, self.TEST_CHAR)
        self.assertEqual(char, 1)

    def test_update_auth_code(self):
        self.db.insert_user(self.TEST_TAG, "123456")
        self.db.update_auth_code(self.TEST_TAG, "234567")
        self.assertEqual(self.db.get_auth_code(self.TEST_TAG), "234567")

    def test_insert_match_and_update_match(self):
        self.db.insert_match(
            self.TEST_SERVER, self.TEST_DATE, self.TEST_TIME, "123456")
        result = self.db.get_match_id(
            self.TEST_SERVER, self.TEST_DATE, "123456")
        self.assertEqual(result, 1)

        self.db.update_match(
            self.TEST_SERVER, self.TEST_DATE, self.TEST_TIME, "123456",
            map="tdm,io", end=datetime.now().strftime(TIME_FORMAT), score=0.65)

        matches = self.db.get_matches_by_day_by_server(self.TEST_SERVER, self.TEST_DATE)
        start, end, map, score = matches[0]
        self.assertEqual(start, self.TEST_TIME)
        self.assertEqual(map, "tdm,io")
        self.assertEqual(score, 0.65)

    def insert_result(self):
        self.test_insert_character()
        self.db.insert_result(
            self.TEST_CHAR, self.TEST_SERVER, self.TEST_DATE, self.TEST_TIME,
            "123456", 1, 100, 1000, 10, "T1G")
        results = self.db.get_match_results(self.TEST_SERVER, self.TEST_DATE, self.TEST_TIME)
        self.assertEqual(len(results), 1)
        name, faction, dmgd, dmgt, assists, deaths, ship = results[0]
        self.assertEqual(self.TEST_CHAR, name)
        self.assertEqual(self.TEST_FACTION, faction)
        self.assertEqual(1, assists)
        self.assertEqual(100, dmgd)
        self.assertEqual(1000, dmgt)
        self.assertEqual(10, deaths)
        self.assertEqual("T1G", ship)

    def tearDown(self):
        os.remove("database.db")

