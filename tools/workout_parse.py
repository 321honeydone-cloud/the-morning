#!/usr/bin/env python3
"""Roll workout set logs into history.

Reads workouts/log/*.json (written by the brief's mic button, or by the
pipeline from Whspr transcript emails), parses each raw transcript into
structured sets, appends them to workouts/history.json keyed by date and
exercise slug, then deletes the consumed log files (git rm is the caller's
job, this script just moves data).

Usage: python3 tools/workout_parse.py [repo_root]

Log file shape (one JSON object per file):
  {"date":"2026-07-27","day":"monday","slug":"goblet-squat",
   "exercise":"Goblet squat","raw":"25 pounds 3 sets of 15",
   "weight":25,"reps":15,"sets":3,"source":"mic"}
Only "raw" is required beyond identity fields. Parsed fields win when present,
otherwise raw is re-parsed here.

History shape (workouts/history.json):
  {"2026-07-27": {"goblet-squat": {"exercise":"Goblet squat",
      "entries":[{"weight":25,"reps":15,"sets":3,"raw":"..."}]}}}
"""
import json, re, sys, pathlib

WORDNUMS = {
    "one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,
    "nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,
    "fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,
    "twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,"seventy":70,
    "eighty":80,"ninety":90,"hundred":100,
}

def words_to_digits(text):
    """Cheap word-number normalizer: 'twenty five' -> '25'."""
    out, acc = [], 0
    for tok in re.split(r"\s+", text.lower()):
        t = tok.strip(",.")
        if t in WORDNUMS:
            v = WORDNUMS[t]
            acc = acc * 100 if v == 100 and acc else acc + v
        else:
            if acc:
                out.append(str(acc)); acc = 0
            out.append(tok)
    if acc:
        out.append(str(acc))
    return " ".join(out)

def parse_raw(raw):
    """Best effort parse of a spoken set line into weight, sets, reps.

    Matched phrases are consumed from the working string so leftover bare
    numbers can fill the remaining fields (weight first, then reps).
    A single bare number with nothing else means reps.
    """
    t = words_to_digits(raw or "")
    s = t
    res = {}

    def take(pattern, key, cast):
        nonlocal s
        m = re.search(pattern, s, re.I)
        if m and key not in res:
            res[key] = cast(m.group(1))
            s = s[:m.start()] + " " + s[m.end():]

    take(r"(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound|pounds|#)", "weight", float)
    take(r"(\d+)\s*sets?", "sets", int)
    take(r"(\d+)\s*reps?", "reps", int)
    m = re.search(r"(\d+)\s*(?:x|by)\s*(\d+)", s, re.I)
    if m:
        res.setdefault("sets", int(m.group(1)))
        res.setdefault("reps", int(m.group(2)))
        s = s[:m.start()] + " " + s[m.end():]
    if re.search(r"body\s*weight", t, re.I):
        res.setdefault("weight", 0)
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", s)]
    if len(nums) == 1 and not res:
        res["reps"] = int(nums[0])
    else:
        for v in nums:
            if "weight" not in res:
                res["weight"] = v
            elif "reps" not in res:
                res["reps"] = int(v)
    return res

def main():
    root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    logdir = root / "workouts" / "log"
    histfile = root / "workouts" / "history.json"
    hist = json.loads(histfile.read_text()) if histfile.exists() else {}
    consumed = []
    for f in sorted(logdir.glob("*.json")) if logdir.exists() else []:
        try:
            e = json.loads(f.read_text())
        except Exception:
            continue
        date, slug = e.get("date"), e.get("slug", "unknown")
        if not date:
            continue
        parsed = parse_raw(e.get("raw", ""))
        entry = {
            "weight": e.get("weight", parsed.get("weight")),
            "sets": e.get("sets", parsed.get("sets")),
            "reps": e.get("reps", parsed.get("reps")),
            "raw": e.get("raw", ""),
            "source": e.get("source", "unknown"),
        }
        day = hist.setdefault(date, {})
        ex = day.setdefault(slug, {"exercise": e.get("exercise", slug), "entries": []})
        if entry not in ex["entries"]:
            ex["entries"].append(entry)
        consumed.append(str(f))
    histfile.write_text(json.dumps(hist, indent=2))
    print(json.dumps({"consumed": consumed, "dates": sorted(hist.keys())}))

if __name__ == "__main__":
    main()
