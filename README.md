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

## Connecting is not something you do

The token is the only thing standing between the page and the Sheet, and it
used to live in exactly one place: `localStorage`, in whichever browser had
been told about it. That made *connected* a property of a device rather than
of the app — every new laptop, phone, profile, private window, or cleared
site-data landed you back on sample data with a banner asking you to go and
paste something.

There are now three places a token can come from, tried in order. The app is
connected if **any** of them answers:

| | Where | What it costs you |
| --- | --- | --- |
| 1 | `localStorage` — pasted into Settings › Chat | One paste, per browser |
| 2 | The URL — `#token=…` or `?token=…` | One visit, per device |
| 3 | `SHEET_TOKEN` in `index.html` | Nothing, ever |

**Layer 3 is the one that makes it automatic.** Fill the constant near the top
of `index.html` with your `APP_TOKEN` and there is no first-run step left at
all: any browser that can open the page opens it connected. Read the value
from Apps Script → Project Settings → **Script Properties** → `APP_TOKEN`
rather than inventing a new one.

Understand what you are trading. That constant is a real credential in a file
anyone who can load the page can read, so on a public GitHub Pages site it
means whoever finds the page can read and write the Sheet behind it and spend
the Anthropic key it proxies. That is the right trade for a workspace page
whose URL you keep to yourself and the wrong one for a page you hand out.
Rotating it is one edit here plus `APP_TOKEN` in Script Properties.

**Layer 2 is how you connect a device without publishing anything.** Open

    https://your-page/#token=YOUR_APP_TOKEN

once. The token is saved into that browser and then scrubbed out of the
address bar with `replaceState`, so it does not survive into history, a
screenshot, or a link copied after arriving. `&endpoint=https://…/exec` works
the same way when the deployment has moved.

Once connected — by any of the three — personas, settings, and conversation
logs sync both ways automatically, on the cadence the Sheet's
`sync_interval_seconds` setting defines.

## What "both directions" actually covers

Everything you can change in Settings is written back to the Sheet, on a short
pause after you stop typing:

| What you change | Where it lands |
| --- | --- |
| Any field of a brief, the mark, the team, the knowledge sources | That persona's `Personas` row, and `KnowledgeSources` |
| **Add a role** | A new `Personas` row, created the moment you add it, keeping the id the app minted |
| **Remove this role** | `Status` on that row becomes `archived` — nothing is erased, and the conversations it answered in still name it |
| Company name, subtitle, page heading, intro line | The `OrgCharts` row |
| Theme, accent, reporting lines, mark animation | The same row |

Two rules make this safe to lean on. A write that fails for weather — a cold
start, a dropped network, a redeploy landing mid-request — **retries on its own**
rather than dropping the edit; only a rejected token or a genuine conflict with
another device stops it, and both say so in a banner. And a background read
**never overwrites something this browser hasn't saved yet**: an edit made a
moment ago, or a role added a moment ago, survives every sync tick until the
Sheet confirms it.

Removing a role is refused while another role reports to it, in the app and in
the Sheet both — the chart is drawn from `ParentPersonaId`, so the subtree under
it would simply disappear. Move the reports first.

## When it isn't connecting

The dot in the header is the whole answer: lit means personas and settings
came from the Sheet, unlit means the page is on built-in sample data. Chat
needs only the token, so it keeps working either way — which is why a
disconnected page can still answer questions and log them to the Sheet while
nothing you edit reaches it. Everything below that dot follows from it:
background sync and persona write-back run only while it is lit, and an edit
made while it is unlit stays in the browser and says so in a banner. Adding a
role is the one thing an unlit page refuses outright rather than accepting and
losing: a new role only exists once the Sheet has a row for it, so there is
nothing honest to do with a brief written against a row that was never made.

Your past conversations are on the lit side of that line, since reading them
means reading the Sheet. An unlit page lists only what this browser has said in
this session, and the line under the list says so rather than presenting a short
history as the whole of it. New conversations are still logged either way, so
nothing said while it was unlit is lost — it appears in the list once the read
succeeds.

Three things turn it off, in rough order of how often they do:

