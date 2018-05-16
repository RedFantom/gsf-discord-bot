MANUAL = {
    "commands":
        "```markdown\n"
        "For the information on the arguments of each command, please consult\n"
        "the manual for each specific command instead.\n"
        "\n"
        "# Bot information\n"
        "- author\n"
        "- purpose\n"
        "- privacy\n"
        "- help\n"
        "- man\n"
        "- link\n"
        "\n"
        "# User commands\n"
        "- register\n"
        "- unregister\n"
        "- forgot_code\n"
        "\n"
        "# Data Retrieval\n"
        "- servers\n"
        "- day\n"
        "- week\n"
        "- period\n"
        "- matches\n"
        "- results\n"
        "- character\n"
        "\n"
        "# Utilities\n"
        "- random\n"
        "```",
    # Data Retrieval
    "day":
        "```markdown\n"
        "Command: day\n"
        "Arguments:\n"
        "- date, optional, assumes today if not given\n"
        "\n"
        "Display the amount of matches registered for each server on any\n"
        "given day in a table format.\n"
        "```",
    "week":
        "```markdown\n"
        "Command: week\n"
        "Arguments: None\n"
        "\n"
        "Display the amount of matches registered for each server for the\n"
        "last seven days in a table format.\n"
        "```",
    "period":
        "```markdown\n"
        "Command: period\n"
        "Arguments:\n"
        "- start date, mandatory\n"
        "- end date, optional, assumes today if not given\n"
        "\n"
        "Display the amount of matches registered for each server in any \n"
        "given period in a table format.\n"
        "```",
    "servers":
        "```markdown\n"
        "Command: servers\n"
        "Arguments: None\n"
        "\n"
        "Display the servers in the Discord Bot database and their current\n"
        "status.\n"
        "```",
    "matches":
        "```markdown\n"
        "Command: servers\n"
        "Arguments:\n"
        "- server code, mandatory\n"
        "- date, optional, assumes today if not given\n"
        "\n"
        "Display the matches registered on each server in a table format with\n"
        "additional information, including the start and end time, match type\n"
        "and map type if available and end score.\n"
        "```",
    "results":
        "```markdown\n"
        "Command: results\n"
        "Arguments:\n"
        "- server code, mandatory\n"
        "- date, mandatory\n"
        "- start, mandatory\n"
        "\n"
        "Display the registered results of a specific match in a table format,\n"
        "including damage dealt, damage taken and other statistics.\n"
        "```",
    "character":
        "```markdown\n"
        "Command: character"
        "Arguments:\n"
        "- server code, mandatory\n"
        "- player name, mandatory\n"
        "\n"
        "Display the Discord tag of the owner of a certain character on a\n"
        "given server. This is only possible if the owner has chosen to share\n"
        "this information.\n"
        "```",
    # Bot Information
    "author":
        "```markdown\n"
        "Command: author\n"
        "Arguments: None\n"
        "\n"
        "Display the copyright and license information, including information\n"
        "on the usage of data generated by this bot.\n"
        "```",
    "purpose":
        "```markdown\n"
        "Command: purpose\n"
        "Arguments: None\n"
        "\n"
        "Display a text explaining the purpose of this bot.\n"
        "```",
    "privacy":
        "```markdown\n"
        "Command: privacy\n"
        "Arguments: None\n"
        "\n"
        "Display a text explaining what data is collected and how it is\n"
        "stored.\n"
        "```",
    "man":
        "```markdown\n"
        "Command: man\n"
        "Arguments:\n"
        "- command, optional, assumes `commands` if not given.\n"
        "\n"
        "Displays a text explaining how to use the different bot commands.\n"
        "```",
    "link":
        "```markdown\n"
        "Command: link\n"
        "Arguments: None\n"
        "\n"
        "Displays download links for the latest version of the GSF Parser.\n"
        "```",
    "help":
        "```markdown\n"
        "Command: help\n"
        "Arguments: None\n"
        "\n"
        "Displays a basic help text.\n"
        "```",
    # User commands
    "register":
        "```markdown\n"
        "Command: register\n"
        "Arguments: None\n"
        "\n"
        "Register yourself as a user of this bot. A security key is sent to \n"
        "you via PM.\n"
        "```",
    "unregister":
        "```markdown\n"
        "Command: unregister\n"
        "Arguments: None\n"
        "\n"
        "Unregister yourself as a user of this bot. Permanently and\n"
        "irreversibly removes all of your personal data from the database.\n"
        "This command is **irreversible** and takes effect **immediately, all\n"
        "your data is **instantly** removed.\n"
        "```",
    "forgot_code":
        "```markdown\n"
        "Command: forgot_code\n"
        "Arguments: None\n"
        "\n"
        "Request a new security key for accessing the Discord Bot Server. Your\n"
        "old code is invalidated instantly and only the new code can be used.\n"
        "```",
    "scoreboard":
        "```markdown\n"
        "Command: scoreboard\n"
        "Arguments:\n"
        "- type, optional, table assumed if not given\n"
        "  Possible values:\n"
        "  - table, output sent as a table\n"
        "  - excel, output sent as an Excel file\n"
        "  - csv, output sent as a CSV file\n"
        "\n"
        "Performs cropping and OCR on a screenshot of a scoreboard in order to\n"
        "build a table with the results. The screenshot should be sent as an\n"
        "attachment.\n"
        "```",
    # Utilities
    "random":
        "```markdown\n"
        "Command: random\n"
        "Arguments:\n"
        "- type, optional\n"
        "\n"
        "Choose a random ship type out of the possibilities. The result is sent\n"
        "as a Tier-Type combination. You can specify the type by using the type\n"
        "argument:\n"
        "  Fighter\n"
        "  Gunship\n"
        "  Scout\n"
        "  Bomber\n"
        "```"
}
