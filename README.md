# Persona Assistant (Work Assistants)

A single-file org-chart chat app (`index.html`, hosted on GitHub Pages) backed by a
Google Sheet through an Apps Script web app (`apps-script/Code.gs`). Every persona,
setting, and conversation log lives in the Sheet — the page holds no data of its own,
and the Sheet is the single source of truth the app syncs against in both directions.

## Set up the backend (about five minutes)

1. Open the Sheet → Extensions → Apps Script. Replace the contents of `Code.gs`
   with `apps-script/Code.gs` from this repository. Save.
2. To connect Anthropic access, paste your key **once** into
   `ANTHROPIC_API_KEY` at the top of the file — it is saved into Script
   Properties automatically and remembered from then on, so you never have
   to enter it in settings again (later code updates can leave the paste
   blank). Do the same with `APP_TOKEN`, a long random string you invent —
   it is the value the app sends as `?token=…` on every request. Keys already
   saved in Script Properties are kept; a new non-empty paste rotates them;
   never commit a filled-in constant.
3. In the editor, run `checkSetup` from the function dropdown, authorize when
   Google asks, and fix anything the log reports.
4. Deploy → New deployment → type **Web app**, Execute as **Me**, Who has
   access **Anyone**. Deploy, then copy the URL ending in `/exec`.

## Connect the app (one paste per browser)

Open the live page → Settings → Chat and paste the full URL with your token on
the end:

    https://script.google.com/macros/s/…/exec?token=YOUR_APP_TOKEN

The app splits it into the endpoint and the token and remembers both in that
browser — one paste per device is all it ever takes. (Pasting just the bare
token also works when the endpoint hasn't changed.) Once connected, personas,
settings, and conversation logs sync both ways automatically, on the cadence
the Sheet's `sync_interval_seconds` setting defines.

## After any code change

Deploy → Manage deployments → ✏️ → Version: **New version** → Deploy. Editing
the script alone does not update the live `/exec` URL — and a brand-new
deployment mints a *new* URL, which you then paste into Settings → Chat once.

## Voice accuracy

Settings → Voice accuracy reads ten test phrases aloud for you to repeat and
measures word error rate twice per pass — the speech engine's raw top guess vs.
after N-best selection and vocabulary fixes — writing each run back to the
Sheet's VoiceTests tab. Run it on the live page with a real microphone; that
measured figure is the acceptance number for the voice pipeline.
