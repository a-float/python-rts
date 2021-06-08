from project import tools
from project.states import game, menu


def main():
    """Add states to control here."""
    app = tools.Control("Tha RTS game")
    state_dict = {
        "MENU": menu.Menu(),
        "GAME": game.Game(),
    }
    app.state_machine.setup_states(state_dict, "MENU")
    app.main()
