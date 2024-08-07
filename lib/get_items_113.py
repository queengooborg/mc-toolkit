# -*- coding: utf-8 -*-

# 
# mc-toolkit - lib/get_items_113
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Get items list from Minecraft source code for 1.13 through 1.19.2, sorted by creative mode tabs
#

import os, re, json
from pathlib import Path

from .creative_only_items import creative_only_items
from .get_recipes import get_recipes
from .item_substitutions import item_substitutions

# Get items list
def get_items(source_path, mc_version, include_creative=False, all_recipes=False):
	items = {}
	recipes = get_recipes(source_path, mc_version, simplest_only=not all_recipes)

	categories = {
		'BUILDING_BLOCKS': {
			'block': 'BRICKS',
			'items': []
		},
		'DECORATIONS': {
			'block': 'PEONY',
			'items': []
		},
		'REDSTONE': {
			'block': 'REDSTONE',
			'items': []
		},
		'TRANSPORTATION': {
			'block': 'POWERED_RAIL',
			'items': []
		},
		'MISC': {
			'block': 'LAVA_BUCKET',
			'items': []
		},
		'FOOD': {
			'block': 'APPLE',
			'items': []
		},
		'TOOLS': {
			'block': 'IRON_AXE',
			'items': []
		},
		'COMBAT': {
			'block': 'GOLDEN_SWORD',
			'items': []
		},
		'BREWING': {
			'block': 'POTION',
			'items': []
		},
		'MISC': {
			'block': 'DRAGON_EGG',
			'items': []
		},
	}

	itemgroupname = 'CreativeModeTab'
	itemgroupjava = Path(f"{source_path}/world/item/{itemgroupname}.java")
	itemsjava = Path(f"{source_path}/world/item/Items.java")

	with open(str(itemgroupjava), 'r') as igj:
		for line in igj.readlines():
			match = re.search(rf"public static final {itemgroupname} (\w+) = \(?new {itemgroupname}\((\d+), \"(\w+)\"\) {{", line)
			if match:
				items[match.group(1).replace('TAB_', '')]['items'] = []

	with open(str(itemsjava), 'r') as ij:
		for line in ij.readlines():
			match = re.search(rf"public static final Item (\w+) = .+{itemgroupname}\.(\w+).+", line)
			item = None
			group = 'MISC'
			if match:
				item = match.group(1)

				group = match.group(2).replace('TAB_', '')
				if group not in items:
					group = 'MISC'
			else:
				match2 = re.search(r"public static final Item (\w+) = .+", line)
				if match2:
					item = match2.group(1)

			if item:
				item = item_substitutions.get(item, item) # Fix any typos present in source code

				if not include_creative and item in creative_only_items:
					continue

				items[item] = recipes.get(item)
				categories[group]['items'].append(item)

	return dict(items=items, categories=categories)
