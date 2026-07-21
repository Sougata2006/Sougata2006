#!/usr/bin/env python3
"""
today.py
--------
Fetches live GitHub stats for a user and renders a neofetch-style
profile card as two SVGs (light_mode.svg / dark_mode.svg).

Run in GitHub Actions on a schedule + on push. Needs a token with
`read:user` scope stored as the ACCESS_TOKEN secret.
"""

import base64
import datetime
import io
import os
import sys
import time
import urllib.request

import requests

# --------------------------------------------------------------------------
# CONFIG - edit this block for your own info. Everything under
# "GitHub Stats" below is fetched live, you don't touch that part.
# --------------------------------------------------------------------------
USERNAME = os.environ.get("GH_USERNAME", "Sougata2006")

STATIC_FIELDS = [
    ("OS", "Windows 11, Android 16"),
    ("Student", "2nd Year, CSE (AI & ML)"),
    ("Languages.Programming", "Java"),
    ("Languages.Real", "English, Bengali, Hindi"),
    ("Hobbies", "Listening to Music, Playing Games"),
]

CONTACT_FIELDS = [
    ("Email", "work.sougatapaul@gmail.com"),
    ("LinkedIn", "sougata-paul"),
]

# Exclude forks from stars / LOC calculations
EXCLUDE_FORKS = True
# Set to False the first time if you want a quick run without the (slower)
# lines-of-code calculation.
CALC_LOC = True

# --------------------------------------------------------------------------
TOKEN = os.environ.get("ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
HEADERS_REST = {"Authorization": f"token {TOKEN}"} if TOKEN else {}
HEADERS_GQL = (
    {"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"}
    if TOKEN
    else {"Content-Type": "application/json"}
)

REST_ROOT = "https://api.github.com"
GQL_URL = "https://api.github.com/graphql"


def rest_get(path, params=None):
    r = requests.get(f"{REST_ROOT}{path}", headers=HEADERS_REST, params=params)
    r.raise_for_status()
    return r.json()


def rest_get_paginated(path, params=None):
    params = dict(params or {})
    params["per_page"] = 100
    page = 1
    out = []
    while True:
        params["page"] = page
        r = requests.get(f"{REST_ROOT}{path}", headers=HEADERS_REST, params=params)
        r.raise_for_status()
        chunk = r.json()
        if not chunk:
            break
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


def gql(query, variables=None):
    r = requests.post(
        GQL_URL, headers=HEADERS_GQL, json={"query": query, "variables": variables or {}}
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


# --------------------------------------------------------------------------
# Stats gathering
# --------------------------------------------------------------------------
def get_user():
    return rest_get(f"/users/{USERNAME}")


def get_owned_repos():
    repos = rest_get_paginated(f"/users/{USERNAME}/repos", {"type": "owner"})
    if EXCLUDE_FORKS:
        repos = [r for r in repos if not r.get("fork")]
    return repos


def total_stars(repos):
    return sum(r.get("stargazers_count", 0) for r in repos)


def total_followers(user):
    return user.get("followers", 0)


def total_following(user):
    return user.get("following", 0)


def account_age(user):
    created = datetime.datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    delta = datetime.datetime.utcnow() - created
    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = (delta.days % 365) % 30
    return f"{years} years, {months} months, {days} days"


def total_commits(user):
    """Sum contributionsCollection.totalCommitContributions year by year
    since the GraphQL API only allows a 1 year window per call."""
    created = datetime.datetime.strptime(user["created_at"], "%Y-%m-%dT%H:%M:%SZ")
    start_year = created.year
    this_year = datetime.datetime.utcnow().year
    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          totalCommitContributions
          restrictedContributionsCount
        }
      }
    }
    """
    commits = 0
    for year in range(start_year, this_year + 1):
        frm = f"{year}-01-01T00:00:00Z"
        to = f"{year}-12-31T23:59:59Z"
        data = gql(query, {"login": USERNAME, "from": frm, "to": to})
        cc = data["user"]["contributionsCollection"]
        commits += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
    return commits


def lines_of_code(repos):
    """Sum additions/deletions authored by USERNAME across owned repos,
    using the commit history's additions/deletions fields."""
    if not CALC_LOC:
        return None, None
    query = """
    query($owner: String!, $name: String!, $cursor: String) {
      repository(owner: $owner, name: $name) {
        defaultBranchRef {
          target {
            ... on Commit {
              history(first: 100, after: $cursor, author: {id: $authorId}) {
                pageInfo { hasNextPage endCursor }
                nodes { additions deletions }
              }
            }
          }
        }
      }
    }
    """
    # get the user's node id once, needed to filter commit authorship
    user_data = gql(
        "query($login:String!){user(login:$login){id}}", {"login": USERNAME}
    )
    author_id = user_data["user"]["id"]

    additions = deletions = 0
    for repo in repos:
        name = repo["name"]
        cursor = None
        while True:
            try:
                data = gql(
                    query.replace("$authorId", "$authorId"),
                    {"owner": USERNAME, "name": name, "cursor": cursor},
                )
            except Exception:
                break
            ref = data["repository"]["defaultBranchRef"]
            if not ref or not ref.get("target"):
                break
            history = ref["target"]["history"]
            for node in history["nodes"]:
                additions += node["additions"]
                deletions += node["deletions"]
            if not history["pageInfo"]["hasNextPage"]:
                break
            cursor = history["pageInfo"]["endCursor"]
            time.sleep(0.2)
    return additions, deletions


