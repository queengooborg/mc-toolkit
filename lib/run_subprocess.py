# -*- coding: utf-8 -*-

# 
# EssentialsX to BossShopPro - lib/run_subprocess
# © 2020-2023 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Run a subprocess and return the code returned by the process
#

def main(cmd, cwd, *args, **kwargs):
	r = subprocess.run(cmd, cwd=str(cwd), *args, **kwargs)
	return r.returncode