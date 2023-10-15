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

def format_item_name(name):
	if type(name) == str:
		return name
	return "/".join(filter(lambda n: n != None, name))

# Add a new recipe to the recipes list for the item
def add_recipe(recipes, key, new_recipe):
	if key in recipes:
		print(f'Warning: multiple recipes detected for {key}!')
		if type(recipes[key]) == list:
			recipes[key].append(new_recipe)
		else:
			recipes[key] = [recipes[key], new_recipe]
	else:
		recipes[key] = new_recipe

# Convert a raw recipe pattern from source code into a sensible pattern
def convert_recipe_pattern(ingredients, raw_pattern):
	count = {i: 0 for i in ingredients.values()}

	pattern = []

	for raw_row in raw_pattern:
		row = []
		for key in raw_row:
			if key == ' ':
				row.append("")
			elif key in ingredients:
				row.append(ingredients[key])
				count[ingredients[key]] += 1
			else:
				raise Exception(f'Character "{key}" found in pattern, but corresponding ingredient does not exist (have {ingredients.items()})')
		pattern.append(row)

	return pattern, count

# Simple recipe functions -- see net.minecraft.data.recipes.RecipeProvider (1.20.2)
def simple_func(func_type, match):
	if func_type == 'banner':
		return {
			'count': 1,
			'ingredients': {
				match.group(3): 6,
				'STICK': 1
			},
			pattern: [
				[match.group(3), match.group(3), match.group(3)],
				[match.group(3), match.group(3), match.group(3)],
				['', 'STICK', '']
			]
		}
	elif func_type == 'bedFromPlanksAndWool':
		return {
			'count': 1,
			'ingredients': {
				match.group(3): 3,
				'PLANKS': 3
			},
			pattern: [
				[match.group(3), match.group(3), match.group(3)],
				['PLANKS', 'PLANKS', 'PLANKS']
			]
		}
	elif func_type == 'candle':
		return {
			'count': 1,
			'ingredients': {
				match.group(3): 1,
				'CANDLE': 1
			},
			pattern: None
		}
	elif func_type == 'carpet':
		return {
			'count': 3,
			'ingredients': {
				match.group(3): 2
			},
			pattern: [[match.group(3), match.group(3)]]
		}
	elif func_type == 'chestBoat':
		return {
			'count': 1,
			'ingredients': {
				match.group(3): 1,
				'CHEST': 1
			},
			pattern: None
		}
	elif func_type == 'coloredTerracottaFromTerracottaAndDye':
		return {
			'count': 8,
			'ingredients': {
				match.group(3): 1,
				'TERRACOTTA': 8
			},
			pattern: [
				['TERRACOTTA', 'TERRACOTTA', 'TERRACOTTA'],
				['TERRACOTTA', match.group(3), 'TERRACOTTA'],
				['TERRACOTTA', 'TERRACOTTA', 'TERRACOTTA']
			]
		}
	elif func_type == 'concretePowder':
		return {
			'count': 8,
			'ingredients': {
				match.group(3): 1,
				'SAND': 4,
				'GRAVEL': 4
			},
			pattern: None
		}
	elif func_type == 'copySmithingTemplate':
		pass
	elif func_type == 'hangingSign':
		pass
	elif func_type == 'pressurePlate':
		pass
	elif func_type == 'stainedGlassFromGlassAndDye':
		pass
	elif func_type == 'stainedGlassPaneFromGlassPaneAndDye':
		pass
	elif func_type == 'stainedGlassPaneFromStainedGlass':
		pass
	elif func_type == 'woodenBoat':
		pass
	elif func_type == 'woodFromLogs':
		pass
	else:
		raise Exception(f'Unhandled type "{func_type}" detected for simple recipe function!')

