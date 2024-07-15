# -*- coding: utf-8 -*-

# 
# mc-toolkit - lib/version
# © 2020-2024 Vinyl Da.i'gyu-Kazotetsu [https://www.queengoob.org].
# This code is licensed under the GNU GPLv3 license (https://choosealicense.com/licenses/gpl-3.0/).
#
# Simple class for handling semantic versioning strings
#

class Version:
	def __init__(self, string):
		parts = string.split(".")
		self.major = int(parts[0])
		self.minor = int(parts[1]) if len(parts) > 1 else 0
		self.patch = int(parts[2]) if len(parts) > 2 else 0

	def __str__(self):
		return f"{self.major}.{self.minor}.{self.patch}"

	def __eq__(self, other):
		return self.major == other.major and \
					 self.minor == other.minor and \
					 self.patch == other.patch

	def __ne__(self, other):
		return not self.__eq__(other)

	def __lt__(self, other):
		if self.major < other.major:
			return True
		if self.major == other.major:
			if self.minor < other.minor:
				return True
			if self.minor == other.minor:
				return self.patch < other.patch

	def __le__(self, other):
		return self.__lt__(other) or self.__eq__(other)

	def __gt__(self, other):
		if self.major > other.major:
			return True
		if self.major == other.major:
			if self.minor > other.minor:
				return True
			if self.minor == other.minor:
				return self.patch > other.patch

	def __ge__(self, other):
		return self.__gt__(other) or self.__eq__(other)

	def __add__(self, other):
		if type(other) == str:
			return self.__str__() + other

		raise TypeError(f"unsupported operand type(s) for +: 'Version' and '{type(other)}'")
