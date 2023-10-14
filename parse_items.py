# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# This program takes a decompiled version of Minecraft and create an ordered list of all the blocks and their designated tabs.  After that, by taking an EssentialsX worth.yml, generates an item shop for BossShopPro + BS-ItemShops on Bukkit/Spigot/Paperclip servers.
# Developed and tested for 1.14 through 1.20. (Note: 1.20 implementation is currently experimental)
#
# Requirements:
# - Java 8+
# - Python 3.7+
# - PyYAML (pip install pyyaml)
# - DecompilerMC (https://github.com/hube12/DecompilerMC) (added as a submodule)
#

import os, sys, glob, re, subprocess
from pathlib import Path

from DecompilerMC.main import get_latest_version
from lib import get_items, prepare_source

import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

script_dir = Path(os.path.dirname(__file__))
output_dir = script_dir / "output"
worth = yaml.load(open(script_dir / "worth.yml", 'r'), Loader=Loader).get('worth', {})

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

def make_shops(mc_version, outdir="BossShopPro"):
	if not mc_version:
		mc_version = get_latest_version()[1]

	source_path = prepare_source(mc_version)
	(groups, all_items) = get_items(source_path, mc_version)

	outpath = output_dir / outdir
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

		with open(outpath / 'Shop{0}.yml'.format(group_title.replace(' ', '')), 'w') as shopfile:
			shopfile.write(shop_data)

		main_shop_data += f"""  {group_id}:
    MenuItem:
    - name:&c{group_title}
    - amount:1
    - type:{groups[group_name]}
    RewardType: SHOP
    Reward: {group_id}
    PriceType: NOTHING
"""

	with open(outpath / 'Menu.yml', 'w') as shopfile:
		shopfile.write(main_shop_data)

	return True

if __name__ == '__main__':
	make_shops(sys.argv[1] if len(sys.argv) > 1 else None)
