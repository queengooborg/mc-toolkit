# -*- coding: utf-8 -*-

# 
# mc-toolkit - lib/prepare_source
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Prepare the deobfuscated source code for a specified Minecraft version, using DecompilerMC
#

import os
import sys
from pathlib import Path

from .version import Version

sys.path.insert(0, Path(__file__).parent.parent)

from DecompilerMC.main import run as do_decompile

def main(mc_version, silent=False):
	decompiler_path = Path(os.path.dirname(__file__)) / ".." / "DecompilerMC"
	source_path = decompiler_path / "src" / str(mc_version) / "client" / "net" / "minecraft"

	if mc_version <= Version("1.14.3"):
		raise Exception("DecompilerMC cannot decompile Minecraft 1.14.3 or lower, as no source mappings are provided")

	if not source_path.exists():
		if not silent:
			print("Decompiled sources not found, performing decompilation now...  This may take a while, please be patient!\n")

		do_decompile(str(mc_version), "client", quiet=silent, clean=True)

		if not silent:
			print("\nDecompilation complete!")

	# Just in case the source path still doesn't exist after running decompiler
	if not source_path.exists():
		raise Exception("Source path does not exist, there may have been a problem preparing the sources")

	return source_path
