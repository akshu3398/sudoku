#!/bin/sh

for dir in *; do
    if [ -d "$dir" ]; then
        find "$dir" -type f > "$dir.index"
    fi
done
find */ -type f >Any.index
for i in *index; do echo -n $i; wc "$i"; done
