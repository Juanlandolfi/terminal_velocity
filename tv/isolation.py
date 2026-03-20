class IsolatedBotLogic:
    """
    A 'bot' that in reality spawns a docker container with the actual bot running inside it.
    """
    def __init__(self, name, bot_type, turn_timeout):
        self.name = name
        self.bot_type = bot_type
        self.turn_timeout = turn_timeout

    def initialize_bot(self):
        """
        Initialize the bot running inside the container.
        """
        # TODO
        ...

    def turn(self, hp, cargo, position, power_distribution, radar_contacts):
        """
        Ask the bot in the container for an action and return it.
        """
        # TODO
        ...

    def stop_bot(self):
        """
        Stop the bot container.
        """
        # TODO
        ...

