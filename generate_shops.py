# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
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

# Items that will not yield a missing item warning
ignored_items = "(" + ")|(".join([
	r'.*commandblock.*',
	r'infested.*',
	'air',
	'light',
	'bedrock',
	'barrier',
	'debugstick',
	'structurevoid',
	'structureblock',
	'jigsaw',
	'endportalframe',
	'spawner',
	r'.*spawnegg',
	'knowledgebook',
	'petrifiedoakslab',
	'grasspath',
	'dirtpath',
	'reinforceddeepslate',
	'frogspawn',
	'netheritebricks', # Non-existent block
	'cutstandstoneslab' # Typo in 1.17+ source code
]) + ")"

def get_worth():
	worth_path = script_dir / "worth.yml"

	if not worth_path.exists():
		raise Exception('worth.yml not found. The file must be placed in the same file as this script.')

	worth_data = yaml.load(open(worth_path, 'r'), Loader=Loader)

	if 'worth' not in worth_data:
		raise Exception('worth.yml appears to be an invalid file; missing "worth" key.')

	return worth_data['worth']

def generate_shops(mc_version, outdir="BossShopPro"):
	if not mc_version:
		mc_version = get_latest_version()[1]

	source_path = prepare_source(mc_version)
	items = get_items(source_path, mc_version)
	worth = get_worth()

	outpath = output_dir / outdir
	os.makedirs(outpath, exist_ok=True)

	main_shop_data = {
		'ShopName': 'Menu',
		'DisplayName': '&8Menu',
		'Command': 'menu',
		'signs': {
			'text': '[Shop]',
			'NeedPermissionToCreateSign': True
		},
		'shop': {}
	}

	for group_name, group_data in items.items():
		group_title = group_name.replace('_', ' ').title()
		group_id = group_title.replace(' ', '')

		main_shop_data['shop'][group_id] = {
			'MenuItem': [
				{'name': f'&c{group_title}'},
				{'amount': 1},
				{'type': group_data['block']}
			],
			'RewardType': 'SHOP',
			'Reward': group_id,
			'PriceType': 'NOTHING'
		}

		shop_data = {
			'ShopName': group_id,
			'DisplayName': f'&8{group_title} &b(%page%/%maxpage%)',
			'Command': f'shop-{group_name.lower()}',
			'signs': {
				'text': f'[Shop{group_id}]',
				'NeedPermissionToCreateSign': True
			},
			'itemshop': {}
		}

		for i in group_data['items']:
			ikey = i.replace('_', '')
			if ikey in worth:
				shop_data['itemshop'][ikey] = {
					'Worth': worth[ikey],
					'Item': [
						{'type': i},
						{'amount': 64}
					]
				}
			elif not re.match(ignored_items, ikey):
				print(f"Warning: item {ikey} is not in worth.yml!")

		with open(outpath / 'Shop{0}.yml'.format(group_title.replace(' ', '')), 'w') as shopfile:
			shopfile.write(yaml.dump(shop_data, Dumper=Dumper, sort_keys=False))

	with open(outpath / 'Menu.yml', 'w') as shopfile:
		shopfile.write(yaml.dump(main_shop_data, Dumper=Dumper, sort_keys=False))

	return True

if __name__ == '__main__':
	generate_shops(sys.argv[1] if len(sys.argv) > 1 else None)