#!/usr/bin/env bash

PLAYERCTL="playerctl --player=spotify,chromium"

STATUS=$($PLAYERCTL status 2>/dev/null)

if [[ -z "$STATUS" || "$STATUS" == "No players found" ]]; then
    echo '{"text": "", "class": "stopped"}'
    exit 0
fi

TITLE=$($PLAYERCTL metadata xesam:title 2>/dev/null | cut -c1-35)
ARTIST=$($PLAYERCTL metadata xesam:artist 2>/dev/null | cut -c1-20)
POSITION=$($PLAYERCTL position 2>/dev/null)
LENGTH=$($PLAYERCTL metadata mpris:length 2>/dev/null)

if [[ -z "$TITLE" ]]; then
    echo '{"text": "", "class": "disconnected"}'
    exit 0
fi

# Progress bar (10 blocks wide)
if [[ -n "$POSITION" && -n "$LENGTH" && "$LENGTH" -gt 0 ]]; then
    POS_US=$(echo "$POSITION * 1000000" | bc | cut -d. -f1)
    PCT=$(( POS_US * 10 / LENGTH ))
    [[ $PCT -gt 10 ]] && PCT=10
    FILLED=$(printf '━%.0s' $(seq 1 $PCT) 2>/dev/null)
    EMPTY=$(printf '─%.0s' $(seq 1 $((10 - PCT))) 2>/dev/null)
    BAR="${FILLED}${EMPTY}"
fi

if [[ "$STATUS" == "Playing" ]]; then
    ICON="" ; CLASS="playing"
else
    ICON="" ; CLASS="paused"
fi

if [[ -n "$ARTIST" ]]; then
    LABEL="${ICON}  ${TITLE} — ${ARTIST}  ${BAR}"
else
    LABEL="${ICON}  ${TITLE}  ${BAR}"
fi

echo "{\"text\": \"$LABEL\", \"class\": \"$CLASS\"}"