# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro - lib/get_items
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Get items list from the Minecraft source code, sorted by creative mode tabs
#

import os, re, json
from pathlib import Path

cache_dir = Path(os.path.dirname(__file__)) / "../output/itemcache"

# Get list for 1.20+
def get_items_120(source_path, mc_version):
	items = {}

	creativemodetabjava = Path(f"{source_path}/world/item/CreativeModeTabs.java")

	with open(str(creativemodetabjava)) as cmtj:
		current_group = None

		# Reading source code line by line to avoid regex backtracking issues
		for line in cmtj.readlines():
			groupmatch = re.search(r"Registry\.register\(registry, ([\w_]+), CreativeModeTab\.builder\(CreativeModeTab\.Row\.(?:TOP|BOTTOM), \d+\)\.title\(Component.translatable\(\"itemGroup\.\w+\"\)\)\.icon\(\(\) -> new ItemStack\((?:Items|Blocks)\.(\w+)\)\)\.displayItems\(\(itemDisplayParameters, output\) -> {", line)
			if groupmatch and groupmatch.group(1) not in ['SPAWN_EGGS', 'OP_BLOCKS']:
				current_group = groupmatch

			itemmatch = re.search(r"output\.accept\(Items\.([\w_]+)\);", line)
			if itemmatch:
				if current_group.group(1) in items:
					items[current_group.group(1)]['items'][itemmatch.group(1).lower()] = {}
				else:
					items[current_group.group(1)] = {
						'block': current_group.group(2),
						'items': {
							itemmatch.group(1).lower(): {}
						}
					}

	return items

# Get list for 1.13 through 1.19
def get_items_113(source_path, mc_version):
	items = {
		'BUILDING_BLOCKS': {
			'block': 'BRICKS',
			'items': {}
		},
		'DECORATIONS': {
			'block': 'PEONY',
			'items': {}
		},
		'REDSTONE': {
			'block': 'REDSTONE',
			'items': {}
		},
		'TRANSPORTATION': {
			'block': 'POWERED_RAIL',
			'items': {}
		},
		'MISC': {
			'block': 'LAVA_BUCKET',
			'items': {}
		},
		'FOOD': {
			'block': 'APPLE',
			'items': {}
		},
		'TOOLS': {
			'block': 'IRON_AXE',
			'items': {}
		},
		'COMBAT': {
			'block': 'GOLDEN_SWORD',
			'items': {}
		},
		'BREWING': {
			'block': 'POTION',
			'items': {}
		},
		'MISC': {
			'block': 'DRAGON_EGG',
			'items': {}
		},
	}

	if mc_version >= '1.17':
		# 1.17-1.19
		itemgroupname = 'CreativeModeTab'
		itemgroupjava = Path(f"{source_path}/world/item/{itemgroupname}.java")
		itemsjava = Path(f"{source_path}/world/item/Items.java")
	else:
		# 1.13-1.16
		itemgroupname = 'ItemGroup'
		itemgroupjava = Path(f"{source_path}/item/{itemgroupname}.java")
		itemsjava = Path(f"{source_path}/item/Items.java")

	with open(str(itemgroupjava), 'r') as igj:
		for line in igj.readlines():
			match = re.search(rf"public static final {itemgroupname} (\w+) = \(?new {itemgroupname}\((\d+), \"(\w+)\"\) {{", line)
			if match:
				items[match.group(1).replace('TAB_', '')]['items'] = []

	with open(str(itemsjava), 'r') as ij:
		for line in ij.readlines():
			match = re.search(rf"public static final Item (\w+) = .+{itemgroupname}\.(\w+).+", line)
			if match:
				group = match.group(2).replace('TAB_', '')
				if group in items:
					items[group]['items'][match.group(1).lower()] = {}
				elif group == 'MATERIALS':
					items['MISC']['items'][match.group(1).lower()] = {}
			else:
				match2 = re.search(r"public static final Item (\w+) = .+", line)
				if match2:
					items['MISC']['items'][match2.group(1).lower()] = {}

	return items

def main(source_path, mc_version):
	cache_path = cache_dir / f"{mc_version}.json"

	if cache_path.exists():
		return json.load(open(cache_path, 'r'))

	data = {}
	if mc_version >= '1.20':
		data = get_items_120(source_path, mc_version)
	else:
		data = get_items_113(source_path, mc_version)

	# Cache data
	os.makedirs(cache_dir, exist_ok=True)
	with open(cache_path, 'w') as cachefile:
		json.dump(data, cachefile)

	return data
