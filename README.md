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

## When it isn't connecting

The dot in the header is the whole answer: lit means personas and settings
came from the Sheet, unlit means the page is on built-in sample data. Chat
needs only the token, so it keeps working either way — which is why a
disconnected page can still answer questions and log them to the Sheet while
nothing you edit reaches it. Everything below that dot follows from it:
background sync and persona write-back run only while it is lit, and an edit
made while it is unlit stays in the browser and says so in a banner.

Three things turn it off, in rough order of how often they do:

- **No token in this browser.** The endpoint is committed; the token never is.
  Every new browser, device, profile, or cleared-site-data is a fresh paste.
  Private windows and Safari's tracking prevention (which evicts local storage
  for sites left alone for a week) both throw it away silently.
- **The token is lost.** Because it is paste-once, blanking `APP_TOKEN` in
  `Code.gs` — as this repo's copy ships — leaves the only surviving copy in
  Apps Script's **Project Settings → Script Properties**. Read it there rather
  than inventing a new one; a new one has to be re-pasted on every device.
- **The deployment moved.** A brand-new deployment mints a new `/exec` URL
  while the old one keeps answering stale code. Paste the current URL from
  Deploy → Manage deployments.

A failed read is not final. The app retries on its own — 5s, 10s, 20s, 40s,
then every minute — and retries immediately when you return to the tab or the
device regains its network, so a cold start or a dropped connection heals
without a reload. It deliberately stops retrying for a rejected token or an
empty Personas tab, since neither improves with waiting; fix the cause and the
next paste in Settings › Chat starts it over.

To confirm the backend independently of the page, open the endpoint with your
token in any browser:

    https://script.google.com/macros/s/…/exec?action=ping&token=YOUR_APP_TOKEN

`{"ok":true,...}` means the deployment and token are good and the problem is in
the browser. `Bad or missing token.` means the deployment is fine but that
token is wrong.

## After any code change

Deploy → Manage deployments → ✏️ → Version: **New version** → Deploy. Editing
the script alone does not update the live `/exec` URL — and a brand-new
deployment mints a *new* URL, which you then paste into Settings → Chat once.

## Switching who answers, mid-conversation

A chat does not have to belong to one person. The bar above the message box
lists everyone in the current conversation and who is answering right now;
**+ Bring in** adds anyone from the chart, and one tap on a chip hands the
thread to them. Nothing is lost in the handover — the transcript stays whole,
each reply is marked with its author's icon and title, and the newcomer can be
put straight onto the question already on the table with **Ask them the same
question**.

Each persona answers from its own brief and sees its colleagues' replies
quoted and attributed, never as words of its own — so Legal can disagree with
Marketing in the same thread, and you can read which of them said what.

Picking someone from the chart or the outline still opens *their* own
conversation, exactly as before; only people already in the current
conversation stay in it when you click them.

## Voice accuracy

Settings → Voice accuracy reads ten test phrases aloud for you to repeat and
measures word error rate twice per pass — the speech engine's raw top guess vs.
after N-best selection and vocabulary fixes — writing each run back to the
Sheet's VoiceTests tab. Run it on the live page with a real microphone; that
measured figure is the acceptance number for the voice pipeline.