# --------------------------------------------------------------------------
# ASCII art from the avatar
# --------------------------------------------------------------------------
RAMP = "@%#*+=-:. "  # dark -> light


def avatar_ascii(avatar_url, cols=34, rows=34):
    try:
        from PIL import Image
    except ImportError:
        return []
    req = urllib.request.Request(avatar_url, headers={"User-Agent": "readme-bot"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        img = Image.open(io.BytesIO(resp.read())).convert("L")
    img = img.resize((cols, rows))
    px = img.load()
    lines = []
    for y in range(rows):
        line = []
        for x in range(cols):
            brightness = px[x, y] / 255
            idx = min(len(RAMP) - 1, int((1 - brightness) * (len(RAMP) - 1)))
            line.append(RAMP[idx])
        lines.append("".join(line))
    return lines


# --------------------------------------------------------------------------
# SVG rendering
# --------------------------------------------------------------------------
def esc(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def dotted_line(label, value, width=46):
    dots = "." * max(1, width - len(label) - len(str(value)) - 2)
    return f"{label}: {dots} {value}"


def build_stat_lines(stats):
    lines = [f"{USERNAME}@github", "-" * (len(USERNAME) + 7), ""]
    for label, value in STATIC_FIELDS:
        lines.append(dotted_line(label, value))
    lines.append("")
    lines.append("- Contact -")
    for label, value in CONTACT_FIELDS:
        lines.append(dotted_line(label, value))
    lines.append("")
    lines.append("- GitHub Stats -")
    lines.append(dotted_line("Repos", stats["repos"]))
    lines.append(dotted_line("Stars", stats["stars"]))
    lines.append(dotted_line("Commits", stats["commits"]))
    lines.append(dotted_line("Followers", stats["followers"]))
    lines.append(dotted_line("Following", stats["following"]))
    lines.append(dotted_line("Uptime", stats["uptime"]))
    if stats.get("additions") is not None:
        lines.append(
            dotted_line(
                "Lines of Code",
                f"{stats['additions']:,}++, {stats['deletions']:,}--",
            )
        )
    return lines


THEMES = {
    "dark_mode.svg": {
        "bg": "#0d1117",
        "text": "#c9d1d9",
        "accent": "#58a6ff",
        "label": "#ffa657",
        "header": "#7ee787",
    },
    "light_mode.svg": {
        "bg": "#ffffff",
        "text": "#24292f",
        "accent": "#0969da",
        "label": "#bc4c00",
        "header": "#116329",
    },
}


def render_svg(ascii_lines, stat_lines, theme):
    line_h = 14
    font_size = 13
    left_w = 34 * 8 + 20
    right_w = max(len(l) for l in stat_lines) * 7.3 + 40
    width = int(left_w + right_w)
    height = int(max(len(ascii_lines), len(stat_lines)) * line_h + 40)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Consolas, \'Courier New\', monospace">',
        f'<rect width="100%" height="100%" fill="{theme["bg"]}" rx="10"/>',
    ]

    y = 24
    for line in ascii_lines:
        svg.append(
            f'<text x="16" y="{y}" font-size="{font_size}" fill="{theme["accent"]}" '
            f'xml:space="preserve">{esc(line)}</text>'
        )
        y += line_h

    y = 24
    x = int(left_w)
    for line in stat_lines:
        color = theme["text"]
        if line.endswith("@github"):
            color = theme["header"]
        elif line.startswith("- ") or line.startswith("-" * 3):
            color = theme["header"]
        elif ":" in line:
            color = theme["label"]
        svg.append(
            f'<text x="{x}" y="{y}" font-size="{font_size}" fill="{color}" '
            f'xml:space="preserve">{esc(line)}</text>'
        )
        y += line_h

    svg.append("</svg>")
    return "\n".join(svg)


# --------------------------------------------------------------------------
def main():
    user = get_user()
    repos = get_owned_repos()

    additions = deletions = None
    if CALC_LOC:
        try:
            additions, deletions = lines_of_code(repos)
        except Exception as e:
            print(f"LOC calculation skipped: {e}", file=sys.stderr)

    try:
        commits = total_commits(user)
    except Exception as e:
        print(f"Commit calculation failed, falling back to 0: {e}", file=sys.stderr)
        commits = 0

    stats = {
        "repos": len(repos),
        "stars": total_stars(repos),
        "followers": total_followers(user),
        "following": total_following(user),
        "commits": commits,
        "uptime": account_age(user),
        "additions": additions,
        "deletions": deletions,
    }

    ascii_lines = avatar_ascii(user["avatar_url"])
    stat_lines = build_stat_lines(stats)

    for filename, theme in THEMES.items():
        svg = render_svg(ascii_lines, stat_lines, theme)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"wrote {filename}")


if __name__ == "__main__":
    main()
