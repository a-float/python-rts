BUILDING_DATA = {
    'castle': {'health': 200, 'income': 5},
    'tower': {'health': 100, 'cost': 10},
    'barracks': {'health': 60, 'cost': 10},
    'market': {'health': 30, 'cost': 5}
}

BUILDING_SPEED = 1  # how fast building is being build (depends on building hp too)

UPGRADE_COST = 50

UPGRADE_TYPES = {
    'tower': {'sniper': 1, 'magic': 2},
    'barracks': {'swords': 1, 'shields': 2},
    'market': {'mine': 1, 'bank': 2},
}

TOWER_RELOAD_TIME = {
    0: 4,
    1: 4,
    2: 2
}

TOWER_DAMAGE = 50

MARKET_STATS = {
    'income': {0: 1, 1: 2, 2: 13},
    'frequency': {0: 1, 1: 2, 2: 13}
}


SOLDIER_STATS = {
    'health': {0: 50, 1: 50, 2: 100},
    'damage': {0: 20, 1: 40, 2: 20}
}