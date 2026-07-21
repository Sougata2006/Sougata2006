# Setup

1. Copy `today.py`, `requirements.txt`, `.github/workflows/update-readme.yml`,
   and `README.md` into your `Sougata2006/Sougata2006` repo (overwrite what's there).

2. Create a Personal Access Token so the Action is allowed to push:
   - GitHub → Settings → Developer settings → Personal access tokens →
     Tokens (classic) → Generate new token.
   - Scopes: `repo` and `read:user`.
   - Copy the token.

3. Add it as a repo secret:
   - Your repo → Settings → Secrets and variables → Actions → New repository secret.
   - Name: `ACCESS_TOKEN`, value: the token you copied.

4. Go to the Actions tab, open "Update profile card", click "Run workflow" once
   to generate `dark_mode.svg` / `light_mode.svg` for the first time.

5. After that it re-runs automatically every 6 hours and on every push, so the
   Repos / Stars / Commits / Followers / Uptime numbers stay current without
   you touching anything.

## Customizing

- Edit `STATIC_FIELDS` and `CONTACT_FIELDS` near the top of `today.py` to
  change the fields shown (OS, student status, languages, hobbies, contact info).
- Set `CALC_LOC = False` in `today.py` if you want faster runs and don't care
  about the "Lines of Code" stat (it's the slowest part since it walks commit
  history per repo).
- Change the cron schedule in `update-readme.yml` if you want a different
  refresh interval.
