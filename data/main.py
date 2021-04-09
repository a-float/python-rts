from data import tools
from data.states import game


def main():
    """Add states to control here."""
    app = tools.Control("Tha RTS game")
    state_dict = {
        "GAME": game.Game(),
    }
    app.state_machine.setup_states(state_dict, "SPLASH")
    app.main()