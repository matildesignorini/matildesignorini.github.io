"""Convert an ADS BibTeX export into _data/publications.yml for the site.

Usage:  python3 scripts/bib2yml.py export-bibtex.bib

Topics and "status" notes already set in _data/publications.yml are kept
(matched by ADS bibcode), so a fresh export only adds what's new. New
papers get no topic: add one by hand afterwards.
Needs: pip install pylatexenc pyyaml
"""
import sys, re, html, json, os, yaml
from pylatexenc.latex2text import LatexNodes2Text

BIB = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), "..", "_data", "publications.yml")
src = open(BIB, encoding="utf-8").read()
l2t = LatexNodes2Text(math_mode="verbatim")

def parse(src):
    entries, i = [], 0
    while True:
        m = re.compile(r"@(\w+)\{([^,]+),").search(src, i)
        if not m: break
        j, depth, k = m.end(), 1, m.end()
        while depth:
            c = src[k]
            depth += c == "{"; depth -= c == "}"
            k += 1
        body, fields, p = src[j:k-1], {}, 0
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            pass
        pos = 0
        while True:
            fm = re.compile(r"\s*(\w+)\s*=\s*").match(body, pos)
            if not fm: break
            key, q = fm.group(1).lower(), fm.end()
            if body[q] in "{\"":
                close = "}" if body[q] == "{" else "\""
                d, r = 0, q
                while True:
                    ch = body[r]
                    if body[q] == "{":
                        d += ch == "{"; d -= ch == "}"
                        if d == 0: break
                    else:
                        if ch == "{": d += 1
                        elif ch == "}": d -= 1
                        elif ch == "\"" and r > q and d == 0: break
                    r += 1
                val, pos = body[q+1:r], r + 1
            else:
                r = body.find(",", q); r = len(body) if r < 0 else r
                val, pos = body[q:r].strip(), r
            fields[key] = val
            n = body.find(",", pos)
            if n < 0: break
            pos = n + 1
        entries.append(dict(fields, _type=m.group(1).lower(), _key=m.group(2)))
        i = k
    return entries

JOURNALS = {r"\aap": "A&A", r"\apj": "ApJ", r"\apjl": "ApJL", r"\apjs": "ApJS", r"\mnras": "MNRAS",
            r"\na": "New Astron.", r"\aj": "AJ", r"\nat": "Nature", r"\natas": "Nat. Astron.",
            "Physics of the Dark Universe": "Phys. Dark Univ.",
            "Astronomische Nachrichten": "Astron. Nachr.",
            "Memorie della Societa Astronomica Italiana": "Mem. SAIt",
            "arXiv e-prints": "arXiv preprint"}
MONTHS = {m: i+1 for i, m in enumerate("jan feb mar apr may jun jul aug sep oct nov dec".split())}

def text(s):
    return l2t.latex_to_text(s).strip()

def title(s):
    s = re.sub(r"<mml:math>.*?<mml:mi>H</mml:mi>.*?<mml:mn>0</mml:mn>.*?</mml:math>", "H₀", s)
    s = s.replace("{\\ensuremath{\\alpha}}", "α").replace("{\\ensuremath{\\lambda}}", "λ")
    s = s.replace("{\\ensuremath{\\sim}}", "~").replace("{\\ensuremath{\\leq}}", "≤")
    s = s.replace("{\\ensuremath{-}}", "-").replace("─", "–")
    s = s.replace("$JWST$", "JWST")
    s = s.replace("$Γ-λ_{Edd}$", "Γ–λ_{Edd}")
    s = s.replace("L$_{X}$-L$_{UV}$", "L_{X}–L_{UV}")
    s = re.sub(r"_\{([^}]*)\}", "\x01\\1\x02", s)
    s = s.replace("{", "").replace("}", "")
    s = html.escape(s, quote=False)
    return s.replace("\x01", "<sub>").replace("\x02", "</sub>")

