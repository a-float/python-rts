BUILDING_DATA = {
    'castle': {'health': 120, 'income': 5},
    'tower': {'health': 60, 'cost': 10},
    'barracks': {'health': 40, 'cost': 10},
    'market': {'health': 40, 'cost': 10}
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

TOWER_DAMAGE = 25

MARKET_STATS = {
    'income': {0: 1, 1: 2, 2: 13},
    'frequency': {0: 1, 1: 2, 2: 13}
}

SOLDIER_STATS = {
    'health': {0: 50, 1: 50, 2: 100},
    'damage': {0: 20, 1: 40, 2: 20}
}


def get_stats_dict():
    return {
        'BUILDING_DATA': BUILDING_DATA,
        'BUIlDING_SPEED': BUILDING_SPEED,
        'UPGRADE_COST': UPGRADE_COST,
        'UPGRADE_TYPES': UPGRADE_TYPES,
        'TOWER_RELOAD_TIME': TOWER_RELOAD_TIME,
        'TOWER_DAMAGE': TOWER_DAMAGE,
        'SOLDIER_STATS': SOLDIER_STATS
    }


def read_stats_dict(stats):
    print('reading the stats')
    global BUILDING_DATA, BUILDING_SPEED, UPGRADE_TYPES, UPGRADE_COST, TOWER_RELOAD_TIME, TOWER_DAMAGE, SOLDIER_STATS
    BUILDING_DATA = stats['BUILDING_DATA']
    BUILDING_SPEED = stats['BUIlDING_SPEED']
    UPGRADE_COST = stats['UPGRADE_COST']
    UPGRADE_TYPES = stats['UPGRADE_TYPES']
    TOWER_RELOAD_TIME = stats['TOWER_RELOAD_TIME']
    TOWER_DAMAGE = stats['TOWER_DAMAGE']
    SOLDIER_STATS = stats['SOLDIER_STATS']
