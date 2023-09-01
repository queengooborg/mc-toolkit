# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# This program takes a decompiled version of Minecraft and create an ordered list of all the blocks and their designated tabs.  After that, by taking an EssentialsX worth.yml, generates an item shop for BossShopPro + BS-ItemShops on Bukkit/Spigot/Paperclip servers.
# Developed and tested for 1.14 through 1.19.
#
# Requirements:
# - Java 8+
# - Python 3.7+
# - PyYAML (pip install pyyaml)
# - DecompilerMC (https://github.com/hube12/DecompilerMC) (added as a submodule)
#

import os, sys, glob, re, subprocess
from collections import OrderedDict
from pathlib import Path
from DecompilerMC.main import get_latest_version

import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

script_dir = os.path.dirname(__file__)

outpath = os.path.join(script_dir, "output")

worth = yaml.load(open(os.path.join(script_dir, "worth.yml"), 'r'), Loader=Loader).get('worth', {})

shop_blocks = {
	'BUILDING_BLOCKS': 'BRICKS',
	'DECORATIONS': 'PEONY',
	'REDSTONE': 'REDSTONE',
	'TRANSPORTATION': 'POWERED_RAIL',
	'MISC': 'LAVA_BUCKET',
	'FOOD': 'APPLE',
	'TOOLS': 'IRON_AXE',
	'COMBAT': 'GOLDEN_SWORD',
	'BREWING': 'POTION',
}

# Items that will not yield a missing item warning
ignored_items = "(" + ")|(".join([
	r'.*commandblock.*',
	r'infested.*',
	'air',
	'barrier',
	'debugstick',
	'structurevoid',
	'structureblock',
	'jigsaw',
	'endportalframe',
	'spawner',
	r'.*spawnegg',
	'knowledgebook',
	'bedrock',
	'petrifiedoakslab',
	'grasspath',
	'dirtpath',
	'netheritebricks',
	'light',
	'reinforceddeepslate',
	'frogspawn',
	'cutstandstoneslab' # Typo in 1.17+ source code
]) + ")"

def run_subprocess(cmd, cwd, *args, **kwargs):
	r = subprocess.run(cmd, cwd=str(cwd), *args, **kwargs)
	return r.returncode

def prepare_source(mc_version):
	sourcepath = Path(f"DecompilerMC/src/{mc_version}/client")

	if not (sourcepath.exists()):
		print("Decompiled sources not found, performing decompilation now...  This may take a while, please be patient!\n")

		if run_subprocess(["python3", "main.py", f"--mcversion={mc_version}", "--quiet"], Path("DecompilerMC")) != 0:
			print("Failed to decompile sources, please try again")
			return False

		print("\nDecompilation complete!")

	source_path = glob.glob(str(sourcepath))
	return Path(f"{source_path[0]}/net/minecraft")

def get_items(source_path, mc_version):
	if mc_version < '1.17':
		itemgroupname = 'ItemGroup'
		itemgroupjava = Path(f"{source_path}/item/{itemgroupname}.java")
		itemsjava = Path(f"{source_path}/item/Items.java")
	else:
		itemgroupname = 'CreativeModeTab'
		itemgroupjava = Path(f"{source_path}/world/item/{itemgroupname}.java")
		itemsjava = Path(f"{source_path}/world/item/Items.java")

	items = OrderedDict()

	with open(str(itemgroupjava), 'r') as igj:
		for line in igj.readlines():
			match = re.search(rf"public static final {itemgroupname} (\w+) = \(?new {itemgroupname}\((\d+), \"(\w+)\"\) {{", line)
			if match:
				items[match.group(1).replace('TAB_', '')] = []
		items['MISC'] = []

	with open(str(itemsjava), 'r') as ij:
		for line in ij.readlines():
			match = re.search(rf"public static final Item (\w+) = .+{itemgroupname}\.(\w+).+", line)
			if match:
				group = match.group(2).replace('TAB_', '')
				if group in items:
					items[group].append(match.group(1).lower())
				elif group == 'MATERIALS':
					items['MISC'].append(match.group(1).lower())
			else:
				match2 = re.search(r"public static final Item (\w+) = .+", line)
				if match2:
					items['MISC'].append(match2.group(1).lower())

	return items

def make_shops(mc_version):
	if not mc_version:
		mc_version = get_latest_version()[1]

	source_path = prepare_source(mc_version)
	if not source_path:
		return False

	all_items = get_items(source_path, mc_version)

	os.makedirs(outpath, exist_ok=True)

	main_shop_data = """ShopName: Menu
DisplayName: '&8Menu'
Command: menu
signs:
  text: '[Shop]'
  NeedPermissionToCreateSign: true
shop:
"""

	for ig in all_items.items():
		group_name, items = ig
		group_title = group_name.replace('_', ' ').title()
		group_id = group_title.replace(' ', '')
		if not items: continue

		shop_data = f"""ShopName: {group_id}
DisplayName: '&8{group_title} &b(%page%/%maxpage%)'
Command: shop-{group_name.lower()}
signs:
  text: '[Shop{group_id}]'
  NeedPermissionToCreateSign: true
itemshop:
"""

		for i in items:
			ikey = i.replace('_', '')
			if ikey in worth:
				shop_data += f"""  {ikey}:
    Worth: {worth[ikey]}
    Item:
    - type:{i}
    - amount:64
"""
			elif not re.match(ignored_items, ikey):
				print(f"Warning: item {ikey} is not in worth.yml!")

		with open(os.path.join(outpath, 'Shop{0}.yml'.format(group_title.replace(' ', ''))), 'w') as shopfile:
			shopfile.write(shop_data)

		main_shop_data += f"""  {group_id}:
    MenuItem:
    - name:&c{group_title}
    - amount:1
    - type:{shop_blocks[group_name]}
    RewardType: SHOP
    Reward: {group_id}
    PriceType: NOTHING
"""

	with open(os.path.join(outpath, 'Menu.yml'), 'w') as shopfile:
		shopfile.write(main_shop_data)

	return True

if __name__ == '__main__':
	make_shops(sys.argv[1] if len(sys.argv) > 1 else None)
