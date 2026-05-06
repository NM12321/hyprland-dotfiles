#!/bin/bash
if pidof gsimplecal > /dev/null; then
    pkill gsimplecal
else
    gsimplecal
fi
