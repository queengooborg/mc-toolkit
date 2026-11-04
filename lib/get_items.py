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
from .get_dye_colors import get_dye_colors
from .item_substitutions import item_substitutions
from .version import Version

cache_dir = Path(os.path.dirname(__file__)) / "../output/itemcache"

# Get items list (MC 1.19.3 and above)
def get_items(source_path, mc_version, include_creative=False, all_recipes=False):
	items = {}
	categories = {}
	recipes = get_recipes(source_path, mc_version, simplest_only=not all_recipes)

	dye_colors = get_dye_colors(source_path)

	weathering_copper_modifiers = ["", "EXPOSED_", "WEATHERED_", "OXIDIZED_", "WAXED_", "WAXED_EXPOSED_", "WAXED_WEATHERED_", "WAXED_OXIDIZED_"]
	weathering_copper_items = set()
	color_collection_items = set()
	itemsjava = Path(f"{source_path}/world/item/Items.java")
	with open(str(itemsjava), 'r') as ij:
		for line in ij:
			match = re.search(rf"public static final (Item|WeatheringCopperItems|WeatheringCopperCollection<Item>|ColorCollection<Item>) (\w+) = ", line)
			if match:
				item = match.group(2)
				item = item_substitutions.get(item, item) # Fix any typos present in source code

				if not include_creative and item in creative_only_items:
					continue

				if match.group(1) == "ColorCollection<Item>":
					color_collection_items.add(item)
					for c in dye_colors:
						items[c + "_" + item] = recipes.get(c + "_" + item)
					continue

				items[item] = recipes.get(item)

				if match.group(1) in ["WeatheringCopperItems", "WeatheringCopperCollection<Item>"]:
					weathering_copper_items.add(item)
					for mod in weathering_copper_modifiers[1:]:
						items[mod + item] = recipes.get(mod + item)

				if item == "WRITABLE_BOOK":
					items["WRITTEN_BOOK"] = None
				elif item == "MAP":
					items["FILLED_MAP"] = None

	with open(Path(f"{source_path}/world/item/CreativeModeTabs.java")) as cmtj:
		current_group = None

		# Reading source code line by line to avoid regex backtracking issues
		for line in cmtj:
			groupmatch = re.search(r"(?:Registry\.register\(registry, (?P<registry_name>[\w_]+), |private static final CreativeModeTab (?P<field_name>[\w_]+) = )?CreativeModeTab\.builder\(CreativeModeTab.Row\.(?:TOP|BOTTOM), \d+\)\.title\(Component.translatable\(\"itemGroup\.\w+\"\)\)\.icon\(\(\) -> new ItemStack\((?:Items|Blocks)\.(?P<icon>\w+)(?:\.(?P<icon_variant>\w+)\(\))?\)\)(?:\.alignedRight\(\))?\.displayItems\(\((?P<parameters>parameters|itemDisplayParameters|featureFlagSet)(?:, (?P<output>\w+))?(?:, \w+)?\) -> {", line)
			if groupmatch:
				current_group = groupmatch

			if not include_creative and current_group and (current_group.group('registry_name') or current_group.group('field_name')) in ['SPAWN_EGGS', 'OP_BLOCKS']:
				# Skip creative-only items
				continue

			item = None
			output = current_group.group('output') if current_group else 'output'
			itemmatch = re.search(rf"{re.escape(output)}\.accept\(Items\.([\w_]+)\);", line)
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

				category_items = [item]
			else:
				color_collection_match = re.search(r"CreativeModeTabs\.registerColoredItems\(\w+, \w+, Items\.([\w_]+)\);", line)
				if color_collection_match and color_collection_match.group(1) in color_collection_items:
					category_items = [
						f'{color}_{color_collection_match.group(1)}'
						for color in dye_colors
					]
				else:
					collectionmatch = re.search(r"Items\.([\w_]+)\.forEach\(\w+::accept\);", line)
					if collectionmatch and collectionmatch.group(1) in weathering_copper_items:
						category_items = [mod + collectionmatch.group(1) for mod in weathering_copper_modifiers]
					else:
						category_items = []

			if category_items:
				group = current_group.group('registry_name') or current_group.group('field_name')
				if group not in categories:
					icon = current_group.group('icon')
					if current_group.group('icon_variant'):
						icon = f"{current_group.group('icon_variant')}_{icon}".upper()
					categories[group] = {
						'block': icon,
						'items': []
					}

				categories[group]['items'].extend(category_items)

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
		for line in igj:
			match = re.search(rf"public static final {itemgroupname} (\w+) = \(?new {itemgroupname}\((\d+), \"(\w+)\"\) {{", line)
			if match:
				categories[match.group(1).replace('TAB_', '')]['items'] = []

	with open(str(itemsjava), 'r') as ij:
		for line in ij:
			match = re.search(rf"public static final Item (\w+) = .+{itemgroupname}\.(\w+).+", line)
			item = None
			group = 'MISC'
			if match:
				item = match.group(1)

				group = match.group(2).replace('TAB_', '')
				if group not in categories:
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
		with open(cache_path, 'r') as cachefile:
			return json.load(cachefile)

	data = {}
	if mc_version >= Version('1.19.3'):
		data = get_items(source_path, mc_version, include_creative, all_recipes)
	else:
		data = get_items_legacy(source_path, mc_version, include_creative, all_recipes)

	# Cache data
	os.makedirs(cache_dir, exist_ok=True)
	with open(cache_path, 'w') as cachefile:
		json.dump(data, cachefile)

	return data
