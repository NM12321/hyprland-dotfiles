#!/bin/bash

if pgrep -x yad >/dev/null; then
    pkill yad
    exit
fi

yad \
    --calendar \
    --undecorated \
    --fixed \
    --close-on-unfocus \
    --no-buttons \
    --width=340 \
    --height=320 \
    --title="Calendar" \
    --borders=12 \
    --posx="$(hyprctl cursorpos -j | jq '.x' | cut -d. -f1)" \
    --posy=45