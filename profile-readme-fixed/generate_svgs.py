#!/usr/bin/env python3
"""
Rebuilds dark_mode.svg / light_mode.svg keeping Sougata's original ASCII
art and field set, but with real `id` attributes wired up so today.py
can actually update them, and consistent column alignment.
"""

ART_LINES = [
    "           ...:.......            ",
    "           .::::::::...           ",
    "         .:::-:.:::::...          ",
    "        .::::::.:::::....         ",
    "        .:::::..::::::..          ",
    "        ::::::-----::.:.          ",
    "        .:::++*****++-.:..        ",
    "        .::=**###****+::..        ",
    "        .:-***####**++-...        ",
    "        .:=***####**++-..         ",
    "         .+**#%%####*+=.          ",
    "         .+===*###*=-==.          ",
    "         :+++=+**+--===.          ",
    "         =+====++-=+=++:          ",
    "         -*=+=+*+=+===+-          ",
    "         :##***#*+*++*+-          ",
    "         :#######*###*+.          ",
    "         :###***+*****=           ",
    "         .*#%#++=+##*+:           ",
    "         .=#*+---+##*=.           ",
    "          :+=-=+=--+=:.           ",
    "        ...-=***++-=-:..          ",
    "       .:-:::=+===-::::..         ",
    "     ..:--:-=-+++-::::::.         ",
    "    .:::--:=*=:::::::::::..       ",
    "   .::::--:*#*+-:::::::::::.      ",
    "  .:::::--:*##***=::::::::::..    ",
    "  .:::::-::-+***=:::::::::::::.   ",
    "  .::::--::::-:::::::::::::::::.  ",
    "  :::::--::---::::::::::::::::::  ",
    " .:::::::::----:::::::::::::::::. ",
    " .:::::::::---:::::::::::::::::::.",
    ".::::::::::---::::::::::::::::::::",
    ".:::::::-:::::::::::::::::::::::::",
]

STATIC_FIELDS = [
    ("OS", "Windows 11, Android 16"),
    ("Student", "2nd Year, CSE (AI & ML)"),
    ("Languages.Programming", "Java"),
    ("Languages.Real", "English, Bengali, Hindi"),
    ("Hobbies", "Listening to Music, Playing Games"),
    ("blank", None),
    ("section", "Contact"),
    ("Email", "work.sougatapaul@gmail.com"),
    ("LinkedIn", "sougata-paul"),
]

ART_LINE_H = 14
ART_X = 16
ART_Y0 = 24
STAT_X = 292
STAT_LINE_H = 14
STAT_Y0 = 24
TARGET_WIDTH = 30  # shared column width so every value lines up


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dots_for(label):
    return "." * max(2, TARGET_WIDTH - len(label))


def build_svg(theme):
    if theme == "dark":
        bg = "#0d1117"
        art_color = "#58a6ff"
        header_color = "#7ee787"
        label_color = "#ffa657"
        value_color = "#c9d1d9"
        add_color = "#3fb950"
        del_color = "#f85149"
    else:
        bg = "#ffffff"
        art_color = "#0969da"
        header_color = "#116329"
        label_color = "#bc4c00"
        value_color = "#24292f"
        add_color = "#1a7f37"
        del_color = "#cf222e"

    height = 516
    width = 675

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Consolas, \'Courier New\', monospace">'
    )
    parts.append(f'<rect width="100%" height="100%" fill="{bg}" rx="10"/>')

    y = ART_Y0
    for line in ART_LINES:
        parts.append(f'<text x="{ART_X}" y="{y}" font-size="13" fill="{art_color}" xml:space="preserve">{esc(line)}</text>')
        y += ART_LINE_H

    y = STAT_Y0
    parts.append(f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{header_color}" xml:space="preserve">sougata2006@github</text>')
    y += STAT_LINE_H
    parts.append(f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{header_color}" xml:space="preserve">------------------</text>')
    y += STAT_LINE_H
    y += STAT_LINE_H  # blank line

    for kind, val in STATIC_FIELDS:
        if kind == "blank":
            y += STAT_LINE_H
            continue
        if kind == "section":
            parts.append(f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{header_color}" xml:space="preserve">- {esc(val)} -</text>')
            y += STAT_LINE_H
            continue
        label = f"{kind}: "
        dots = dots_for(label)
        parts.append(
            f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{label_color}" xml:space="preserve">'
            f'{esc(label)}{dots} {esc(val)}</text>'
        )
        y += STAT_LINE_H

    y += STAT_LINE_H  # blank line
    parts.append(f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{header_color}" xml:space="preserve">- GitHub Stats -</text>')
    y += STAT_LINE_H

    # Repos | Stars
    parts.append(
        f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{label_color}" xml:space="preserve">'
        f'Repos: <tspan id="repo_data_dots">.... </tspan><tspan id="repo_data" fill="{value_color}">0</tspan>'
        f'  |  Stars: <tspan id="star_data_dots">.... </tspan><tspan id="star_data" fill="{value_color}">0</tspan>'
        f'</text>'
    )
    y += STAT_LINE_H

    # Commits | Followers | Following
    parts.append(
        f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{label_color}" xml:space="preserve">'
        f'Commits: <tspan id="commit_data_dots">.... </tspan><tspan id="commit_data" fill="{value_color}">0</tspan>'
        f'  |  Followers: <tspan id="follower_data_dots">.... </tspan><tspan id="follower_data" fill="{value_color}">0</tspan>'
        f'  |  Following: <tspan id="following_data_dots">.... </tspan><tspan id="following_data" fill="{value_color}">0</tspan>'
        f'</text>'
    )
    y += STAT_LINE_H

    # Uptime (account age)
    parts.append(
        f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{label_color}" xml:space="preserve">'
        f'Uptime: <tspan id="age_data_dots">.......... </tspan><tspan id="age_data" fill="{value_color}">0 days</tspan>'
        f'</text>'
    )
    y += STAT_LINE_H

    # Lines of Code
    parts.append(
        f'<text x="{STAT_X}" y="{y}" font-size="13" fill="{label_color}" xml:space="preserve">'
        f'Lines of Code: <tspan id="loc_data_dots">.......... </tspan><tspan id="loc_data" fill="{value_color}">0</tspan>'
        f' (<tspan id="loc_add" fill="{add_color}">0</tspan><tspan fill="{add_color}">++</tspan>, '
        f'<tspan id="loc_del" fill="{del_color}">0</tspan><tspan fill="{del_color}">--</tspan>)'
        f'</text>'
    )
    y += STAT_LINE_H

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    with open("dark_mode.svg", "w") as f:
        f.write(build_svg("dark"))
    with open("light_mode.svg", "w") as f:
        f.write(build_svg("light"))
    print("done")
