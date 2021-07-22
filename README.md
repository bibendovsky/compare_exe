Overview
========

Compares executable files for equality.  
Useful for merging projects into the one on preprocessor level.


Usage
=====

`compare_exe.py <script.json>`


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
