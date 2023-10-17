# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro - generate_items.py
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Generate an items list
#

import argparse, os, json
from pathlib import Path

from DecompilerMC.main import get_latest_version
from lib import prepare_source, get_items

script_dir = Path(os.path.dirname(__file__))
output_dir = script_dir / "output"

def generate_items(mc_version, no_cache=False, outpath=output_dir / "items.json"):
	if not mc_version:
		mc_version = get_latest_version()[1]

	source_path = prepare_source(mc_version)
	items = get_items(source_path, mc_version, no_cache)

	with open(outpath, 'w') as f:
		json.dump(items, f,  ensure_ascii=False, indent=2)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(prog="generate_items", description="Generate a list of items by scanning the Minecraft source code")
	parser.add_argument('mc_version', nargs='?')
	parser.add_argument('-n', '--no_cache', action='store_true')
	args = parser.parse_args()

	generate_items(args.mc_version, no_cache=args.no_cache)
