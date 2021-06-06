# frequency is no of times per second
BUILDING_DATA = {
    'castle': {'health': 1, 'income': 2, 'cost': 0},
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


# def get_stats_dict():
#     return {
#         'BUILDING_DATA': BUILDING_DATA,
#         'BUIlDING_SPEED': BUILDING_SPEED,
#         'UPGRADE_COST': UPGRADE_COST,
#         'UPGRADE_TYPES': UPGRADE_TYPES,
#         'TOWER_RELOAD_TIME': TOWER_RELOAD_TIME,
#         'TOWER_DAMAGE': TOWER_DAMAGE,
#         'SOLDIER_STATS': SOLDIER_STATS
#     }
#
#
# def read_stats_dict(stats):
#     print('reading the stats')
#     global BUILDING_DATA, BUILDING_SPEED, UPGRADE_TYPES, UPGRADE_COST, TOWER_RELOAD_TIME, TOWER_DAMAGE, SOLDIER_STATS
#     BUILDING_DATA = stats['BUILDING_DATA']
#     BUILDING_SPEED = stats['BUIlDING_SPEED']
#     UPGRADE_COST = stats['UPGRADE_COST']
#     UPGRADE_TYPES = stats['UPGRADE_TYPES']
#     TOWER_RELOAD_TIME = stats['TOWER_RELOAD_TIME']
#     TOWER_DAMAGE = stats['TOWER_DAMAGE']
#     SOLDIER_STATS = stats['SOLDIER_STATS']
