"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Packages
from discord import TextChannel as Channel, User as DiscordUser
# Project Modules
from bot.messages import *
from utils import generate_tag, generate_code, hash_auth


async def register(self, channel: Channel, user: DiscordUser, args: tuple):
    """Register a new user into the database"""
    tag = generate_tag(user)
    self.logger.debug("Initializing registration of a user: {}".format(tag))
    if self.db.get_auth_code(tag) is not None:
        await self.send_message(channel, ALREADY_REGISTERED)
        self.logger.debug("{} is already registered.".format(tag))
        return
    code = generate_code()
    message = UPON_REGISTER.format(code)
    self.logger.debug("Sending registration message to {}.".format(tag))
    await self.send_message(user, message)
    self.logger.info("Registering new user {}.".format(tag))
    self.db.insert_user(generate_tag(user), hash_auth(code))
    self.logger.debug("Sending public registration message to {}.".format(channel.name))
    await self.send_message(channel, UPON_REGISTER_PUBLIC)


async def unregister(self, channel: Channel, user: DiscordUser, args: tuple):
    """Remove a user fully from the database"""
    tag = generate_tag(user)
    self.db.delete_user(tag)
    self.logger.info("Unregistered {}.".format(tag))
    await self.send_message(channel, UNREGISTER_PUBLIC)
    await self.send_message(user, UNREGISTER)


async def forgot_code(self, channel: Channel, user: DiscordUser, args: tuple):
    """Generate a new access code for the user"""
    tag = generate_tag(user)
    self.logger.info("Generating new access code for {}.".format(tag))
    code = generate_code()
    self.db.update_auth_code(tag, code)
    await self.send_message(user, NEW_CODE.format(code))

