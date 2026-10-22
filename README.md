# matildesignorini.com

Personal website of Matilde Signorini, built with Jekyll and served by GitHub Pages.

Content lives in plain data files, so most updates don't touch the page itself:

| What | File |
|---|---|
| Name, role, bio, links, research interests, CV, contact | `_data/profile.yml` |
| Publications (generated from an ADS BibTeX export) | `_data/publications.yml` |
| Invited talks | `_data/talks.yml` |
| Outreach | `_data/outreach.yml` |
| CV and slides (PDF) | `files/` |
| Colours and layout | `assets/css/style.css` |

To refresh publications from a new ADS export (keeps existing topics):

    pip install pylatexenc pyyaml
    python3 scripts/bib2yml.py export-bibtex.bib
