# -*- coding: utf-8 -*-

# 
# mc-toolkit - lib/get_items
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Get items list from the Minecraft source code, sorted by creative mode tabs
#

import os, re, json
from pathlib import Path

from .get_items_113 import get_items as get_items_113
from .get_items_1193 import get_items as get_items_1193
from .creative_only_items import creative_only_items
from .version import Version

cache_dir = Path(os.path.dirname(__file__)) / "../output/itemcache"

def main(source_path, mc_version, no_cache=False, include_creative=False, all_recipes=False):
	cache_path = cache_dir / (mc_version + ("_creative" if include_creative else "") + ("_all-recipes" if all_recipes else "") + ".json")

	if cache_path.exists() and not no_cache:
		return json.load(open(cache_path, 'r'))

	data = {}
	if mc_version >= Version('1.19.3'):
		data = get_items_1193(source_path, mc_version, include_creative)
	else:
		data = get_items_113(source_path, mc_version, include_creative)

	# Cache data
	os.makedirs(cache_dir, exist_ok=True)
	with open(cache_path, 'w') as cachefile:
		json.dump(data, cachefile)

	return data
