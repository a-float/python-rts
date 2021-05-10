from data import config, tools
from data.states import offline_game, main_menu


def main():
    """Add states to control here."""
    app = tools.Control("Tha RTS game")
    state_dict = {
        "MENU": main_menu.Menu(),
        "GAME": offline_game.OfflineGame(),
    }
    app.state_machine.setup_states(state_dict, "MENU")
    app.main()