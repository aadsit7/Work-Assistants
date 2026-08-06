# Persona Assistant (Work Assistants)

A single-file org-chart chat app (`index.html`, hosted on GitHub Pages) backed by a
Google Sheet through an Apps Script web app (`apps-script/Code.gs`). Every persona,
setting, and conversation lives in the Sheet — the page holds no data of its own,
and the Sheet is the single source of truth the app syncs against in both directions.

That includes your chat history. The side menu lists every conversation you have
ever had, because `Interactions` is the list of them and `Messages` is their
contents; there is no separate history store and nothing to export. Reload the
page, open it on a different device, clear the browser — the list is the same.

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
   Google asks, and fix anything the log reports. It also names any of the
   three history columns below that your Sheet is missing.
4. Deploy → New deployment → type **Web app**, Execute as **Me**, Who has
   access **Anyone**. Deploy, then copy the URL ending in `/exec`.

### Three columns conversation history uses

Add these to an existing Sheet — put the header in the first empty column of the
tab, which appends it without moving anything. A Sheet without them still works;
each one just costs the thing next to it, and `checkSetup` says which are absent.

| Tab | Column | Without it |
| --- | --- | --- |
| `Interactions` | `Title` | Conversations are named after their opening question and can't be renamed |
| `Interactions` | `ParticipantIds` | A reopened conversation rebuilds its cast from who answered in it, rather than from the order people joined |
| `Messages` | `ContextShown` | The colleague context a persona was shown in a handed-over conversation isn't kept |

`Messages.Content` holds what you typed. When a conversation has changed hands,
the colleague answers that persona was *additionally* shown go in `ContextShown`,
so the tab reads as the conversation it is and still answers "what did this
persona actually see?"

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

Your past conversations are on the lit side of that line, since reading them
means reading the Sheet. An unlit page lists only what this browser has said in
this session, and the line under the list says so rather than presenting a short
history as the whole of it. New conversations are still logged either way, so
nothing said while it was unlit is lost — it appears in the list once the read
succeeds.

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

## The side menu

The left column is the app's spine, and it holds two things behind one switch.

**Chats** is your history, newest first, grouped Today / Yesterday / Previous 7
days / Previous 30 days / by month. Each row shows the cast that spoke in that
conversation as stacked marks, its name, and how long it ran — so a conversation
that changed hands is recognisable before you open it. Hovering a row reveals
rename and delete; delete asks once, marks the row deleted in the Sheet, and
never removes a logged message. **+ New chat** starts a fresh conversation with
whoever is on screen, and pressing it twice does not leave a trail of empty ones.

One person can now hold as many conversations as you like. Clicking someone in
**Team** returns you to the one you were already having with them and starts one
when there isn't one; a conversation from three weeks ago is only ever reopened
deliberately, from the list.

Search covers everything, in two passes that show no seam. Titles and any
transcript already in memory match as you type; the full text of every other
message is matched by the server against the `Messages` tab a moment later, and
the two sets are merged. That is what lets a question asked last month on another
laptop come back from three words. The line under the list always says which of
the two it is showing — the whole Sheet, or only what this browser holds.

On a phone the same menu is a drawer: the button left of the gear slides it in
over the conversation, and picking anything closes it. On a desktop that button
hides and shows the column instead.

## Switching who answers, mid-conversation

A chat does not have to belong to one person. The bar above the message box
lists everyone in the current conversation and who is answering right now;
**+ Bring in** adds anyone from the chart, and one tap on a chip hands the
thread to them. Nothing is lost in the handover — the transcript stays whole,
each reply is marked with its author's icon and title, and the newcomer can be
put straight onto the question already on the table with **Ask them the same
question**.

You can hand it back as easily as you handed it over: tap the chip of anyone
already in the conversation and they answer the next question. Ask the CEO, take
it to Legal, come back to the CEO — one transcript, three turns, each answered
from that persona's own brief.

Each persona answers from its own brief and sees its colleagues' replies
quoted and attributed, never as words of its own — so Legal can disagree with
Marketing in the same thread, and you can read which of them said what.

None of this depends on the conversation being new. A conversation reopened from
the side menu comes back with its cast intact, because every message in the Sheet
names the persona that wrote it — so a chat from last week can still be passed
around today, and the whole exchange stays on the one row it started on.

Picking someone from the chart or the outline still opens the conversation you
were having with *them*; only people already in the current conversation stay in
it when you click them.

## Voice accuracy

Settings → Voice accuracy reads ten test phrases aloud for you to repeat and
measures word error rate twice per pass — the speech engine's raw top guess vs.
after N-best selection and vocabulary fixes — writing each run back to the
Sheet's VoiceTests tab. Run it on the live page with a real microphone; that
measured figure is the acceptance number for the voice pipeline.
