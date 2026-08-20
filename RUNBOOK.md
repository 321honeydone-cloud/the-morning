# the-morning

Manny's PIN-gated daily morning brief, published to GitHub Pages at morning.321honeydone.com.

Daily pipeline (6 AM ET weekdays, run by Manny's scheduled Claude task):

1. git pull this repo.
2. For every queue/*.json: archive that Gmail thread (remove the INBOX label), then git rm the file.
3. Promo sweep: Gmail categories promotions, social, updates get the Promos label and leave the inbox. Transactional, government, school, medical, and financial mail is never touched.
4. Gather calendar, inbox, and Melbourne FL weather (forecast.weather.gov). Calendar means ALL calendars on the account, not just 321honeydone@gmail.com: always include the Family group calendars from list_calendars (family17388733884721953521@group.calendar.google.com holds most personal appointments such as VPRR, dental, audiogram, BDD exams, and OLL school events). Build the dark industrial brief.
5. Encrypt with tools/encrypt_brief.py (AES-256-GCM, PBKDF2-SHA256 600k iterations, fixed public salt). The PIN comes from the scheduled task config. All personal content and the queue-writer token live only inside the ciphertext.
6. Commit index.html plus queue deletions, push to main. Pages serves it.

The public wrapper (index.html as served) contains only the PIN gate and ciphertext.

## Priority appointments

Two categories outrank everything else in the brief and must never be dropped:

1. **Jobber jobs.** Manny's work schedule lives in Jobber and reaches Google through Jobber's one-way iCal calendar sync (Google refreshes it roughly every 12 hours). In the gather, always call list_calendars and include every calendar whose name mentions Jobber (or that carries getjobber.com events) alongside the account and Family calendars. Every Jobber visit today gets a gold dot on the terrain and a named line in its act. Week-ahead days with Jobber visits get a gold event tag with the client name or job, and the headline names the first job when one lands today. If no Jobber calendar exists on the account yet, fall back to fresh Jobber notification emails (notification@*.getjobber.com) for anything scheduled, and note once in the brief that the Jobber calendar sync is not connected.
2. **VA BDD appointments.** Anything tied to the VA claim: BDD, C&P, SHPE, SHA sittings, VA exams, VSO meetings (Jose Nazario), VPRR. Same treatment: terrain dot with label, named act line, week-ahead tag, plus a PREP row in Needs Attention the day before any exam or sitting.

If a Jobber job and a BDD appointment share a day, the headline names them both. These two beat promos, bills, and everything else for space on the page.

## Workout tab

The brief has two tabs: BRIEF and WORKOUT. The workout module lives in this repo:

- `workouts/plan.json` — the Mon/Wed/Fri full body plan (high rep, low weight). Edit here to change the plan.
- `workouts/log/` — one JSON file per logged set. Written live by the tab's LOG SET button through the GitHub contents API (same pattern as `queue/`), or by the pipeline from Whspr transcript emails once that bridge is set up.
- `workouts/history.json` — rolled-up history keyed by date then exercise slug. This is what powers the "last time" line under each exercise.
- `tools/workout_parse.py` — parses raw spoken lines ("25 pounds 3 sets of 15") into weight, sets, reps and rolls log files into history.

Daily pipeline additions (every run, not just training days):

1. Before building: search Gmail for Whspr workout transcript emails (subject or sender containing "whspr", unconfigured until Manny sends a test note). Write each as a `workouts/log/*.json` entry with the raw transcript.
2. Run `python3 tools/workout_parse.py .` then `git rm` the consumed `workouts/log/*.json` files. Commit the updated `workouts/history.json`.
3. Build the brief from `templates/brief_template.html`: substitute the font placeholders, `__PLAN_JSON__` with `workouts/plan.json`, `__HISTORY_JSON__` with `workouts/history.json`, and `__GH_TOKEN__` with the queue-writer token. Update the date, weather, headline, terrain, stats, and list panels for the day. The workout tab itself is client-side and picks the right day automatically.

## Panels (added 2026-08-19)

The brief template no longer carries sample day content. `templates/brief_template.html`
holds the chassis (fonts, tokens, CSS, workout tab, JS) and one placeholder,
`__BRIEF_BODY__`, which the daily build fills with the whole BRIEF tab. Build the body in
this order:

headline · terrain · acts · stat grid · NEEDS ATTENTION · VA CLAIM · LEADS AND QUOTES ·
MONEY · ALBIE · SkillBridge strip · RESOLVED · WEEK AHEAD

A panel with nothing real in it gets dropped for the day, heading and all. Never render an
empty panel or a placeholder row.

### Stat grid

Meetings Today · Needs You · Open Pipeline · Today's High. Open Pipeline is the sum of the
Coming In column, rounded to one decimal in thousands.

### VA CLAIM (`.panel.mission`)

Header carries a countdown to the next hard claim date, a progress bar of exam sittings
done over total, and the packet window. Claim items live here and NOT in Needs Attention,
so nothing repeats. Track every C&P sitting, the packet review window, records deadlines
(DoD SAFE pickups expire 7 days after drop off), and anything from Jose Nazario. Never put
a draft-reply button on a medical or claim row.

### LEADS AND QUOTES

Every open lead and unanswered quote, each with an age clock (`.age`, and `.age.hot` past
10 days). Sources: ProReferral notifications, Jobber quote and request emails, supplier
threads waiting on Manny. Sorted newest first. This panel is money, so it never gets cut
for space.

### MONEY

Two columns. Coming In is built from Jobber notification emails: invoices sent, quotes
approved, deposits paid, balances outstanding. Going Out is the next 30 days of recurring
bills read off the most recent notice for each (FACTS tuition, SoFi, FPL, Chase, Sherwin).
QuickBooks holds only mileage and receipts on this account, so it has no invoices and must
not be used as an AR source. Always print the footer line saying which side is estimated.

### ALBIE

Everything for Albion: OLL homework and letters, FACTS tuition, Step Up / SUFS attestations
and scholarship items, Catholic Youth Sports and PlayMetrics, school events. School items
go here, not in Needs Attention.

### SkillBridge strip (`.strip`)

Compact countdown to 9/2 plus one line of current status. Retire the strip once the program
starts and reuse it for whatever countdown matters next.

### Draft reply buttons

Rows where Manny owes someone a written reply get a second action, `.dr`, next to the tag.
It opens a seeded Claude session at
`https://claude.ai/new?q={urlencoded seed}&surface=cowork&composer=mini`.
The seed opens imperative, describes the thread in Manny's own terms without quoting the
other person, tells the fresh session to search Gmail and re-read the thread itself, names
the connected tools, and closes on a Gmail draft. No seed on anything touching medical
records, the claim, credentials, or account numbers.

### Jobber

Still no Jobber calendar on the account. Until an iCal feed is wired in, jobs come only
from Jobber notification emails and customer replies, and any job named in the brief says
so once.

## Calendar accounts (corrected 2026-08-20)

The Google Calendar connector is authenticated as **mrivero24@gmail.com**, not
321honeydone@gmail.com. Call list_calendars every run and read every calendar returned.
The ones that matter:

- `mrivero24@gmail.com` primary: personal appointments, recurring bills, meetings
- `s1pr4fei8rnfrl98o6hi3043m6rdsgog@import.calendar.google.com`: **the Jobber feed.** Its
  summary is the raw getjobber.com iCal URL. Every HoneyDone job lives here with the client
  name in the title, the address in `location`, and the scope in `description`. This is
  priority one, per the Jobber section above. Do not try to fetch the getjobber.com URL
  directly, it is blocked by robots.txt. Read it through the Google calendar id.
- `family17388733884721953521@group.calendar.google.com`: family and school events
- `en.usa#holiday`, `NCOA 22-3`, `en.uk#holiday`: ignore unless something lands on them

Known gap: events created on 321honeydone@gmail.com with no attendees are invisible from
this account. The BDD final packet review block (Aug 24 to 28) is one of them, so it is
carried in the VA CLAIM panel from the RUNBOOK rather than read off a calendar. If Manny
shares the 321honeydone calendar with mrivero24, drop this workaround.

## JOB PREP panel

Renders when a Jobber job falls today or tomorrow, placed directly under Needs Attention.
Header line carries time window, client, address, job value if known, and scope. Three
columns of locally-checkable items: Buy or Confirm Loaded, Tools Beyond the Bag, Sequence
and Gotchas. Build them from `jobs/checklists.json` by matching the Jobber job title
against each entry's `match` keywords, then subtract anything listed in `jobs/edc.json`.
While `edc.json` has `recorded: false`, render the full list and say so in the footer note.
Checkbox state is localStorage only under key `mb_job` and never touches the network. Add a
gotcha line naming the next job on the calendar so nothing bleeds into it.

## Google search bar

The page is Manny's browser homepage. The chassis carries a plain GET form to
google.com/search above the tabs. It needs no JS, no key, and no upkeep. Leave it in place.
