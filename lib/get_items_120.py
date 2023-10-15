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

line_prefix = r"^\s*(?:\(\((?:Shaped|Shapeless)RecipeBuilder\))*"
one_ingredient_regex = r"(?:Blocks|Items|ItemTags)\.([\w_]+)(?:\.asItem\(\))?"
ingredient_regex = rf"(?:{one_ingredient_regex}|Ingredient\.of\({one_ingredient_regex}(?:, {one_ingredient_regex})*\))"

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
	cost = match.group(5) or match.group(6)
	count = int(match.group(8) or 1)

	if func_type == 'banner':
		return {
			'count': 1,
			'ingredients': {
				cost: 6,
				'STICK': 1
			},
			'pattern': [
				[cost, cost, cost],
				[cost, cost, cost],
				['', 'STICK', '']
			]
		}
	elif func_type == 'bedFromPlanksAndWool':
		return {
			'count': 1,
			'ingredients': {
				cost: 3,
				'PLANKS': 3
			},
			'pattern': [
				[cost, cost, cost],
				['PLANKS', 'PLANKS', 'PLANKS']
			]
		}
	elif func_type == 'candle':
		return {
			'count': 1,
			'ingredients': {
				cost: 1,
				'CANDLE': 1
			},
			'pattern': None
		}
	elif func_type == 'carpet':
		return {
			'count': 3,
			'ingredients': {
				cost: 2
			},
			'pattern': [[cost, cost]]
		}
	elif func_type in ['chiseled', 'chiseledBuilder']:
		return {
			'count': 1,
			'ingredients': {
				cost: 2,
			},
			'pattern': [[cost], [cost]]
		}
	elif func_type == 'chestBoat':
		return {
			'count': 1,
			'ingredients': {
				cost: 1,
				'CHEST': 1
			},
			'pattern': None
		}
	elif func_type == 'coloredTerracottaFromTerracottaAndDye':
		return {
			'count': 8,
			'ingredients': {
				cost: 1,
				'TERRACOTTA': 8
			},
			'pattern': [
				['TERRACOTTA', 'TERRACOTTA', 'TERRACOTTA'],
				['TERRACOTTA', cost, 'TERRACOTTA'],
				['TERRACOTTA', 'TERRACOTTA', 'TERRACOTTA']
			]
		}
	elif func_type == 'concretePowder':
		return {
			'count': 8,
			'ingredients': {
				cost: 1,
				'SAND': 4,
				'GRAVEL': 4
			},
			'pattern': None
		}
	elif func_type in ['cut', 'cutBuilder']:
		return {
			'count': 4,
			'ingredients': {
				cost: 4,
			},
			'pattern': [
				[cost, cost],
				[cost, cost]
			]
		}
	elif func_type == 'doorBuilder':
		return {
			'count': 3,
			'ingredients': {
				cost: 6,
			},
			'pattern': [
				[cost, cost],
				[cost, cost],
				[cost, cost]
			]
		}
	elif func_type == 'hangingSign':
		return {
			'count': 6,
			'ingredients': {
				cost: 6,
				'CHAIN': 2,
			},
			'pattern': [
				['CHAIN', '', 'CHAIN'],
				[cost, cost, cost],
				[cost, cost, cost]
			]
		}
	elif func_type == 'mosaicBuilder':
		return {
			'count': 1,
			'ingredients': {
				cost: 2,
			},
			'pattern': [[cost], [cost]]
		}
	elif func_type in ['planksFromLog', 'planksFromLogs']:
		return {
			'count': count or 4,
			'ingredients': {
				cost: 1,
			},
			'pattern': None
		}
	elif func_type in ['polished', 'polishedBuilder']:
		return {
			'count': 4,
			'ingredients': {
				cost: 4
			},
			'pattern': [
				[cost, cost],
				[cost, cost]
			]
		}
	elif func_type == 'pressurePlate':
		return {
			'count': 2,
			'ingredients': {
				cost: 2
			},
			'pattern': [[cost, cost]]
		}
	elif func_type in ['slab', 'slabBuilder']:
		return {
			'count': 6,
			'ingredients': {
				cost: 3,
			},
			'pattern': [[cost, cost, cost]]
		}
	elif func_type == 'stairBuilder':
		return {
			'count': 4,
			'ingredients': {
				cost: 6
			},
			'pattern': [
				[cost, '', ''],
				[cost, cost, ''],
				[cost, cost, cost]
			]
		}
	elif func_type == 'stainedGlassFromGlassAndDye':
		return {
			'count': 8,
			'ingredients': {
				cost: 1,
				'GLASS': 8,
			},
			'pattern': [
				['GLASS', 'GLASS', 'GLASS'],
				['GLASS', cost, 'GLASS'],
				['GLASS', 'GLASS', 'GLASS']
			]
		}
	elif func_type == 'stainedGlassPaneFromGlassPaneAndDye':
		return {
			'count': 8,
			'ingredients': {
				cost: 1,
				'GLASS_PANE': 8,
			},
			'pattern': [
				['GLASS_PANE', 'GLASS_PANE', 'GLASS_PANE'],
				['GLASS_PANE', cost, 'GLASS_PANE'],
				['GLASS_PANE', 'GLASS_PANE', 'GLASS_PANE']
			]
		}
	elif func_type == 'stainedGlassPaneFromStainedGlass':
		return {
			'count': 16,
			'ingredients': {
				cost: 6
			},
			'pattern': [
				[cost, cost, cost],
				[cost, cost, cost]
			]
		}
	elif func_type == 'stonecutterResultFromBase':
		return {
			'count': count or 1,
			'ingredients': {
				cost: 1
			},
			'pattern': 'stonecutter'
		}
	elif func_type in ['wall', 'wallBuilder']:
		return {
			'count': 6,
			'ingredients': {
				cost: 6
			},
			'pattern': [
				[cost, cost, cost],
				[cost, cost, cost]
			]
		}
	elif func_type == 'woodenBoat':
		return {
			'count': 1,
			'ingredients': {
				cost: 5
			},
			'pattern': [
				[cost, '', cost],
				[cost, cost, cost]
			]
		}
	elif func_type == 'woodFromLogs':
		return {
			'count': 3,
			'ingredients': {
				cost: 4
			},
			'pattern': [
				[cost, cost],
				[cost, cost]
			]
		}
	else:
		print(match.group())
		raise Exception(f'Unhandled type "{func_type}" detected for simple recipe function!')

