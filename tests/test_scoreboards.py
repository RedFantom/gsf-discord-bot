"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import os
import asyncio
from unittest import TestCase
# Project Modules
from parsing import scoreboards as sb
from utils.utils import get_assets_directory
# Packages
from PIL import Image


class MockBot(object):
    async def edit_message(self, *args):
        pass

    async def send_message(self, *args):
        pass


class Message(object):
    pass


class TestScoreboards(TestCase):
    def setUp(self):
        self.image = Image.open(os.path.join(get_assets_directory(), "tests", "test1.png"))

    def test_is_scoreboard(self):
        self.assertTrue(sb.is_scoreboard(self.image))

    def test_parse_scoreboard(self):
        for i in range(1, 5):
            path = os.path.join(get_assets_directory(), "tests", "test{}.png".format(i))
            image = Image.open(path)
            scale, location = sb.is_scoreboard(image)
            coroutine = sb.parse_scoreboard(image, scale, location, MockBot(), Message())
            results = asyncio.get_event_loop().run_until_complete(coroutine)
            self.assertIsInstance(results, list)
            self.assertEqual(len(results), 16)
            for row in results:
                self.assertEqual(len(results), len(sb.columns))
                for col in row:
                    self.assertIsInstance(col, (str, int))
            names = [row[0] for row in results]
            self.assertTrue("Redfantom" in names)
