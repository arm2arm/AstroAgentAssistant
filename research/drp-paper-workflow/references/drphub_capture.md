DRP-Hub capture notes

1) Preferred headless Chromium command (snap path common):

/snap/bin/chromium --headless --disable-gpu --screenshot=/abs/path/to/out.png --window-size=1280,800 file:///abs/path/to/drphub_home.html

2) Fallback: wkhtmltoimage (if installed):

wkhtmltoimage --quality 90 /abs/path/to/drphub_home.html /abs/path/to/out.png

3) If page content is lazy-loaded and missing in screenshot:
 - increase window-size (e.g. 1920x1600)
 - fetch JSON endpoints (/api/cards, /api/cards/<id>) and render as verbatim LaTeX instead
 - or use headful browser + manual screenshot (not recommended for reproducibility)

4) Save screenshots into figures/ with descriptive filenames and commit them.
