# -*- coding: utf-8 -*-

# 
# mc-toolkit - generate_shops.py
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Generate BossShopPro shops from a worth.yml file
#

import argparse, os, re
from pathlib import Path

from DecompilerMC.main import get_latest_version
from lib import get_items, prepare_source, Version
from generate_worth import generate_worth

import yaml
try:
	from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
	from yaml import Loader, Dumper

script_dir = Path(os.path.dirname(__file__))
output_dir = script_dir / "output"

# Items that will not yield a missing item warning
ignored_items = [
	'air',
	'light',
	'grasspath',
	'dirtpath',
	'netheritebricks', # Non-existent block
	'cutstandstoneslab' # Typo in 1.17+ source code
]

def get_worth(mc_version):
	worth_path = output_dir / "worth.yml"

	if not worth_path.exists():
		generate_worth(mc_version)

	worth_data = yaml.load(open(worth_path, 'r'), Loader=Loader)

	if 'worth' not in worth_data:
		raise Exception('worth.yml appears to be an invalid file; missing "worth" key.')

	return worth_data['worth']

def generate_shops(mc_version, no_cache=False, outpath=output_dir / "BossShopPro"):
	source_path = prepare_source(mc_version)
	items = get_items(source_path, mc_version, no_cache)
	worth = get_worth(mc_version)

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

	for group_name, group_data in items['categories'].items():
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

		for item in group_data['items']:
			ikey = item.lower().replace('_', '')
			if ikey in worth:
				shop_data['itemshop'][ikey] = {
					'Worth': worth[ikey],
					'Item': [
						{'type': item},
						{'amount': 64}
					]
				}
			elif not ikey in ignored_items:
				print(f"Warning: item {ikey} is not in worth.yml!")

		with open(outpath / 'Shop{0}.yml'.format(group_title.replace(' ', '')), 'w') as shopfile:
			shopfile.write(yaml.dump(shop_data, Dumper=Dumper, sort_keys=False))

	with open(outpath / 'Menu.yml', 'w') as shopfile:
		shopfile.write(yaml.dump(main_shop_data, Dumper=Dumper, sort_keys=False))

	return True

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog="generate_shops", description="Generate BossShopPro configuration files using an EssentialsX worth.yml and Minecraft deobfuscated source code")
	parser.add_argument('mc_version', nargs='?', default=get_latest_version()[1], help="The Minecraft version to use")
	parser.add_argument('-n', '--no_cache', action='store_true', help="Regenerate everything from scratch")
	parser.add_argument('-n', '--no_cache', action='store_true')
	args = parser.parse_args()

	generate_shops(Version(args.mc_version), no_cache=args.no_cache)
