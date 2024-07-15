# -*- coding: utf-8 -*-

# 
# mc-toolkit - lib/get_items_120
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Get items list from Minecraft source code for 1.20, sorted by creative mode tabs
#

import os, re, json
from pathlib import Path

from .creative_only_items import creative_only_items
from .get_recipes import get_recipes

# Get items list
def get_items(source_path, mc_version, include_creative=False, all_recipes=False):
	items = {}
	categories = {}
	recipes = get_recipes(source_path, mc_version, simplest_only=not all_recipes)

	itemsjava = Path(f"{source_path}/world/item/Items.java")
	with open(str(itemsjava), 'r') as ij:
		for line in ij.readlines():
			match = re.search(rf"public static final Item (\w+) = ", line)
			if match:
				item = match.group(1)
				if not include_creative and item in creative_only_items:
					continue

				if item == "CUT_STANDSTONE_SLAB":
					item = "CUT_SANDSTONE_SLAB" # Fix typo present in source code
				recipe = recipes.get(item)

				items[item] = recipe

				if item == "WRITABLE_BOOK":
					items["WRITTEN_BOOK"] = None
				elif item == "MAP":
					items["FILLED_MAP"] = None

	with open(Path(f"{source_path}/world/item/CreativeModeTabs.java")) as cmtj:
		current_group = None

		# Reading source code line by line to avoid regex backtracking issues
		for line in cmtj.readlines():
			groupmatch = re.search(r"Registry\.register\(registry, ([\w_]+), CreativeModeTab\.builder\(CreativeModeTab\.Row\.(?:TOP|BOTTOM), \d+\)\.title\(Component.translatable\(\"itemGroup\.\w+\"\)\)\.icon\(\(\) -> new ItemStack\((?:Items|Blocks)\.(\w+)\)\)(?:\.alignedRight\(\))?\.displayItems\(\(itemDisplayParameters, output\) -> {", line)
			if groupmatch:
				current_group = groupmatch

			if not include_creative and current_group and current_group.group(1) in ['SPAWN_EGGS', 'OP_BLOCKS']:
				# Skip creative-only items
				continue

			item = None
			itemmatch = re.search(r"output\.accept\(Items\.([\w_]+)\);", line)
			if itemmatch:
				item = itemmatch.group(1)
			elif 'CreativeModeTabs.generateFireworksAllDurations(' in line:
				item = 'FIREWORK_ROCKET'
			elif 'CreativeModeTabs.generateSuspiciousStews(' in line:
				item = "SUSPICIOUS_STEW"
			elif 'CreativeModeTabs.generateInstrumentTypes(output, registryLookup, Items.GOAT_HORN' in line:
				item = "GOAT_HORN"
			elif 'CreativeModeTabs.generateEnchantmentBookTypesOnlyMaxLevel(' in line:
				item = 'ENCHANTED_BOOK'
			else:
				potionmatch = re.search(r"CreativeModeTabs\.generatePotionEffectTypes\(output, registryLookup, Items\.([\w_]+)", line)
				if potionmatch:
					item = potionmatch.group(1)

			if item:
				if item == "CUT_STANDSTONE_SLAB":
					item = "CUT_SANDSTONE_SLAB" # Fix typo present in source code
				recipe = recipes.get(item)

				if not include_creative and item in creative_only_items:
					continue

				group = current_group.group(1)
				if group not in categories:
					categories[group] = {
						'block': current_group.group(2),
						'items': []
					}

				categories[group]['items'].append(item)

	return dict(items=items, categories=categories)
