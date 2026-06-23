# -*- coding: utf-8 -*-

# 
# mc-toolkit - lib/get_items
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Get items list from the Minecraft source code, sorted by creative mode tabs
#

import os, re, json
from pathlib import Path

from .creative_only_items import creative_only_items
from .get_recipes import get_recipes
from .item_substitutions import item_substitutions
from .version import Version

cache_dir = Path(os.path.dirname(__file__)) / "../output/itemcache"

# Get items list (MC 1.19.3 and above)
def get_items(source_path, mc_version, include_creative=False, all_recipes=False):
	items = {}
	categories = {}
	recipes = get_recipes(source_path, mc_version, simplest_only=not all_recipes)

	itemsjava = Path(f"{source_path}/world/item/Items.java")
	with open(str(itemsjava), 'r') as ij:
		for line in ij.readlines():
			match = re.search(rf"public static final (Item|WeatheringCopperItems) (\w+) = ", line)
			if match:
				item = match.group(2)
				item = item_substitutions.get(item, item) # Fix any typos present in source code

				if not include_creative and item in creative_only_items:
					continue

				items[item] = recipes.get(item)

				if match.group(1) == "WeatheringCopperItems":
					for mod in ["EXPOSED_", "WEATHERED_", "OXIDIZED_", "WAXED_", "WAXED_EXPOSED_", "WAXED_WEATHERED_", "WAXED_OXIDIZED_"]:
						items[mod + item] = recipes.get(mod + item)

				if item == "WRITABLE_BOOK":
					items["WRITTEN_BOOK"] = None
				elif item == "MAP":
					items["FILLED_MAP"] = None

	with open(Path(f"{source_path}/world/item/CreativeModeTabs.java")) as cmtj:
		current_group = None

		# Reading source code line by line to avoid regex backtracking issues
		for line in cmtj.readlines():
			groupmatch = re.search(r"(?:Registry\.register\(registry, ([\w_]+), )?CreativeModeTab\.builder\(CreativeModeTab\.Row\.(?:TOP|BOTTOM), \d+\)\.title\(Component.translatable\(\"itemGroup\.\w+\"\)\)\.icon\(\(\) -> new ItemStack\((?:Items|Blocks)\.(\w+)\)\)(?:\.alignedRight\(\))?\.displayItems\(\((parameters|itemDisplayParameters|featureFlagSet)(?:, output)?(?:, (?:bl|buildingBlocks))?\) -> {", line)
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
				item = item_substitutions.get(item, item) # Fix any typos present in source code
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

# Get items list (MC 1.13 through 1.19.2)
def get_items_legacy(source_path, mc_version, include_creative=False, all_recipes=False):
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

def main(source_path, mc_version, no_cache=False, include_creative=False, all_recipes=False):
	cache_path = cache_dir / (mc_version + ("_creative" if include_creative else "") + ("_all-recipes" if all_recipes else "") + ".json")

	if cache_path.exists() and not no_cache:
		return json.load(open(cache_path, 'r'))

	data = {}
	if mc_version >= Version('1.19.3'):
		data = get_items(source_path, mc_version, include_creative)
	else:
		data = get_items_legacy(source_path, mc_version, include_creative)

	# Cache data
	os.makedirs(cache_dir, exist_ok=True)
	with open(cache_path, 'w') as cachefile:
		json.dump(data, cachefile)

	return data
