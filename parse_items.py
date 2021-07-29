# -*- coding: utf-8 -*-

#
# This program takes a decompiled version of Minecraft and create an ordered list of all the blocks and their designated tabs.  After that, by taking an EssentialsX worth.yml, generates an item shop for BossShopPro + BS-ItemShops on Bukkit/Spigot/Paperclip servers.
# Developed and tested for 1.14 through 1.16, may work on all versions from 1.13 on.
# Requirements:
# - A Minecraft Forge MDK
#   - Initialize using `gradlew eclipse` then `gradlew prepareRunClient` to decompile the Minecraft source code.
# - PyYAML
#

import os
import re
from collections import OrderedDict

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

minecraft_source = os.path.abspath("/Users/vinyldarkscratch/Developer/Forge MDK/forge-1.16.1-32.0.61-mdk/build/tmp/expandedArchives/forge-1.16.1-32.0.61_mapped_snapshot_20200707-1.16.1-sources.jar_8b7ec6ab0a9d6699309ef77a0ea9c952/net/minecraft")
itemgroupjava = os.path.join(minecraft_source, 'item', 'ItemGroup.java')
itemsjava = os.path.join(minecraft_source, 'item', 'Items.java')

worthfile = "./worth.yml"
outpath = "./output"

worth = yaml.load(open(worthfile, 'r'), Loader=Loader).get('worth', {})

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

def get_items():
	items = OrderedDict()

	with open(itemgroupjava, 'r') as igj:
		for line in igj.readlines():
			match = re.search(r"public static final ItemGroup (\w+) = \(?new ItemGroup\((\d+), \"(\w+)\"\) {", line)
			if match:
				items[match.group(1)] = []

	with open(itemsjava, 'r') as ij:
		for line in ij.readlines():
			match = re.search(r"public static final Item (\w+) = .+ItemGroup\.(\w+).+", line)
			if match and match.group(2) in items:
				items[match.group(2)].append(match.group(1).lower())
			elif match and match.group(2) == 'MATERIALS':
				items['MISC'].append(match.group(1).lower())
			else:
				match2 = re.search(r"public static final Item (\w+) = .+", line)
				if match2:
					items['MISC'].append(match2.group(1).lower())

	return items

def make_shops():
	os.makedirs(outpath, exist_ok=True)

	main_shop_data = """ShopName: Menu
DisplayName: '&8Menu'
Command: menu
signs:
  text: '[Shop]'
  NeedPermissionToCreateSign: true
shop:
"""

	for ig in get_items().items():
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
			else:
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

if __name__ == '__main__':
	make_shops()
