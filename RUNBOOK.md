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
