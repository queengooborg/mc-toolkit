# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro - generate_worth.py
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Generate a worth.yml using some base values and recipes determined from Minecraft source
#

import argparse, os
from pathlib import Path

from DecompilerMC.main import get_latest_version
from lib import prepare_source, get_items, creative_only_items

import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

script_dir = Path(os.path.dirname(__file__))
output_dir = script_dir / "output"

base_worth = yaml.load(open(script_dir / "base_worth.yml", 'r'), Loader=Loader)
worth_header = open(script_dir / "worth_yml_header.yml", "r").read()

def remap_ingredient(item_id):
	remappings = {
		'PLANKS': 'OAK_PLANKS',
		'LOGS': 'OAK_LOG',
		'LOGS_THAT_BURN': 'OAK_LOG',
		'WOODEN_SLABS': 'OAK_SLAB',
		'COAL/CHARCOAL': 'COAL',
		'COALS': 'COAL',
		'WOOL': 'WHITE_WOOL',
		'SOUL_FIRE_BASE_BLOCKS': 'SOUL_SOIL',
		'STONE_CRAFTING_MATERIALS': 'COBBLESTONE',
		'STONE_TOOL_MATERIALS': 'COBBLESTONE',
		'SAND/RED_SAND': 'SAND',
	}

	if item_id in remappings:
		return remappings[item_id]
	elif item_id.endswith('_LOGS'):
		item_id = item_id.replace('_LOGS', '_LOG')
	elif item_id.endswith('_STEMS'):
		item_id = item_id.replace('_STEMS', '_STEM')
	elif item_id.endswith('_BLOCKS'):
		item_id = item_id.replace('_BLOCKS', '_BLOCK')

	return item_id

def add_to_worth(worth, item_id, value):
	worth[item_id] = round(value, 2)

# Calculate worth for a specific recipe
def calculate_worth_from_recipe(items, worth, item_id):
	recipe = items.get(item_id)
	if not recipe:
		if item_id not in items:
			raise Exception(f'Item {item_id} not found!')
		raise Exception(f'Item {item_id} has no recipe!')

	if type(recipe) == list:
		recipe = recipe[0]

	value = 0.0
	ing_count = 0

	for i, ic in recipe['ingredients'].items():
		ingredient = remap_ingredient(i)
		if ingredient not in worth:
			raise Exception(f"Ingredient {ingredient} is not defined in worth data!")
		value += worth[ingredient] * ic
		ing_count += ic

	result = value * (1.0 - ((ing_count - 1) / 100)) / recipe['count']

	if recipe['pattern'] in ['axe', 'shovel', 'hoe']:
		result = result * 0.9
	elif recipe['pattern'] in ['furnace', 'stonecutter']:
		result = result * 1.25

	return result

def calculate_worth(worth, items):
	for item, recipe in items.items():

		if item in worth:
			continue # Skip already calculated values

		# Ores
		if item.endswith('_ORE'):
			material = item.replace("NETHER_", "").replace("DEEPSLATE_", "").split('_')[0]
			if material in ['IRON', 'COPPER', 'GOLD']:
				material = f'RAW_{material}'
			elif material == 'LAPIS':
				material = 'LAPIS_LAZULI'
			add_to_worth(worth, item, worth[material] * 0.75)
			continue

		# Oxidized copper blocks (EXPOSED_COPPER, WEATHERED_COPPER, OXIDIZED_COPPER)
		elif item in ["EXPOSED_COPPER", "WEATHERED_COPPER", "OXIDIZED_COPPER"]:
			if not 'CUT_COPPER' in worth:
				continue # Need to wait for calculation
			add_to_worth(worth, item, worth['CUT_COPPER'] *
				(0.5 if item == 'EXPOSED_COPPER' else 0.4 if item == 'WEATHERED_COPPER' else 0.3)
			)
			continue

		# Damaged anvils (CHIPPED_ANVIL, DAMAGED_ANVIL)
		elif item.endswith("_ANVIL"):
			if not 'ANVIL' in worth:
				continue # Need to wait for calculation
			add_to_worth(worth, item, worth['ANVIL'] * (0.5 if item == 'CHIPPED_ANVIL' else 0.25))
			continue

		if not recipe:
			continue # No recipe, cannot calculate

		if type(recipe) == list:
			recipe = recipe[0]

		can_calc = True
		for ing in recipe['ingredients'].keys():
			if remap_ingredient(ing) not in worth:
				can_calc = False
				break

		if not can_calc:
			continue

		add_to_worth(worth, item, calculate_worth_from_recipe(items, worth, item))

		# Handle legacy names
		if item.startswith('END_STONE_BRICK') and item != "END_STONE_BRICKS":
			worth[item.replace('_BRICK', '')] = worth[item]
		elif item == "MELON":
			worth["MELON_BLOCK"] = worth['MELON']
		elif item == "SKULL_BANNER_PATTERN":
			worth["SKELETON_BANNER_PATTERN"] = worth["SKULL_BANNER_PATTERN"]

def remap_names_for_essentials(worth):
	new_worth = {}
	for item, value in worth.items():
		new_worth[item.replace('_', '').lower()] = value
	return new_worth

def generate_worth(mc_version, no_cache=False, outpath=output_dir / "worth.yml", essentials=True):
	if not mc_version:
		mc_version = get_latest_version()[1]

	source_path = prepare_source(mc_version)
	items = get_items(source_path, mc_version, no_cache)['items']
	worth = base_worth

	calculated_items = len(worth.keys())
	while True:
		calculate_worth(worth, items)
		if len(worth.keys()) == calculated_items:
			break # We aren't able to calculate any more recipes
		calculated_items = len(worth.keys())

	for i in items:
		if i not in worth:
			print(f'{i} was not calculated!', f'Its recipe was {items[i]}' if items[i] else 'It has no recipe!')
		elif worth[i] == 0.0:
			print(f'{i} resulted in a value of 0.00, calculation error!')


	os.makedirs(output_dir, exist_ok=True)

	if essentials:
		worth = remap_names_for_essentials(worth)

	with open(outpath, 'w') as worthfile:
		worthfile.write(worth_header + "\n\n")
		worthfile.write(yaml.dump({'worth': worth}, Dumper=Dumper))

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog="generate_worth", description="Generate an EssentialsX worth.yml file based on Minecraft recipes and a few base prices")
	parser.add_argument('mc_version', nargs='?')
	parser.add_argument('-n', '--no_cache', action='store_true')
	parser.add_argument('-v', '--vanilla', action='store_true')
	args = parser.parse_args()

	generate_worth(args.mc_version, no_cache=args.no_cache, essentials=not args.vanilla)
