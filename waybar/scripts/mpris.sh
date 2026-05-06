#!/bin/bash
STATUS=$(playerctl status 2>/dev/null)
if [ -z "$STATUS" ] || [ "$STATUS" = "No players found" ]; then
    echo "󰝛  Nothing playing"
elif [ "$STATUS" = "Paused" ]; then
    echo "⏸ $(playerctl metadata title) ($(playerctl metadata artist))"
else
    echo "▶ $(playerctl metadata title) ($(playerctl metadata artist))"
fi
