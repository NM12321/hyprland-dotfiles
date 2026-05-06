#!/bin/bash
# =====================================================================
#  wallpaper.sh – Rofi wallpaper picker for swww
# =====================================================================

WALLPAPER_DIR=~/wallpapers
THEME=~/.config/rofi/wallpaper.rasi

# Pick wallpaper via rofi filebrowser
SELECTED=$(ls "$WALLPAPER_DIR" | grep -E '\.(png|jpg|jpeg|webp)$' | \
    rofi -dmenu \
         -i \
         -p "󰸉  Wallpaper" \
         -theme "$THEME")

# Exit if nothing selected
[ -z "$SELECTED" ] && exit

# Make sure swww daemon is running
swww query || swww init

# Set wallpaper with smooth transition
swww img "$WALLPAPER_DIR/$SELECTED" \
    --transition-type wipe \
    --transition-angle 30 \
    --transition-duration 1.2 \
    --transition-fps 60
