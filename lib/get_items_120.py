# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro - lib/get_items_120
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Get items list from Minecraft source code for 1.20, sorted by creative mode tabs
#

import os, re, json
from pathlib import Path

# Get items list
def get_items(source_path, mc_version):
	items = {}

	with open(Path(f"{source_path}/world/item/CreativeModeTabs.java")) as cmtj:
		current_group = None

		# Reading source code line by line to avoid regex backtracking issues
		for line in cmtj.readlines():
			groupmatch = re.search(r"Registry\.register\(registry, ([\w_]+), CreativeModeTab\.builder\(CreativeModeTab\.Row\.(?:TOP|BOTTOM), \d+\)\.title\(Component.translatable\(\"itemGroup\.\w+\"\)\)\.icon\(\(\) -> new ItemStack\((?:Items|Blocks)\.(\w+)\)\)\.displayItems\(\(itemDisplayParameters, output\) -> {", line)
			if groupmatch and groupmatch.group(1) not in ['SPAWN_EGGS', 'OP_BLOCKS']:
				current_group = groupmatch

			itemmatch = re.search(r"output\.accept\(Items\.([\w_]+)\);", line)
			if itemmatch:
				item = itemmatch.group(1)
				recipe = recipes.get(item)

				# Add item to list
				if current_group.group(1) in items:
					items[current_group.group(1)]['items'][item] = {}
				else:
					items[current_group.group(1)] = {
						'block': current_group.group(2),
						'items': {
							item: {}
						}
					}

	return items
