"""
The main function is defined here. It simply creates an instance of
tools.Control and adds the game states to its state_machine dictionary.
There should be no need (theoretically) to edit the tools.Control class.
All modifications should occur in this module
and in the config module.
"""

import sys
import pygame as pg

from project.main import main

if __name__ == '__main__':
    main()
    pg.quit()
    sys.exit()