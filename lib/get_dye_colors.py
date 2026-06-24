# -*- coding: utf-8 -*-

# 
# mc-toolkit - lib/get_dye_colors
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Get all of the dye colors
#

import re
from pathlib import Path

def get_dye_colors(source_path):
	dye_colors = []

	# Get all dye colors
	with open(Path(f"{source_path}/world/item/DyeColor.java")) as dcj:
		for line in dcj.readlines():
			# match = re.match(r'^\s+public static final /\* enum \*/ DyeColor ([\w_]+) = new DyeColor\(', line)
			match = re.match(r'^\s+(\w+)\(\d+, "\w+", ', line)
			if match:
				dye_colors.append(match.group(1))
				continue

	return dye_colors
