"""

Overview
========

Compares executable files for equality.
Useful for merging projects into the one on preprocessor level.


Usage
=====

compare_exe.py <script.json>


Notes
=====

Atomatically added exclusions:
    - PE COFF timestamp


Sample script
=============

```
{
	"dir_1" : "1",
	"dir_2" : "2",
	"files" :
	[
		{
			"name" : "1.txt",
			"exclusions" :
			[
				{"offset" : 1, "size" : 2},
				{"offset" : 3, "size" : 4}
			]
		},

		{
			"name" : "2.txt",
			"exclusions" :
			[
				{"offset" : 0, "size" : 6},
				{"offset" : 15, "size" : 6}
			]
		}
	]
}
```

Disclaimer
==========

Copyright (c) 2021 Boris I. Bendovsky (<bibendovsky@hotmail.com>)

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

For a copy of the GNU General Public License see file LICENSE.
For an original source code license see file "Blake Stone source code license.doc".


"""

# ---------------------------------------------------------------------------

import json
import os
import sys

# ---------------------------------------------------------------------------

if len(sys.argv) != 2:
	print("Usage: app.py <script.json>")
	sys.exit()

# ---------------------------------------------------------------------------

__offset_name = "offset"
__size_name = "size"
__name_name = "name"

# ---------------------------------------------------------------------------

def to_int(value):
	if isinstance(value, str):
		return int(value, 0)
	elif isinstance(value, int):
		return value
	else:
		raise Exception("Expected \"int\" or \"str\".")

# ---------------------------------------------------------------------------

class CompareContext:
	def __init__(self):
		self.paths = []
		self.size = 0
		self.exclusions = []
		self.datas = []

# ---------------------------------------------------------------------------

def validate_exclusions(compare_context):
	exclusions = compare_context.exclusions

	if len(exclusions) == 0:
		return

	exclusions.sort(key = lambda exclusion: to_int(exclusion[__offset_name]))

	prev_offset = None
	prev_size = None

	for exclusion in exclusions:
		offset = to_int(exclusion[__offset_name])

		if offset < 0:
			raise Exception("Negative offset.")

		size = to_int(exclusion[__size_name])

		if size <= 0:
			raise Exception("Negative or zero size.")

		if (offset + size) > compare_context.size:
			raise Exception("Exclusion range out of file bounds.")

		if prev_offset is not None and prev_size is not None:
			if offset == prev_offset:
				raise Exception("Duplicate offset.")

			if offset > prev_offset and offset < (prev_offset + prev_size):
				raise Exception("Exclusions overlap.")

		prev_offset = offset
		prev_size = size

# ---------------------------------------------------------------------------

def load_file(path, size):
	with open(path, "rb") as file:
		return file.read(size)

# ---------------------------------------------------------------------------

def find_exe_exclusions(data):
	view = memoryview(data)
	data_size = len(view)


	# Get COFF timestamp
	#

	pe_offset_offset = 0x3C

	if (pe_offset_offset + 4) >= data_size:
		return list()

	pe_offset_offset_view = view[pe_offset_offset:pe_offset_offset + 4]
	pe_offset = int.from_bytes(pe_offset_offset_view, "little")

	coff_size = 20
	coff_offset = pe_offset + 4

	coff_opt_header_offset = coff_offset + coff_size

	if coff_opt_header_offset >= data_size:
		return list()

	pe_ref_signature = bytearray(b"\x50\x45\x00\x00")
	pe_signature = view[pe_offset:coff_offset]

	if pe_signature != pe_ref_signature:
		return list()

	coff_timestamp_offset = coff_offset + 4

	return [{__offset_name : coff_timestamp_offset, __size_name : 4}]

# ---------------------------------------------------------------------------

def compare_files(compare_context):
	if compare_context.paths[0] == compare_context.paths[1]:
		raise Exception("Same paths.")

	size_1 = os.path.getsize(compare_context.paths[0])
	size_2 = os.path.getsize(compare_context.paths[1])

	if size_1 != size_2:
		raise Exception("Size mismatch.")

	compare_context.size = size_1

	for path in compare_context.paths:
		data = load_file(path, compare_context.size)
		compare_context.datas.append(data)

	exe_exclusions = find_exe_exclusions(compare_context.datas[0])
	compare_context.exclusions = exe_exclusions + compare_context.exclusions
	validate_exclusions(compare_context)

	eof = False
	offset = 0
	exclusion_it = iter(compare_context.exclusions)

	while True:
		end_offset = offset

		try:
			exclusion = next(exclusion_it)
			end_offset = to_int(exclusion[__offset_name])
		except StopIteration:
			eof = True
			end_offset = compare_context.size

		data_1 = compare_context.datas[0]
		view_1 = memoryview(data_1)
		slice_1 = view_1[offset:end_offset]

		data_2 = compare_context.datas[1]
		view_2 = memoryview(data_2)
		slice_2 = view_2[offset:end_offset]

		slice_size = len(slice_1)

		for i in range(slice_size):
			if slice_1[i] != slice_2[i]:
				mismatch_offset = offset + i
				raise Exception("Data block mismatch at {} ({}).".format(hex(mismatch_offset), mismatch_offset))

		if eof:
			break;

		offset = to_int(exclusion[__offset_name]) + to_int(exclusion[__size_name])

# ---------------------------------------------------------------------------

def load_script(file_name):
	with open(file_name) as script_file:
		return json.load(script_file)

# ---------------------------------------------------------------------------

def main():
	script = load_script(sys.argv[1])

	dir_1 = os.path.normpath(script["dir_1"])
	print("Dir 1: \"{}\"".format(dir_1))

	dir_2 = os.path.normpath(script["dir_2"])
	print("Dir 2: \"{}\"".format(dir_2))

	print()

	files = script["files"]

	if len(files) == 0:
		raise Exception("Empty file list.")

	if len(files) != len(set([i[__name_name] for i in files])):
		raise Exception("Duplicate file name.")

	for file in files:
		file_name = file[__name_name]
		print("File: \"{}\"".format(file_name))

		path_1 = os.path.realpath(os.path.join(dir_1, file_name))
		path_2 = os.path.realpath(os.path.join(dir_2, file_name))

		compare_context = CompareContext()
		compare_context.paths.append(path_1)
		compare_context.paths.append(path_2)
		compare_context.exclusions = file.get("exclusions", [])

		compare_files(compare_context)

	print()
	print("Succeeded.")

# ---------------------------------------------------------------------------

main()
