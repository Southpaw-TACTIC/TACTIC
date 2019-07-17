#!/bin/bash

files=$(find . ! -name "._*" -a -name "*test.py")

while read -r line; do
	python "$line"
done <<< "$files"
