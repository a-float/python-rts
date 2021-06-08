from typing import Any

import pygame as pg
from project import state_machine
from project.states.menu_states import MainMenu, GameSetup, OnlineModeSelect, OnlineLobby


class Menu(state_machine.State):
    def __init__(self):
        super().__init__()
        self.next = "GAME"
        self.state_machine: Any[state_machine.StateMachine] = None

    def startup(self, now, persistent):
        self.state_machine = state_machine.StateMachine()
        state_dict = {
            "MAIN": MainMenu(),
            "GAME_SETUP": GameSetup(),
            'ONLINE_MODE_SELECT': OnlineModeSelect(),
            'ONLINE_LOBBY': OnlineLobby()
        }
        self.state_machine.setup_states(state_dict, "MAIN")
        super().startup(now, {})

    def cleanup(self):
        self.state_machine.state.cleanup()
        return super().cleanup()

    def get_event(self, event):
        if event.type == pg.KEYDOWN:
            self.start_time = pg.time.get_ticks()
        self.state_machine.get_event(event)

    def update(self, keys, now):
        self.state_machine.update(keys, now)
        if self.state_machine.done:
            self.done = True
            # taking the persist out of this state machine so it can be passed to the GAME state
            self.persist = self.state_machine.state.persist
            # print('new MENU persist ', self.persist)

    def draw(self, surface, interpolate):
        self.state_machine.draw(surface, interpolate)
