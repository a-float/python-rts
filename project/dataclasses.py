from dataclasses import dataclass
from typing import Optional
from project.networking import Client, Server


@dataclass
class MapConfig:
    """ Stores project needed for the initialization of the map. Part of the GameData class"""
    player_no: int
    name: str
    layout: str


@dataclass
class GameData:
    """ Stores project that needs to be passed via persist to configure the game """
    server: Optional[Server]
    client: Optional[Client]
    map: MapConfig
