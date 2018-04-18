"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from unittest import TestCase
# Project Modules
from database import DatabaseHandler


class TestDatabase(TestCase):
    def test_initialization(self):
        DatabaseHandler()

    def test_insert_user(self):
        command = None
