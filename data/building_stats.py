# frequency is no of times per second
BUILDING_DATA = {
    'castle': {'health': 100, 'income': 2, 'cost': 0},
    'tower': {'health': 60, 'cost': 10, 'damage': 5, 'fire_rate': 8, 'range': 0.035},  # 0.02 is roughly one tile
    'sniper_tower': {'health': 60, 'cost': 10, 'damage': 10, 'fire_rate': 1, 'range': 0.15},
    'magic_tower': {'health': 60, 'cost': 10, 'damage': 30, 'fire_rate': 2, 'range': 0.025},

    'barracks': {'health': 40, 'cost': 10},
    'swords_barracks': {'health': 40, 'cost': 10},
    'shields_barracks': {'health': 40, 'cost': 10},

    'market': {'health': 40, 'cost': 10, 'income': 3, 'frequency': 1},  # average
    'mine': {'health': 40, 'cost': 10, 'income': 50, 'frequency': 0.1},  # slow but big
    'bank': {'health': 40, 'cost': 10, 'income': 2, 'frequency': 0.6},  # fast but tiny
}

BUILDING_SPEED = 1  # how fast buildings are being build (depends on building's hp as well)

UPGRADE_TYPES = {
    'tower': ['sniper_tower', 'magic_tower'],
    'barracks': ['swords_barracks', 'shields_barracks'],
    'market': ['mine', 'bank'],
}

SOLDIER_STATS = {
    'barracks': {'health': 80, 'attack': 20},
    'swords': {'health': 80, 'attack': 40},
    'shields': {'health': 160, 'attack': 20}
}

SOLDIER_ANIM_FPS = 7