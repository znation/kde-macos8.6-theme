"""The classic Platinum-era 16-color system table for terminal themes.

No reference screenshot shows a terminal, so this table is the contract for
the Ghostty palette and the Konsole colorscheme slots 0 to 15. Slots 12 and 14
repeat 4 and 6 because the table has no bright blue or bright cyan.
"""

# Classic Platinum-era 16-color system table, ANSI slot -> color. Slots 12 and
# 14 repeat 4 and 6 because the table has no bright blue or bright cyan. Written
# here as the contract; the file must match it exactly.
PALETTE = {
    0: "#000000",
    1: "#dd0806",
    2: "#006411",
    3: "#562c05",
    4: "#0000d4",
    5: "#4600a5",
    6: "#02abea",
    7: "#c0c0c0",
    8: "#808080",
    9: "#ff6403",
    10: "#1fb714",
    11: "#fcf305",
    12: "#0000d4",
    13: "#f20884",
    14: "#02abea",
    15: "#ffffff",
}
