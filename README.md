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

### Five columns the Sheet can grow into

Add these to an existing Sheet — put the header in the first empty column of the
tab, which appends it without moving anything. A Sheet without them still works;
each one just costs the thing next to it, and `checkSetup` says which are absent.

| Tab | Column | Without it |
| --- | --- | --- |
| `Interactions` | `Title` | Conversations are named after their opening question and can't be renamed |
| `Interactions` | `ParticipantIds` | A reopened conversation rebuilds its cast from who answered in it, rather than from the order people joined |
| `Messages` | `ContextShown` | The colleague context a persona was shown in a handed-over conversation isn't kept |
| `KnowledgeSources` | `SourceUrl` | A source added as a website URL keeps its label but loses its link |
| `KnowledgeSources` | `Content` | A source added as pasted text keeps its label but loses the text |

The last two are the only ones the app will tell you about while you use it: a
save that had to drop a link or a body says so in a banner, naming the column
to add, rather than reporting a clean save over a partial one.

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

## What an answer looks like

Every persona is briefed to answer in three sections, and the page renders them
as three sections rather than as the markdown they arrive in:

- **Question** — one line restating what was asked, so you can see which
  reading you got before you read the answer to it.
- **Answer** — the conclusion first, then the working. Bullets are bullets,
  tables are tables, and anything that can't wrap — a table, a block of code —
  scrolls inside its own box so the conversation never does.
- **Sources** — what the answer rests on, one per line, listed so it can be
  checked. Where a persona is giving you its own read rather than something it
  can point at, that line says so instead of naming a source it invented.

Nothing is padded to fill a section, so a one-sentence answer is still one
sentence. Both halves of this live in the brief itself — `[ANSWER FORMAT]` —
which is why the server can rebuild it and check the fingerprint. A format the
page applied on its own would be rejected as a stale brief.

## Answers you hear are written to be heard

The brief's `[SPOKEN ANSWER]` section asks for a second, spoken version after a
`===SPOKEN===` marker: one to three sentences, contractions, no headings, no
bullets, no URLs — what the persona would actually say to you rather than the
document read aloud. The page shows the half above the marker and speaks the
half below it, so turning the speaker on doesn't change what you read.

When a reply arrives without a marker, the spoken fallback reads the Answer
section only. The restatement and the source list are dropped, because
"Question. Sources." is not a thing anyone says.

## Settings is full screen on a desktop

Settings used to open the same way everywhere: a 560×760 card floating over the
page, one column running down it. That is the right shape for flipping a toggle
on a phone and the wrong one for adding a role, where a brief is two identity
fields, six long ones and a knowledge list — about one and a half of which fit
on screen at a time. You wrote a persona by scrolling a slot.

On a desktop or in a browser window wider than 900px it now takes the whole
screen and spends the width on making sections visible rather than wide:

- **The main pane tiles.** Company, Appearance, every team with its **Add a
  role** button, Chat, Voice and Configuration lay out in up to three columns,
  so the whole of the org is on screen at once and adding a role to Support
  doesn't mean scrolling past Legal to find it.
- **The role editor splits.** The mark, the voice and **Remove this role** sit
  in a narrow left column; the brief opens across the rest as a board of cards —
  Personality, Context and Task on one row, the knowledge list full width under
  them, Outcome, Hard rules and Out of scope on the next. Every field of a
  persona is legible at a glance, and the long fields are twice as tall.
- **The content column caps at 1520px** and centres, so a 27-inch display gets
  three comfortable columns rather than one stretched to the bezels.

Below 901px nothing changes: the sheet still rises from the bottom as a 94dvh
drawer with one column in it, pixel for pixel what it was.

## Knowledge sources: links and text, not just labels

Settings → a persona → **Knowledge sources** is where a persona's reference
material is edited, and a source is one of three things:

- **Label** — a name and nothing else ("CRM opportunity records"). What every
  source was before, and what a Sheet row with no link and no body still reads
  as. Nothing had to be migrated.
- **Website URL** — a link the persona may read. Name it or don't; an unnamed
  one shows as its address.
- **Text** — the material itself, pasted, as many lines as you like. It goes
  into the brief verbatim under its own label, indented, so the persona can see
  where the pasted material starts and stops.

**+ Add a source** starts at that fork — URL or text — and you can add as many
of either as you like. The list is ordered and the order is the priority the
prompt prints, so ↑ moves a source up the persona's reading list. ✎ edits one
in place; ✕ removes it from the persona and soft-archives the row in the Sheet,
which is why nothing a logged answer cited ever disappears.

One source is one Sheet cell, so one holds 45,000 characters. Paste more than
that and the editor says so and asks you to split it, rather than letting the
end be cut off somewhere you can't see.

## Voice accuracy

Settings → Voice accuracy reads ten test phrases aloud for you to repeat and
measures word error rate twice per pass — the speech engine's raw top guess vs.
after N-best selection and vocabulary fixes — writing each run back to the
Sheet's VoiceTests tab. Run it on the live page with a real microphone; that
measured figure is the acceptance number for the voice pipeline.
