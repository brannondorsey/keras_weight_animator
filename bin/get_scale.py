#!/usr/bin/env python

import sys

if len(sys.argv) != 4:
	print('usage: python get_resized.py orig_dim max_width max_height')
	exit(1)

width, height = map(lambda x: int(x), sys.argv[1].split('x'))
max_width  = int(sys.argv[2])
max_height = int(sys.argv[3])

# landscape
if width > height:
	new_height = int((height * max_width) / width)
	# uncomment to print new dimensions
	# print('{}x{}'.format(max_width, new_height))
	
	# print the scale increase
	print('{}%'.format(int(max_width / width) * 100))
# portrait
else:
	new_width = int((width * max_height) / height)
	# uncomment to print new dimensions
	# print('{}x{}'.format(new_width, max_height))

	# print the scale increase
	print('{}%'.format(int(max_height / height) * 100))

	