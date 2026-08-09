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
