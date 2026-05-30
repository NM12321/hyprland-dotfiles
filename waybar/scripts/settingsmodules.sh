#!/usr/bin/env bash

dir="$HOME/.config/rofi/controlcenter"
theme='controlcenter'

# Current volume
current_volume=$(pamixer --get-volume)

# Active connection
active_type=$(nmcli -t -f TYPE,STATE device \
    | grep ':connected' \
    | head -n1 \
    | cut -d: -f1)

if [ "$active_type" = "ethernet" ]; then
    network="🖧  Ethernet Connected"

elif [ "$active_type" = "wifi" ]; then
    wifi_info=$(nmcli -t -f active,ssid,signal dev wifi \
        | grep '^yes')

    wifi_name=$(echo "$wifi_info" | cut -d: -f2)
    wifi_signal=$(echo "$wifi_info" | cut -d: -f3)

    network="󰤨  ${wifi_name}  ${wifi_signal}%"

else
    network="󰤭  No Network"
fi

# Menu entries
bluetooth="󰂯  Bluetooth"
volume="󰕾  Volume  ${current_volume}%"
btop="󰄪  BTOP"
reload="󰑐  Reload Hyprland"

# Launch rofi
chosen=$(printf "%s\n%s\n%s\n%s\n%s" \
"$network" \
"$bluetooth" \
"$volume" \
"$btop" \
"$reload" | rofi -dmenu -i \
-theme "${dir}/${theme}.rasi")

# Actions
case "$chosen" in

    "$network")
        nm-connection-editor
        ;;

    "$bluetooth")
        blueman-manager
        ;;

    "$volume")

        action=$(printf "󰕾  Increase\n󰖀  Decrease" \
            | rofi -dmenu -i \
            -theme "${dir}/${theme}.rasi")

        case "$action" in
            "󰕾  Increase")
                pamixer -i 5
                ;;

            "󰖀  Decrease")
                pamixer -d 5
                ;;
        esac

        ~/.config/rofi/controlcenter/controlcenter.sh
        ;;

    "$btop")
        kitty -e btop
        ;;

    "$reload")
        hyprctl reload
        ;;

esac