from dataclasses import dataclass
from typing import Optional

from data.networking.client import Client
from data.networking.server import Server


@dataclass
class MapConfig:
    """ Stores data needed for the initialization of the map. Part of the GameData class"""
    player_no: int
    name: str
    layout: str


@dataclass
class GameData:
    """ Stores data that needs to be passed via persist to configure the game """
    server: Optional[Server]
    client: Optional[Client]
    map: MapConfig
