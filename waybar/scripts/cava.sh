#!/bin/bash

bars=("▁" "▂" "▃" "▄" "▅" "▆" "▇" "█")

cava -p ~/.config/cava/waybar.conf | while read -r line; do
    output=""
    for n in $line; do
        output+="${bars[$n]}"
    done
    echo "$output"
done