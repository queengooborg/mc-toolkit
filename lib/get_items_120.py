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

from .creative_only_items import creative_only_items

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
		if type(recipes[key]) == list:
			if new_recipe in recipes[key]:
				return # Ignore duplicates
			# print(f'Warning: multiple recipes detected for {key}!')
			recipes[key].append(new_recipe)
		else:
			if new_recipe == recipes[key]:
				return # Ignore duplicates
			# print(f'Warning: multiple recipes detected for {key}!')
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

# Create recipe for common block variants
def create_variant_recipe(variant, cost):
	if variant == 'button':
		return {
			'count': 1,
			'ingredients': {
				cost: 1,
			},
			'pattern': None
		}
	elif variant in ['carpet', 'pressurePlate']:
		return {
			'count': 3 if variant == 'carpet' else 1,
			'ingredients': {
				cost: 2,
			},
			'pattern': [[cost, cost]]
		}
	elif variant in ['chiseled', 'mosaic']:
		return {
			'count': 1,
			'ingredients': {
				cost: 2,
			},
			'pattern': [[cost], [cost]]
		}
	elif variant == 'cracked':
		return {
			'count': 1,
			'ingredients': {
				cost: 1
			},
			'pattern': 'furnace'
		}
	elif variant == 'cut':
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
	elif variant == 'door':
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
	elif variant in ['fence', 'customFence']:
		return {
			'count': 1,
			'ingredients': {
				cost: 4,
				'STICK': 2
			},
			'pattern': [
				[cost, 'STICK', cost],
				[cost, 'STICK', cost]
			]
		}
	elif variant in ['fenceGate', 'customFenceGate']:
		return {
			'count': 1,
			'ingredients': {
				cost: 2,
				'STICK': 4
			},
			'pattern': [
				['STICK', cost, 'STICK'],
				['STICK', cost, 'STICK']
			]
		}
	elif variant == 'polished':
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
	elif variant in ['sign', 'banner']:
		return {
			'count': 3 if variant == 'sign' else 1,
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
	elif variant == 'slab':
		return {
			'count': 6,
			'ingredients': {
				cost: 3,
			},
			'pattern': [[cost, cost, cost]]
		}
	elif variant == 'stairs':
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
	elif variant in ['trapdoor', 'wall']:
		return {
			'count': 2 if variant == 'trapdoor' else 6,
			'ingredients': {
				cost: 6,
			},
			'pattern': [
				[cost, cost, cost],
				[cost, cost, cost]
			]
		}
	else:
		raise Exception(f'Unhandled type "{func_type}" detected for simple recipe function!')

# Simple recipe functions -- see net.minecraft.data.recipes.RecipeProvider (1.20.2)
def simple_func(func_type, match):
	cost = match.group(5) or match.group(6)
	count = int(match.group(8) or 1)

	if func_type == 'banner':
		return create_variant_recipe('banner', cost)
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
		return create_variant_recipe('carpet', cost)
	elif func_type in ['chiseled', 'chiseledBuilder']:
		return create_variant_recipe('slab', cost)
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
		return create_variant_recipe('cut', cost)
	elif func_type == 'doorBuilder':
		return create_variant_recipe('door', cost)
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
		return create_variant_recipe('mosaic', cost)
	elif func_type in ['planksFromLog', 'planksFromLogs']:
		return {
			'count': count or 4,
			'ingredients': {
				cost: 1,
			},
			'pattern': None
		}
	elif func_type in ['polished', 'polishedBuilder']:
		return create_variant_recipe('polished', cost)
	elif func_type == 'pressurePlate':
		return create_variant_recipe('pressurePlate', cost)
	elif func_type in ['slab', 'slabBuilder']:
		return create_variant_recipe('slab', cost)
	elif func_type == 'stairBuilder':
		return create_variant_recipe('stairs', cost)
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
		return create_variant_recipe('wall', cost)
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
		raise Exception(f'Unhandled type "{func_type}" detected for simple recipe function!')

def process_VanillaRecipe_line(recipes, line, simplest_only, dye_colors, smeltables):
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
		if match.group(1) == 'SMELTS_TO_GLASS':
			add_recipe(recipes, match.group(2), {
				'count': 1,
				'ingredients': {
					'SAND': 1
				},
				'pattern': 'furnace'
			})
			add_recipe(recipes, match.group(2), {
				'count': 1,
				'ingredients': {
					'RED_SAND': 1
				},
				'pattern': 'furnace'
			})
		else:
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

	# Recoloring wool, bed and carpet -- see net.minecraft.data.recipes.VanillaRecipeProvider (1.20.2)
	match = re.match(rf'{line_prefix}VanillaRecipeProvider\.colorBlockWithDye\(recipeOutput, list, list\d, "(\w+)"\)', line)
	if match:
		item = match.group(1).upper()
		if simplest_only and item != 'WOOL':
			return # Beds and carpets can be crafted directly with colored wool
		for color in dye_colors:
			if simplest_only and item == 'WOOL' and color == 'WHITE':
				continue # White wool can be crafted directly with string
			add_recipe(recipes, f'{color}_{item}', {
				'count': 1,
				'ingredients': {
					item: 1,
					f'{color}_DYE': 1
				},
				'pattern': None
			})
		return

	# Recoloring Shulker Boxes
	match = re.match(rf'{line_prefix}SpecialRecipeBuilder\.special\(RecipeSerializer\.SHULKER_BOX_COLORING\)', line)
	if match:
		for color in dye_colors:
			add_recipe(recipes, f'{color}_SHULKER_BOX', {
				'count': 1,
				'ingredients': {
					'SHULKER_BOX': 1,
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
		add_recipe(recipes, match.group(1), {
			'count': int(match.groupdict().get('count', 1)),
			'ingredients': {
				match.group(2): 1
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
	match = re.match(rf'{line_prefix}VanillaRecipeProvider\.nineBlockStorageRecipes(?:(?:Recipes)?WithCustom(?:Packing|Unpacking))?\(recipeOutput, RecipeCategory\.[\w_]+, {one_ingredient_regex}, RecipeCategory\.[\w_]+, {one_ingredient_regex}', line)
	if match:
		is_nugget = match.group(1).endswith("_NUGGET")
		# 1 block to 9 items
		if not simplest_only or is_nugget:
			add_recipe(recipes, match.group(1), {
				'count': 9,
				'ingredients': {
					match.group(2): 1
				},
				'pattern': None
			})
		# 9 items to 1 block
		if not (is_nugget and simplest_only):
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
		if match_type.startswith('planksFromLog'):
			# Add "recipes" for stripped logs
			add_recipe(recipes, f"STRIPPED_{match.group(5).replace('LOGS', 'LOG').replace('BLOCKS', 'BLOCK').replace('STEMS', 'STEM')}", {
				'count': 1,
				'ingredients': {
					match.group(5): 1
				},
				'pattern': 'axe'
			})

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
			# match = re.match(r'^\s+public static final /\* enum \*/ DyeColor ([\w_]+) = new DyeColor\(', line)
			match = re.match(r'^\s+(\w+)\(\d+, "\w+", ', line)
			if match:
				dye_colors.append(match.group(1))
				continue

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
				continue

	# Get recipes for waxable items
	with open(Path(f"{source_path}/world/item/HoneycombItem.java")) as dcj:
		for line in dcj.readlines():
			match = re.match(rf'^\s+public static final Supplier<BiMap<Block, Block>> WAXABLES = ', line)
			if match:
				pairs = re.finditer(rf'\.put\(\(Object\){one_ingredient_regex}, \(Object\){one_ingredient_regex}\)', line)
				for pair in pairs:
					add_recipe(recipes, pair.group(2), {
						'count': 1,
						'ingredients': {
							pair.group(1): 1,
							'HONEYCOMB': 1
						},
						'pattern': None
					})
				continue

	# Get recipes for block families (stairs, fences, etc.)
	with open(Path(f"{source_path}/data/BlockFamilies.java")) as bfj:
		for line in bfj.readlines():
			match = re.match(rf'^\s+public static final BlockFamily [\w_]+ = BlockFamilies\.familyBuilder\({one_ingredient_regex}\)(.*)\.getFamily\(\);$', line)
			if match:
				sets = re.finditer(rf'\.(\w+)\({one_ingredient_regex}(?:, {one_ingredient_regex})?\)', match.group(2))
				for s in sets:
					variant = s.group(1)
					if variant == 'mosaic':
						continue # Bamboo Mosaic recipe is defined elsewhere
					add_recipe(recipes, s.group(2), create_variant_recipe(variant, match.group(1)))

	with open(Path(f"{source_path}/data/recipes/packs/VanillaRecipeProvider.java")) as vrpj:
		for line in vrpj.readlines():
			# Get smeltables lists
			match = re.match(rf'^\s+private static final ImmutableList<ItemLike> (\w+_SMELTABLES) = ImmutableList\.of\(\(Object\)Items\.([\w_]+)(?:, \(Object\)Items\.([\w_]+))*\);', line)
			if match:
				smeltables[match.group(1)] = match.groups()[1:]
				continue

			# Process recipe lines
			process_VanillaRecipe_line(recipes, line, simplest_only, dye_colors, smeltables)

	# Add "recipes" for concrete
	for color in dye_colors:
		add_recipe(recipes, f'{color}_CONCRETE', {
			'count': 1,
			'ingredients': {
				f'{color}_CONCRETE_POWDER': 1
			},
			'pattern': 'submerge'
		})

	# Add "recipe" for dirt path and farmland
	add_recipe(recipes, 'DIRT_PATH', {
		'count': 1,
		'ingredients': {
			'DIRT': 1
		},
		'pattern': 'shovel'
	})
	add_recipe(recipes, 'FARMLAND', {
		'count': 1,
		'ingredients': {
			'DIRT': 1
		},
		'pattern': 'hoe'
	})

	return recipes

# Get items list
def get_items(source_path, mc_version, include_creative=False, all_recipes=False):
	items = {}
	categories = {}
	recipes = get_recipes(source_path, simplest_only=not all_recipes)

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
