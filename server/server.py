"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
import traceback
from semantic_version import Version
# Project Modules
from database import DatabaseHandler
from utils import setup_logger, hash_auth


class Server(object):
    """
    Parent class for DiscordServer and SharingServer. Each Server
    executes its own functionality in the same manner.
    1. The asyncio loop checks for clients once the server is started.
    2. When a Client connects, the handle_client function is called.
    3. The handle_client function authenticates the client and
       starts the processing of received data with a process_command
       instance function.
    4. The result of the process_command function is sent back to the
       client, after which the connection is closed. Each command
       requires a new connection.
    """

    MAX_ATTEMPTS = 50
    BUFFER_SIZE = 32
    MIN_VERSION = "v5.0.0"

    def __init__(self, database: DatabaseHandler, host: str, port: int, name: str="Server"):
        """
        :param database: DatabaseHandler instance
        :param host: Hostname to bind the server to
        :param port: Port number to bind the server to
        """
        log_file = name.replace("Server", "").lower() + ".log"
        self.logger = setup_logger(name, log_file)
        self.db = database
        self.host, self.port = host, port

    async def start(self):
        """Start the server in the asyncio loop"""
        self.logger.info("Initiating server ({}, {})...".format(self.host, self.port))
        await asyncio.start_server(self.handle_client, self.host, self.port)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """
        Authenticate the connecting client and read the command from the
        stream. The command is decoded and passed to the
        process_command function, where execution should happen.
        The result of the process_command function is sent back to the
        client.
        """
        self.logger.debug("Accepted a new client.")
        try:
            self.logger.debug("Reading command from client...")
            command = await self.read_command(reader)
            split = await self.split_command(command)
            if split is None:
                raise ValueError("Command split failed")
            # Authenticate the user and check version
            tag, auth, version, command, args = split
            if self.authenticate_user(tag, auth) is False:
                writer.write(b"unauth")
                raise PermissionError("Unauthorized usage")
            if self.check_version(version) is False:
                writer.write(b"version")
                raise ValueError("Version mismatch")
            # Process the command
            result = await self.process_command(tag, command, args)
            if result is None:  # Command execution failed
                self.logger.error("Command execution failed: {}, {}".format(command, args))
                writer.write(b"error")
                raise RuntimeError("Command execution failed")
            to_write = result.encode()
            writer.write(to_write)
        except Exception:
            self.logger.error("Client handling failed:\n{}".format(traceback.format_exc()))
        finally:
            await writer.drain()
            writer.close()

    async def read_command(self, reader: asyncio.StreamReader)->(str, None):
        """Read data from the stream"""
        result = b""
        try:
            while True:
                try:
                    data = await asyncio.wait_for(reader.read(self.BUFFER_SIZE), timeout=1)
                except (Exception, TimeoutError):
                    data = None
                if data is None:
                    self.logger.debug("Reading complete.")
                    break
                self.logger.debug("Read: {}".format(data))
                result += data
        except Exception:
            self.logger.error("Error occurred while reading from stream:\n{}".format(traceback.format_exc()))
            return None
        if result == "":
            return None
        try:
            return result.decode().replace("+", "")
        except Exception:
            self.logger.error("Error while decoding: {}".format(traceback.format_exc()))
            return None

    async def authenticate_user(self, tag: str, code: str)->bool:
        """
        Return whether the auth code is valid for this user

        The Discord tag and the hashed authentication code are stored in
        the server, this function checks the given credentials against
        the database.
        :param tag: Discord Tag ('@TestUser#1111')
        :param code: Authentication code in str format
        :return: boolean, authenticated
        """
        valid = self.db.get_auth_code(tag)
        if valid is None:  # User not known
            self.logger.info("User {} not known.".format(tag))
            return False
        hashed = hash_auth(code)
        if valid != hashed:  # Invalid authentication code
            self.logger.error("User {} failed to authenticate.".format(tag))
            return False
        self.logger.debug("User {} authenticated successfully.".format(tag))
        return True

    async def check_version(self, version: str)->bool:
        """
        Check the version the client is using, and whether the user is
        using the required minimum version of the server.
        """
        valid = Server.version_from_tag(version) >= Server.version_from_tag(Server.MIN_VERSION)
        if valid is False:
            self.logger.debug("Too old client version detected.")
            return False
        return True

    @staticmethod
    def version_from_tag(version: str)->Version:
        """Convert a str version tag to a Version instance"""
        return Version(version[1:])  # v4.0.2, v5.0.0

    async def split_command(self, command: str)->(tuple, None):
        """
        Split the given command into different elements. The command is
        in the format:
            @TestUser#1111_123456_v4.0.2_command_arg1_arg2...
        """
        elements = command.split("_")
        if len(elements) < 5:
            self.logger.error("Invalid amount of elements received: {}".format(command))
            return None
        (tag, auth, version, command), args = elements[:4], tuple(elements[4:])
        return tag, auth, version, command, args

    async def process_command(self, tag: str, command: str, args: tuple)->(str, None):
        """Abstract function to be implemented for performing tasks"""
        raise NotImplementedError