- **No token anywhere.** With `SHEET_TOKEN` left empty, the token lives only in
  whichever browser was told about it, so every new browser, device, profile,
  or cleared-site-data is a fresh paste — and private windows and Safari's
  tracking prevention (which evicts local storage for sites left alone for a
  week) throw it away silently. Filling `SHEET_TOKEN` is what retires this
  cause entirely; the `#token=` link retires it one device at a time.
- **The token is lost.** Because it is paste-once, blanking `APP_TOKEN` in
  `Code.gs` — as this repo's copy ships — leaves the only surviving copy in
  Apps Script's **Project Settings → Script Properties**. Read it there rather
  than inventing a new one; a new one has to be re-pasted everywhere.
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

## The workspace

The app reads as a workspace rather than as a chart with a messenger bolted to
it: a dark rail down the left with the lists in it, and the conversation
filling everything else.

- **The rail is one dark column** in both themes, under a header that names the
  workspace and a pencil that starts a new chat. That is what makes the two
  panes read as one object with a spine, instead of as two sheets of the same
  white that happen to sit beside each other.
- **The lists are both open at once.** *Conversations* and *Team* are sections
  in one scroller, each with a disclosure triangle, and either collapses (the
  app remembers which). Picking somebody to talk to used to mean switching to
  a Team pane first, losing sight of your history to do it; now both are simply
  there. The state persists per browser.
- **The conversation fills the window.** The capped, centred column is gone —
  a wide window gave you a narrow document with two empty margins.
- **The accent still yours, still readable.** The selected row in the rail is a
  solid block of your accent with white text on it, and several of the accents
  on offer are far too light to carry white — on the orange it reads at 2.5:1,
  well under the 4.5:1 ordinary text needs. Rather than flip that one row's
  label to black, the fill is darkened just far enough to carry white and no
  further, so the colour you picked is still the colour you see.

## The side menu

**Conversations** is your history, newest first, grouped Today / Yesterday /
Previous 7 days / Previous 30 days / by month. Each row shows the cast that
spoke in that conversation as stacked marks, its name, and how long it ran — so
a conversation that changed hands is recognisable before you open it. Hovering
a row reveals rename and delete; delete asks once, marks the row deleted in the
Sheet, and never removes a logged message. **+ New chat** — the pencil in the
header, or the row under the list — starts a fresh conversation with whoever is
on screen, and pressing it twice does not leave a trail of empty ones.

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

A chat does not have to belong to one person. The header carries the members as
a facepile with a count, the bar above the message box lists everyone in the
current conversation and who is answering right now, and one tap on a chip
hands the thread to them.

Adding somebody has three doors to the same room, because "who else is in
here?" and "add someone" are the same question asked twice: the **add-person
icon** in the header, the **facepile itself** (a member list you can click is
how you expect to add a member), and **+ Bring in** on the cast bar. Nothing is
lost in the handover — the transcript stays whole, each reply is marked with
its author's icon and title, and the newcomer can be put straight onto the
question already on the table with **Ask them the same question**.

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

## Every message is signed

Attribution used to be conditional. A reply wore its author's mark only once a
second persona had joined, and what you typed wore nothing at all, because a
right-aligned coloured bubble was understood to be yours. That reads fine as a
phone messenger and badly as a workplace transcript: the two speakers are told
apart by which edge of the column they hug, so scrolling back through a thread
gives you a wall of alternating shapes rather than a list of who said what.

Every message is now one row — avatar, name, time, then the words at the full
width of the column. It is what lets an answer hold a table or a block of code
without fighting a 68%-wide balloon for room, and what makes a thread with four
people in it readable as a transcript. Runs by the same person inside five
minutes collapse into the first row's header, so a signed transcript doesn't
become a stack of name tags; a collapsed row shows its own time on hover.

**Nothing the app says is signed with a persona's name.** A failed request
carries the persona's id so a retry knows who to ask again, but that id is
routing, not authorship — putting "Couldn't get a reply" under someone's face
would attribute words to them they never said, in the one place a reader is
least able to tell the difference. Failures and system notes render unsigned,
and they end a run, so the answer that follows one always re-introduces its
author.

A **date divider** marks each day the conversation ran across, labelled with
the day itself — the buckets in the side menu ("Previous 7 days") are right for
sorting a list into piles and wrong on a divider, which marks one specific day.

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
