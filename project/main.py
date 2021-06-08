from project.tools import Control
from project.states import game, menu


def main():
    """Add states to control here."""
    app = Control("Tha RTS game")
    state_dict = {
        "MENU": menu.Menu(),
        "GAME": game.Game(),
    }
    app.state_machine.setup_states(state_dict, "MENU")
    app.main()