def process_recipe_line(recipes, line, dye_colors, smeltables):
	# Ignore blasting recipes; all are duplicates of smelting (as of 1.20.2)
	if 'SimpleCookingRecipeBuilder.blasting(' in line or 'VanillaRecipeProvider.oreBlasting(' in line:
		return

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
		return

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

		return

	# Smelting recipes
	match = re.match(rf'{line_prefix}SimpleCookingRecipeBuilder\.smelting\(Ingredient\.of\({one_ingredient_regex}\), RecipeCategory\.[\w_]+, {one_ingredient_regex}', line)
	if match:
		add_recipe(recipes, match.group(2), {
			'count': 1,
			'ingredients': {
				match.group(1): 1
			},
			'pattern': 'furnace'
		})
		return

	# Ore smelting recipes
	match = re.match(rf'{line_prefix}VanillaRecipeProvider\.oreSmelting\(recipeOutput, ([\w_]+), RecipeCategory\.[\w_]+, {one_ingredient_regex}', line)
	if match:
		add_recipe(recipes, match.group(2), {
			'count': 1,
			'ingredients': {
				format_item_name(smeltables.get(match.group(1))): 1
			},
			'pattern': 'furnace'
		})
		return

	# Stonecutting recipes
	match = re.match(rf'{line_prefix}SingleItemRecipeBuilder\.stonecutting\(Ingredient\.of\({one_ingredient_regex}\), RecipeCategory\.[\w_]+, {one_ingredient_regex}(?:, (\d+))?\)', line)
	if match:
		add_recipe(recipes, match.group(2), {
			'count': match.group(3) or 1,
			'ingredients': {
				match.group(1): 1
			},
			'pattern': 'stonecutter'
		})
		return

	# Netherite smithing recipes
	match = re.match(rf'{line_prefix}VanillaRecipeProvider\.netheriteSmithing\(recipeOutput, {one_ingredient_regex}, RecipeCategory\.[\w_]+, {one_ingredient_regex}', line)
	if match:
		add_recipe(recipes, match.group(2), {
			'count': 1,
			'ingredients': {
				match.group(1): 1,
				'NETHERITE_INGOT': 1
			},
			'pattern': 'smithingTable'
		})
		return

	if not simplest_only:
		# Recoloring wool, bed and carpet -- see net.minecraft.data.recipes.VanillaRecipeProvider (1.20.2)
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
			return

		# Smithing template copying -- see net.minecraft.data.recipes.RecipeProvider (1.20.2)
		match = re.match(rf'{line_prefix}VanillaRecipeProvider\.copySmithingTemplate\(recipeOutput, \(ItemLike\){one_ingredient_regex}, {one_ingredient_regex}\);', line)
		if match:
			add_recipe(recipes, match.group(2), {
				'count': 2,
				'ingredients': {
					match.group(2): 1,
					match.group(3): 1,
					'DIAMOND': 7,
				},
				'pattern': [
					['DIAMOND', match.group(2), 'DIAMOND'],
					['DIAMOND', match.group(3), 'DIAMOND'],
					['DIAMOND', 'DIAMOND', 'DIAMOND'],
				]
			})
			return

	# One-to-one conversion -- see net.minecraft.data.recipes.RecipeProvider (1.20.2)
	match = re.match(rf'{line_prefix}VanillaRecipeProvider\.oneToOneConversionRecipe\(recipeOutput, {one_ingredient_regex}, {one_ingredient_regex}(?:, "[\w_]+")?(?:, (/P<count>\d+))?', line)
	if match:
		add_recipe(recipes, match.group(2), {
			'count': int(match.groupdict().get('count', 1)),
			'ingredients': {
				match.group(3): 1
			},
			'pattern': None
		})
		return

	# 2x2/3x3 packer conversion -- see net.minecraft.data.recipes.RecipeProvider (1.20.2)
	match = re.match(rf'{line_prefix}VanillaRecipeProvider\.(twoByTwo|threeByThree)Packer\(recipeOutput(?:, RecipeCategory\.[\w_]+)?, {one_ingredient_regex}, {one_ingredient_regex}(?:, "[\w_]+")?(?:, (\d+))?\);', line)
	if match:
		if match.group(1) == 'twoByTwo':
			add_recipe(recipes, match.group(2), {
				'count': 1,
				'ingredients': {
					match.group(3): 4
				},
				'pattern': [
					[match.group(3), match.group(3)],
					[match.group(3), match.group(3)]
				]
			})
		else:
			add_recipe(recipes, match.group(2), {
				'count': 1,
				'ingredients': {
					match.group(3): 9
				},
				'pattern': None
			})
		return

	# 9x9 packer conversion -- see net.minecraft.data.recipes.RecipeProvider (1.20.2)
	match = re.match(rf'{line_prefix}VanillaRecipeProvider\.nineBlockStorageRecipes(?:WithCustom(?:Packing|Unpacking))?\(recipeOutput, RecipeCategory\.[\w_]+, {one_ingredient_regex}, RecipeCategory\.[\w_]+ {one_ingredient_regex}', line)
	if match:
		if not simplest_only:
			add_recipe(recipes, match.group(1), {
				'count': 9,
				'ingredients': {
					match.group(2): 1
				},
				'pattern': None
			})
		add_recipe(recipes, match.group(2), {
			'count': 1,
			'ingredients': {
				match.group(1): 9
			},
			'pattern': None
		})
		return

	# Simple recipe functions -- see net.minecraft.data.recipes.RecipeProvider (1.20.2)
	match = re.match(rf'{line_prefix}VanillaRecipeProvider\.(\w+)\((?:recipeOutput, )?(?:RecipeCategory\.[\w_]+, )?{ingredient_regex}, {ingredient_regex}(?:, (\d+))?', line)
	if match:
		match_type = match.group(1)
		if match_type == 'stainedGlassPaneFromGlassPaneAndDye' and simplest_only:
			return # Only use "stainedGlassPaneFromStainedGlass"
		add_recipe(recipes, match.group(2), simple_func(match_type, match))
		return

