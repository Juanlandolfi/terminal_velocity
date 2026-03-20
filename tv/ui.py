from contextlib import contextmanager
from time import sleep
import curses

from blessings import Terminal

from tv.game import (
    SPACESHIP,
    ASTEROID,
    HOME_BASE,
    ENGINES,
    SHIELDS,
    LASERS,
    Position,
    Player,
)


class TerminalVelocityUI:
    """
    Cli UI for Terminal Velocity.
    """
    def __init__(self, turn_delay):
        self.term = Terminal()
        self.turn_delay = turn_delay
        self.last_args = None
        self.game = None
        self.player_colors = {}

    def initialize(self, game):
        """
        Initialize the UI with the game instance, so it can access the game state when rendering.
        Also assign colors to players.
        """
        self.game = game

        free_colors = [
            self.term.blue, self.term.red, self.term.green, self.term.yellow, self.term.cyan,
            self.term.white, self.term.magenta,
        ]
        for player in self.game.players.values():
            self.player_colors[player.name] = free_colors.pop(0)

    def render(self, turn_number, winners=None, running_in_fullscreen=True):
        """
        Render the game state.
        """
        self.last_args = (turn_number, winners)

        if winners:
            winner_names = {winner.name for winner in winners}
        else:
            winner_names = set()

        if running_in_fullscreen:
            print(self.term.move(0, 0))

        self.render_world(winner_names, blink_winners=False)
        self.render_players_status(turn_number, winner_names, blink_winners=False)

        if winner_names and running_in_fullscreen:
            blink = True
            while True:
                sleep(0.3)
                print(self.term.move(0, 0))
                self.render_world(winner_names, blink_winners=blink)
                self.render_players_status(turn_number, winner_names, blink_winners=blink)
                blink = not blink

        sleep(self.turn_delay)

    def render_world(self, winner_names, blink_winners=False):
        """
        Render the world of the game.
        """
        # populate the world cache
        world = {}
        for home_base_position in self.game.home_base_positions_cache:
            world[home_base_position] = HOME_BASE
        for asteroid in self.game.asteroids:
            world[asteroid] = ASTEROID
        for player in self.game.players.values():
            world[player.position] = player

        # renderize the world
        for y in range(-self.game.map_radius, self.game.map_radius + 1):
            row = ""
            for x in range(-self.game.map_radius, self.game.map_radius + 1):
                icon = "  "
                color = self.term.black

                thing = world.get(Position(x, y))

                if isinstance(thing, Player):
                    icon = "<>"
                    color = self.player_colors[thing.name]
                    if thing.name in winner_names and blink_winners:
                        color = self.term.black
                elif thing == ASTEROID:
                    icon = "{}"
                    color = self.term.white
                elif thing == HOME_BASE:
                    icon = "[]"
                    color = self.term.white

                row += f"{color}{icon}{self.term.normal}"
            print(row)

    def render_players_status(self, turn_number, winner_names, blink_winners=False, running_in_fullscreen=True):
        """
        Render the status of the players.
        """
        print("Turn", turn_number, self.term.clear_eol)

        for player in self.game.players.values():
            player_line = (
                f"E{player.power_distribution[ENGINES] * '>':<4} "
                f"S{player.power_distribution[SHIELDS] * '>':<4} "
                f"L{player.power_distribution[LASERS] * '>':<4} "
                f"C{player.cargo * '{}':<8} "
                f"{player.hp}+ "
                f"{player.score}$"
                f"{self.term.clear_eol}"
            )

            color = self.player_colors[player.name]
            if player.name in winner_names:
                winner_message = " WINNER!! Press ctrl-c to quit"
                if blink_winners:
                    color = self.term.black
            else:
                winner_message = ""

            print(f"{color}{player_line} {player}{self.term.normal}{winner_message}{self.term.clear_eol}")

    @contextmanager
    def show(self):
        """
        Context manager to wrap the showing of the game ui during its execution.
        """
        try:
            with self.term.fullscreen(), self.term.hidden_cursor():
                print(self.term.clear)
                yield self
        finally:
            print(self.term.normal)
            if self.last_args is not None:
                self.render(*self.last_args, running_in_fullscreen=False)

