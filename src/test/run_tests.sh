#!/bin/bash

files=$(find . ! -name "._*" -a -name "*test.py")

while read -r line; do
	echo "--------------- running: $line --------------------"
    python "$line"
done <<< "$files"