# Get item recipes
def get_recipes(source_path, simplest_only=True):
	recipes = {}

	dye_colors = []
	smeltables = {}

	# Get all dye colors
	with open(Path(f"{source_path}/world/item/DyeColor.java")) as dcj:
		for line in dcj.readlines():
			match = re.match(r'^\s+public static final /\* enum \*/ DyeColor ([\w_]+) = new DyeColor\(', line)
			if match:
				dye_colors.append(match.group(1))

	# Get recipes for cooked food
	with open(Path(f"{source_path}/data/recipes/RecipeProvider.java")) as dcj:
		for line in dcj.readlines():
			match = re.match(rf'^\s+RecipeProvider\.simpleCookingRecipe\(recipeOutput, string, recipeSerializer, n, {one_ingredient_regex}, {one_ingredient_regex}\);', line)
			if match:
				add_recipe(recipes, match.group(2), {
					'count': 1,
					'ingredients': {
						match.group(1): 1
					},
					'pattern': 'furnace'
				})

	# Get recipes for waxable items
	with open(Path(f"{source_path}/world/item/HoneycombItem.java")) as dcj:
		for line in dcj.readlines():
			match = re.match(rf'^public static final Supplier<BiMap<Block, Block>> WAXABLES = ', line)
			if match:
				pairs = re.finditer(rf'\.put\(\(Object\){one_ingredient_regex}, \(Object\){one_ingredient_regex}\)', line)
				add_recipe(recipes, match.group(2), {
					'count': 1,
					'ingredients': {
						match.group(1): 1,
						'HONEYCOMB': 1
					},
					'pattern': None
				})

	with open(Path(f"{source_path}/data/recipes/packs/VanillaRecipeProvider.java")) as rj:
		for line in rj.readlines():
			# Get smeltables lists
			match = re.match(rf'^\s+private static final ImmutableList<ItemLike> (\w+_SMELTABLES) = ImmutableList\.of\(\(Object\)Items\.([\w_]+)(?:, \(Object\)Items\.([\w_]+))*\);', line)
			if match:
				smeltables[match.group(1)] = match.groups()[1:]
				continue

			process_recipe_line(recipes, line, dye_colors, smeltables)

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
