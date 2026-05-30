#!/usr/bin/env python3

import calendar
from datetime import datetime

now = datetime.now()

year = now.year
month = now.month

cal = calendar.TextCalendar(calendar.SUNDAY)

header = f"{calendar.month_name[month]} {year}\n"

print(header)
print(cal.formatmonth(year, month))
print("\n──────────────")
print(calendar.month(year, month - 1 if month > 1 else 12))
print("\n──────────────")
print(calendar.month(year, month + 1 if month < 12 else 1))