# Get item recipes
def get_recipes(source_path, simplest_only=True):
	recipes = {}

	dye_colors = []
	smeltables = {}

	line_prefix = r"^\s*(?:\(\((?:Shaped|Shapeless)RecipeBuilder\))*"
	one_ingredient_regex = r"(?:Blocks|Items|ItemTags)\.([\w_]+)(?:\.asItem\(\))?"
	ingredient_regex = rf"(?:{one_ingredient_regex}|Ingredient\.of\({one_ingredient_regex}(?:, {one_ingredient_regex})*\))"

	# Get all dye colors
	with open(Path(f"{source_path}/world/item/DyeColor.java")) as dcj:
		for line in dcj.readlines():
			match = re.match(r'^\s+public static final /\* enum \*/ DyeColor ([\w_]+) = new DyeColor\(', line)
			if match:
				dye_colors.append(match.group(1))

	with open(Path(f"{source_path}/data/recipes/packs/VanillaRecipeProvider.java")) as rj:
		for line in rj.readlines():
			# Get smeltables lists
			match = re.match(rf'^\s+private static final ImmutableList<ItemLike> (\w+)_SMELTABLES = ImmutableList\.of\(\(Object\)Items\.([\w_]+)(?:, \(Object\)Items\.([\w_]+))*\);', line)
			if match:
				smeltables[match.group(1)] = match.groups()[1:]
				continue

			# Ignore blasting recipes; all are duplicates of smelting (as of 1.20.2)
			if 'SimpleCookingRecipeBuilder.blasting(' in line:
				continue

			# Shapeless recipes
			match = re.match(rf'{line_prefix}ShapelessRecipeBuilder\.shapeless\(RecipeCategory\.[\w_]+, (?:Blocks|Items)\.([\w_]+)(?:, (\d+))?\)', line)
			if match:
				add_recipe(recipes, match.group(1), {
					'count': int(match.group(2) or 1),
					'ingredients': {
						format_item_name(i.group(1) or i.groups()[1:-1]): int(i.groupdict().get('count', 1)) for i in re.finditer(rf'\.requires\({ingredient_regex}(?:, (/P<count>\d+))?\)', line)
					},
					'pattern': None
				})
				continue

			# Shaped recipes
			match = re.match(rf'{line_prefix}ShapedRecipeBuilder\.shaped\(RecipeCategory\.[\w_]+, (?:Blocks|Items)\.([\w_]+)(?:, (\d+))?\)', line)
			if match:
				item = match.group(1)
				ingredients = {i.group(1): format_item_name(i.group(2) or i.groups()[2:]) for i in re.finditer(rf"\.define\(Character\.valueOf\('(.)'\), {ingredient_regex}\)", line)}
				raw_pattern = [list(p.group(1)) for p in re.finditer(r'\.pattern\("([^"]+)"\)', line)]

				pattern, count = convert_recipe_pattern(ingredients, raw_pattern)

				add_recipe(recipes, item, {
					'count': int(match.group(2) or 1),
					'ingredients': count,
					'pattern': pattern
				})

				continue

			# Smelting recipes
			match = re.match(rf'{line_prefix}SimpleCookingRecipeBuilder\.smelting\(Ingredient\.of\({one_ingredient_regex}\), RecipeCategory\.[\w_]+, {one_ingredient_regex}', line)
			if match:
				add_recipe(recipes, match.group(2), {
					'count': 1,
					'ingredients': match.group(1),
					'pattern': 'furnace'
				})
				continue

			if not simplest_only:
				# Recoloring wool, bed and carpet
				match = re.match(rf'{line_prefix}VanillaRecipeProvider\.colorBlockWithDye\(recipeOutput, list, list\d, "(\w+)"\)', line)
				if match:
					item = match.group(1).upper()
					for color in dye_colors:
						add_recipe(recipes, f'{color}_{item}', {
							'count': 1,
							'ingredients': {
								item: 1,
								f'{color}_DYE': 1
							},
							'pattern': None
						})
					continue

			# Simple recipe functions -- see net.minecraft.data.recipes.RecipeProvider (1.20.2)
			match = re.match(rf'{line_prefix}VanillaRecipeProvider\.(\w+)\(recipeOutput, (?:\(ItemLike\))?{ingredient_regex}, {ingredient_regex}\);', line)
			if match:
				match_type = match.group(1)
				add_recipe(recipes, match_type, simple_func(match_type, match))

	return recipes

# Get items list
def get_items(source_path, mc_version):
	items = {}
	recipes = get_recipes(source_path)

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
					items[current_group.group(1)]['items'][item] = recipe
				else:
					items[current_group.group(1)] = {
						'block': current_group.group(2),
						'items': {
							item: recipe
						}
					}

	return items