def author(a):
    a = a.strip()
    m = re.match(r"^\{(.*?)\},\s*(.*)$", a)
    last, first = (m.group(1), m.group(2)) if m else (a.strip("{}"), "")
    last, first = text(last), text(first)
    initials = " ".join(p[0] + "." for p in re.split(r"[\s~]+", first) if p and p[0].isalpha())
    initials = re.sub(r"\.\s*-", ".-", initials)
    return f"{last}, {initials}" if initials else last

old = {}
if os.path.exists(OUT):
    for p in yaml.safe_load(open(OUT, encoding="utf-8")) or []:
        if p.get("bibcode"): old[p["bibcode"]] = p
new_papers = []
out = ["# Generated from an ADS BibTeX export. Order doesn't matter: the site sorts.",
       "#",
       "#   authors:   the first authors, then \"…\" and you if you're further down.",
       "#   et_al:     true adds \"et al.\" after the names shown.",
       "#   n_authors: total number of authors, shown when the list is shortened.",
       "#   status:    optional note shown before the journal, e.g. \"Submitted to A&A\".",
       "#   topics:    one or more topic names from _data/profile.yml.",
       "#              A topic that isn't in profile.yml shows up grey, at the end.",
       ""]
for e in parse(src):
    names = [author(a) for a in re.split(r"\s+and\s+", e["author"].replace("\n", " "))]
    me = next((i for i, n in enumerate(names) if n.startswith("Signorini, M")), None)
    truncated = me is None          # ADS stops listing authors at 200
    if truncated: me = len(names); names.append("Signorini, M.")
    names[me] = "Signorini, M."
    shown = names[:3] if len(names) > 5 else names
    if me >= len(shown): shown = shown + ["…", "Signorini, M."]
    j = e.get("journal") or e.get("booktitle", "")
    j = JOURNALS.get(j, text(j))
    if j == "arXiv preprint" and e.get("eprint"): j = f"arXiv:{e['eprint']}"
    if e["_key"] not in old: new_papers.append(e["_key"])
    t = title(e["title"])
    entry = {
        "title": t,
        "authors": shown,
        "n_authors": f"{len(names)-1}+" if truncated else len(names),
        "journal": j,
        "year": int(e["year"]),
        "month": MONTHS.get(e.get("month", "")[:3].lower(), 0),
        "topics": old.get(e["_key"], {}).get("topics", []),
        "status": old.get(e["_key"], {}).get("status"),
        "ads": e.get("adsurl"),
        "arxiv": f"https://arxiv.org/abs/{e['eprint']}" if e.get("eprint") else None,
        "doi": f"https://doi.org/{e['doi']}" if e.get("doi") else None,
        "bibcode": e["_key"],
    }
    out.append(f"- title: {json.dumps(entry['title'], ensure_ascii=False)}")
    out.append(f"  authors: {json.dumps(entry['authors'], ensure_ascii=False)}")
    abbreviated = len([a for a in shown if a != "…"]) < len(names)
    if abbreviated:
        last_shown = 2 if shown[-1] != "Signorini, M." or me < 3 else me
        if truncated or last_shown < len(names) - 1:
            out.append("  et_al: true")
        out.append(f"  n_authors: {json.dumps(str(entry['n_authors']))}")
    if entry["status"]: out.append(f"  status: {json.dumps(entry['status'], ensure_ascii=False)}")
    out.append(f"  journal: {json.dumps(entry['journal'], ensure_ascii=False)}")
    out.append(f"  year: {entry['year']}")
    out.append(f"  month: {entry['month']}")
    out.append(f"  topics: {json.dumps(entry['topics'], ensure_ascii=False)}")
    for k in ("ads", "arxiv", "doi", "bibcode"):
        if entry[k]: out.append(f"  {k}: {entry[k]}")
    out.append("")
open(OUT, "w", encoding="utf-8").write("\n".join(out))
print(len([l for l in out if l.startswith("- title")]), "papers")
if old and new_papers: print("New, without a topic yet:", ", ".join(new_papers))
