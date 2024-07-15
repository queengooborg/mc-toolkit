# -*- coding: utf-8 -*-

# 
# mc-toolkit - lib/prepare_source
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Prepare the deobfuscated source code for a specified Minecraft version, using DecompilerMC
#

import os
from pathlib import Path

from .run_subprocess import main as run_subprocess
from .version import Version

def main(mc_version, silent=False):
	decompiler_path = Path(os.path.dirname(__file__)) / "../DecompilerMC"
	source_path = decompiler_path / f"src/{mc_version}/client/net/minecraft"

	if mc_version <= Version("1.14.3"):
		raise Exception("DecompilerMC cannot decompile Minecraft 1.14.3 or lower, as no source mappings are provided")

	if not source_path.exists():
		if not silent:
			print("Decompiled sources not found, performing decompilation now...  This may take a while, please be patient!\n")

		if run_subprocess(["python3", "main.py", f"--mcversion={mc_version}", "--quiet"], decompiler_path) != 0:
			raise Exception("Failed to decompile sources, please try again")

		if not silent:
			print("\nDecompilation complete!")

	# Just in case the source path still doesn't exist after running decompiler
	if not source_path.exists():
		raise Exception("Source path does not exist, there may have been a problem preparing the sources")

	return source_path
