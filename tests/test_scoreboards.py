"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import os
from unittest import TestCase
# Project Modules
from parsing import scoreboards as sb
from utils.utils import get_assets_directory
# Packages
from PIL import Image


class TestScoreboards(TestCase):
    def setUp(self):
        self.image = Image.open(os.path.join(get_assets_directory(), "tests", "test1.png"))

    def test_is_scoreboard(self):
        self.assertTrue(sb.is_scoreboard(self.image))

    def test_parse_scoreboard(self):
        results = sb.parse_scoreboard(self.image)
        self.assertIsInstance(results, list)
