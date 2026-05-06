#!/usr/bin/env bash

## Powermenu — Icons only, top center
## Requires: JetBrainsMono Nerd Font Mono

dir="$HOME/.config/rofi/powermenu"
theme='style'

uptime_str="$(uptime -p | sed 's/up //')"

# Icons only — Nerd Font glyphs
# 󰌾 Lock  󰒲 Suspend  󰍃 Logout  󰜉 Reboot  󰐥 Shutdown
lock='󰌾'
suspend='󰒲'
logout='󰍃'
reboot='󰜉'
shutdown='󰐥'

yes='󰄬'
no='󰅖'

rofi_cmd() {
    rofi -dmenu \
        -p "Uptime: $uptime_str" \
        -mesg "Uptime: $uptime_str" \
        -theme "${dir}/${theme}.rasi"
}

confirm_cmd() {
    rofi \
        -theme-str 'window {location: center; anchor: center; fullscreen: false; width: 350px;}' \
        -theme-str 'mainbox {children: [ "message", "listview" ];}' \
        -theme-str 'listview {columns: 2; lines: 1;}' \
        -theme-str 'element-text {horizontal-align: 0.5;}' \
        -theme-str 'textbox {horizontal-align: 0.5;}' \
        -dmenu \
        -p 'Confirmation' \
        -mesg 'Are you sure?' \
        -theme "${dir}/${theme}.rasi"
}

confirm_exit() {
    echo -e "$yes\n$no" | confirm_cmd
}

run_rofi() {
    echo -e "$lock\n$suspend\n$logout\n$reboot\n$shutdown" | rofi_cmd
}

run_cmd() {
    selected="$(confirm_exit)"
    if [[ "$selected" == "$yes" ]]; then
        case $1 in
            --shutdown) systemctl poweroff ;;
            --reboot)   systemctl reboot ;;
            --suspend)
                amixer set Master mute 2>/dev/null
                systemctl suspend
                ;;
            --logout)
                if [[ -n "$HYPRLAND_INSTANCE_SIGNATURE" ]]; then
                    hyprctl dispatch exit
                else
                    case "$DESKTOP_SESSION" in
                        bspwm)   bspc quit ;;
                        i3)      i3-msg exit ;;
                        openbox) openbox --exit ;;
                        plasma)  qdbus org.kde.ksmserver /KSMServer logout 0 0 0 ;;
                        sway)    swaymsg exit ;;
                        *)       loginctl terminate-session "$XDG_SESSION_ID" ;;
                    esac
                fi
                ;;
        esac
    fi
}

chosen="$(run_rofi)"
case "$chosen" in
    "$lock")
        if   command -v hyprlock         &>/dev/null; then hyprlock
        elif command -v swaylock         &>/dev/null; then swaylock
        elif command -v betterlockscreen &>/dev/null; then betterlockscreen -l
        elif command -v i3lock           &>/dev/null; then i3lock
        fi
        ;;
    "$suspend")  run_cmd --suspend  ;;
    "$logout")   run_cmd --logout   ;;
    "$reboot")   run_cmd --reboot   ;;
    "$shutdown") run_cmd --shutdown ;;
esac