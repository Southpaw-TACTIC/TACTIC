#!/bin/bash

files=$(find . ! -name "._*" -a -name "*test.py")

while read -r line; do
	git add "$line"
done <<< "$files"
