# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro - lib/get_items
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Get items list from the Minecraft source code, sorted by creative mode tabs
#

import os, re, json
from pathlib import Path

from .get_items_113 import get_items as get_items_113
from .get_items_120 import get_items as get_items_120

cache_dir = Path(os.path.dirname(__file__)) / "../output/itemcache"

def main(source_path, mc_version, no_cache=False):
	cache_path = cache_dir / f"{mc_version}.json"

	if cache_path.exists() and not no_cache:
		return json.load(open(cache_path, 'r'))

	data = {}
	if mc_version >= '1.20':
		data = get_items_120(source_path, mc_version)
	else:
		data = get_items_113(source_path, mc_version)

	# Cache data
	os.makedirs(cache_dir, exist_ok=True)
	with open(cache_path, 'w') as cachefile:
		json.dump(data, cachefile)

	return data

def get_items_list(source_path, mc_version, no_cache=False):
	data = main(source_path, mc_version, no_cache=no_cache)
	items = {}

	for cat, catdata in data.items():
		items.update(catdata['items'])

	return items
