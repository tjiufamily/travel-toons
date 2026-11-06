#!/usr/bin/env python3
"""Build the offline Travel Toons flipbook.

Reads trips.json (the first trip) plus the web-sized day images in
images/ and the music files in music/, and writes a single
self-contained HTML file with everything embedded as data URIs, so the
flipbook works fully offline once downloaded.

Usage (from this folder):
    python3 build_flipbook.py
    python3 build_flipbook.py --shared

Output: highlights-of-eastern-europe-flipbook.html (about 24 MB).
With --shared: highlights-of-eastern-europe-flipbook-shared.html,
the shareable version with no dedication page, no dedication line,
no mention of Christmin, and no "My Perfect Valentine" track
(Canon in D, the Chopin waltz and the theme song only). The Vercel page keeps its
dedication; only the shared file is clean for circulation.
Re-run it whenever a new day's cartoon is added to trips.json and the
images/ folder; days whose "image" is null are skipped automatically,
so Days 11-13 will be picked up as soon as they land.

The flipbook is too big for the Vercel deploy path (single-file cap
about 95 KB), so it is published through the GitHub repo and the
jsDelivr CDN instead:
    git add highlights-of-eastern-europe-flipbook.html
    git commit -m "Flipbook: ..."
    git push origin master:main
    git push origin master
Then it is served at:
    https://cdn.jsdelivr.net/gh/tjiufamily/travel-toons@main/highlights-of-eastern-europe-flipbook.html
The "Download flipbook" button on the Travel Toons page links there.
"""
import argparse
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "highlights-of-eastern-europe-flipbook.html"
SHARED_OUT = ROOT / "highlights-of-eastern-europe-flipbook-shared.html"

# Music files (local), in the order the flipbook plays them.
# The theme song is FOURTH in the image flipbook: Canon stays the
# default, the theme song is an extra track (James, 6 Nov 2026).
# The VIDEO flipbook is different: theme song only, default ON, no
# other tracks (James, 6 Nov 2026); see VIDEO-WORKFLOW.md.
TRACKS = [
    ("canon", "Canon in D", "Johann Pachelbel", ROOT / "music" / "pachelbel-canon-in-d.mp3"),
    ("chopin", "Waltz in C-sharp minor, Op. 64 No. 2", "Frédéric Chopin", ROOT / "music" / "chopin-waltz-op64-no2.mp3"),
    ("valentine", "My Perfect Valentine", "written by James for Christmin", ROOT / "music" / "my-perfect-valentine.mp3"),
    ("theme", "Across the Cobbled Square — Theme song for the trip", "Gemini", ROOT / "music" / "across-the-cobbled-square.mp3"),
]


def data_uri(path, mime):
    raw = path.read_bytes()
    return "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")


def main():
    parser = argparse.ArgumentParser(description="Build the Travel Toons flipbook.")
    parser.add_argument("--shared", action="store_true",
                        help="Build the shareable version: no dedication page, "
                             "no mention of Christmin, no Valentine track.")
    args = parser.parse_args()
    shared = args.shared
    out = SHARED_OUT if shared else OUT
    data = json.loads((ROOT / "trips.json").read_text())
    trip = data["trips"][0]
    days = [d for d in trip["days"] if d.get("image")]
    if not days:
        raise SystemExit("no days with an image in trips.json")

    # Day images as data URIs (web-sized copies only).
    images = {}
    for d in days:
        p = ROOT / d["image"]
        images[d["day"]] = data_uri(p, "image/jpeg")

    # Music as data URIs. Shared version drops the Valentine track
    # entirely (its credit names Christmin); Canon + Chopin + theme
    # song stay. The theme song is generic, no names, so it is safe
    # to circulate.
    all_tracks = TRACKS if not shared else [t for t in TRACKS if t[0] != "valentine"]
    tracks = []
    for key, title, credit, path in all_tracks:
        tracks.append((key, title, credit, data_uri(path, "audio/mpeg")))

    # Pages: cover, then (original only) dedication, then one per day.
    pages = []
    cover = (
        '<div class="page cover" data-i="0">'
        '<p class="cover-eyebrow">A travel toon journey</p>'
        '<h1>' + html.escape(trip["title"]) + '</h1>'
        '<p class="cover-sub">' + html.escape(trip.get("subtitle", "")) + '</p>'
        '<p class="cover-dates">' + html.escape(trip["dates"]) + '</p>'
    )
    if not shared:
        cover += '<p class="cover-ded">' + html.escape(trip["dedication"]) + '</p>'
    cover += '<p class="cover-hint">Tap or swipe to begin &rsaquo;</p></div>'
    pages.append(cover)
    if not shared:
        intro = (data.get("dedicationIntro") or "").strip()
        paras = [p.strip() for p in intro.split("\n") if p.strip()]
        if not paras:
            # Split the single-paragraph intro into three readable paragraphs.
            paras = [intro]
        ded_html = "".join("<p>" + html.escape(p) + "</p>" for p in paras)
        pages.append(
            '<div class="page dedication" data-i="1">'
            '<h2>For Christmin</h2>'
            '<div class="ded-text">' + ded_html + '</div>'
            '<p class="page-num">Dedication</p>'
            '</div>'
        )
    for n, d in enumerate(days):
        i = n + 1 if shared else n + 2
        pages.append(
            '<div class="page day" data-i="' + str(i) + '">'
            '<img src="' + images[d["day"]] + '" alt="Day ' + str(d["day"]) + ' — ' + html.escape(d["title"]) + '">'
            '<div class="day-cap">'
            '<p class="day-tag">Day ' + str(d["day"]) + ' of 13 &middot; ' + html.escape(d["date"]) + ' &middot; ' + html.escape(d["place"]) + '</p>'
            '<h3>' + html.escape(d["title"]) + '</h3>'
            '<p>' + html.escape(d["blurb"]) + '</p>'
            '</div>'
            '</div>'
        )

    pages_html = "\n".join(pages)
    total = len(pages)

    # Music track data (embedded as data URIs).
    canon_uri = tracks[0][3]
    chopin_uri = tracks[1][3]
    theme_uri = [t[3] for t in tracks if t[0] == "theme"][0]

    doc = TEMPLATE
    doc = doc.replace("__TITLE__", html.escape(trip["title"]))
    doc = doc.replace("__DATES__", html.escape(trip["dates"]))
    if shared:
        # No dedication line in the top header at all. Note __DATES__
        # was already replaced above, so match the rendered dates line.
        doc = doc.replace(" &middot; __DEDICATION__", "")
        # Page labels: cover, then Day 1 directly (no Dedication page).
        doc = doc.replace(
            "function pageName(i){\n  if (i === 0) return 'Cover';\n"
            "  if (i === 1) return 'Dedication';\n"
            "  return 'Day ' + (i - 1) + ' of __DAYS_INCLUDED__';\n}",
            "function pageName(i){\n  if (i === 0) return 'Cover';\n"
            "  return 'Day ' + i + ' of __DAYS_INCLUDED__';\n}")
        # Drop the Valentine track button, its JS entry, toggle and
        # click handler, and update the music hint. Also drop the
        # dedication CSS rules so the word appears nowhere in the file.
        doc = doc.replace(
            '    <button class="track-btn" id="trackValentine" type="button">'
            '&#9654; My Perfect Valentine &mdash; written by James for Christmin</button>\n', "")
        doc = doc.replace(
            "  valentine: { title: 'My Perfect Valentine', file: '__VALENTINE_URI__', "
            "label: 'My Perfect Valentine \\u2014 written by James for Christmin' },\n", "")
        doc = doc.replace(
            "  document.getElementById('trackValentine').classList.toggle('active', key === 'valentine');\n", "")
        doc = doc.replace(
            "document.getElementById('trackValentine').onclick = function(){ setTrack('valentine'); };\n", "")
        doc = doc.replace(
            "; the Chopin waltz, &ldquo;My Perfect Valentine&rdquo; and the theme song &ldquo;Across the Cobbled Square&rdquo; play only when you choose them.",
            "; the Chopin waltz and the theme song &ldquo;Across the Cobbled Square&rdquo; play only when you choose them.")
        doc = doc.replace(".page.cover,.page.dedication{", ".page.cover{")
        doc = doc.replace(
            ".page.dedication h2{font-size:clamp(1.6rem,4vw,2.2rem);margin-bottom:16px}\n", "")
        doc = doc.replace(
            ".ded-text{font-family:var(--serif);font-size:clamp(1rem,2.2vw,1.2rem);line-height:1.85;color:#f7ead0;max-width:640px;text-align:left;overflow-y:auto}\n", "")
        doc = doc.replace(".ded-text p{margin-bottom:14px}\n", "")
    else:
        doc = doc.replace("__DEDICATION__", html.escape(trip["dedication"]))
        valentine_uri = tracks[2][3]
        doc = doc.replace("__VALENTINE_URI__", valentine_uri)
    doc = doc.replace("__PAGES__", pages_html)
    doc = doc.replace("__TOTAL__", str(total))
    doc = doc.replace("__DAYS_INCLUDED__", str(len(days)))
    doc = doc.replace("__CANON_URI__", canon_uri)
    doc = doc.replace("__CHOPIN_URI__", chopin_uri)
    doc = doc.replace("__THEME_URI__", theme_uri)

    out.write_text(doc, encoding="utf-8")
    size = out.stat().st_size
    print("wrote", out.name)
    print("days included:", len(days), "(Days " + str(days[0]["day"]) + "–" + str(days[-1]["day"]) + ")")
    print("size: %d bytes (%.2f MB, %.2f MiB)" % (size, size / 1_000_000, size / 1_048_576))


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__ — Flipbook</title>
<style>
:root{--ink:#f5efe4;--ink-dim:#cfc4ae;--gold:#d9a441;--gold-soft:#e8c37a;--bg:#0d0b09;--card:#1d1813;--line:rgba(217,164,65,.35);--serif:Georgia,'Times New Roman',serif;--sans:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);line-height:1.6;-webkit-font-smoothing:antialiased;min-height:100svh;display:flex;flex-direction:column;align-items:center;padding:18px 14px 28px}
h1,h2,h3{font-family:var(--serif);font-weight:400}
.top{width:100%;max-width:920px;text-align:center;margin-bottom:14px}
.top h1{font-size:clamp(1.5rem,4.5vw,2.2rem)}
.top p{color:var(--ink-dim);font-size:.9rem}
.book{position:relative;width:100%;max-width:920px;aspect-ratio:16/14;perspective:1800px}
.page{position:absolute;inset:0;background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;backface-visibility:hidden;transform-origin:left center;transition:transform .75s cubic-bezier(.22,.8,.24,1);display:flex;flex-direction:column}
.page.flipped{transform:rotateY(-180deg);pointer-events:none}
.page.cover,.page.dedication{align-items:center;justify-content:center;text-align:center;padding:28px 26px;background:radial-gradient(120% 120% at 20% 10%,#2b2118 0%,#171310 55%,#0d0b09 100%)}
.cover-eyebrow{letter-spacing:.35em;text-transform:uppercase;font-size:.7rem;color:var(--gold-soft);margin-bottom:14px}
.page.cover h1{font-size:clamp(2rem,6vw,3.4rem);line-height:1.1}
.cover-sub{font-family:var(--serif);font-style:italic;color:var(--ink-dim);margin-top:10px;font-size:clamp(1rem,2.4vw,1.3rem)}
.cover-dates{margin-top:16px;color:var(--gold-soft);letter-spacing:.12em;text-transform:uppercase;font-size:.85rem}
.cover-ded{font-family:var(--serif);font-style:italic;font-size:clamp(1rem,2.4vw,1.25rem);color:#f7ead0;margin-top:18px}
.cover-hint{margin-top:26px;color:var(--gold-soft);letter-spacing:.18em;text-transform:uppercase;font-size:.8rem}
.page.dedication h2{font-size:clamp(1.6rem,4vw,2.2rem);margin-bottom:16px}
.ded-text{font-family:var(--serif);font-size:clamp(1rem,2.2vw,1.2rem);line-height:1.85;color:#f7ead0;max-width:640px;text-align:left;overflow-y:auto}
.ded-text p{margin-bottom:14px}
.page.day img{width:100%;aspect-ratio:16/9;object-fit:cover;flex:0 0 auto}
.day-cap{flex:1 1 auto;min-height:0;padding:16px 20px 14px;overflow-y:auto}
@media (max-width:700px){.book{aspect-ratio:16/18}.day-cap{padding:12px 16px 16px}.day-cap h3{font-size:1.25rem}}
.day-tag{color:var(--gold-soft);font-size:.78rem;letter-spacing:.14em;text-transform:uppercase}
.day-cap h3{font-size:clamp(1.3rem,3.4vw,1.8rem);margin:4px 0 6px}
.day-cap p{color:var(--ink-dim)}
.page-num{margin-top:auto;padding:0 20px 12px;color:var(--ink-dim);font-size:.78rem;letter-spacing:.14em;text-transform:uppercase}
.controls{width:100%;max-width:920px;display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:16px}
.controls button{padding:11px 20px;border-radius:999px;border:1px solid var(--gold);background:var(--gold);color:#14100c;font-size:1rem;cursor:pointer;font-family:var(--sans)}
.controls button:disabled{opacity:.45;cursor:default}
.controls button.ghost{background:transparent;color:var(--gold-soft);border-color:var(--line)}
.page-label{color:var(--ink-dim);font-size:.9rem;text-align:center}
.music{width:100%;max-width:920px;margin-top:18px;border:1px solid var(--line);border-radius:14px;padding:16px 18px;background:rgba(23,19,16,.85);text-align:center}
.music .now{color:var(--ink-dim);font-size:.9rem;margin-bottom:10px}
.music .now b{color:var(--ink)}
.track-btn{display:inline-block;margin:5px 6px;padding:9px 16px;border:1px solid var(--line);border-radius:999px;background:rgba(23,19,16,.85);color:var(--ink);font-family:var(--sans);font-size:.85rem;cursor:pointer}
.track-btn:hover,.track-btn.active{border-color:var(--gold);color:var(--gold-soft)}
.music .hint{color:var(--ink-dim);font-size:.82rem;margin-top:10px}
</style>
</head>
<body>
<div class="top">
  <h1>__TITLE__</h1>
  <p>__DATES__ &middot; __DEDICATION__</p>
</div>

<div class="book" id="book">
__PAGES__
</div>

<div class="controls">
  <button id="prevBtn" type="button">&lsaquo; Prev</button>
  <span class="page-label" id="pageLabel"></span>
  <button id="nextBtn" type="button">Next &rsaquo;</button>
</div>

<div class="music">
  <p class="now"><b>Now playing:</b> <span id="nowPlaying">Canon in D major &mdash; Johann Pachelbel</span></p>
  <p>
    <button class="track-btn active" id="trackCanon" type="button">&#9654; Canon in D &mdash; Pachelbel</button>
    <button class="track-btn" id="trackChopin" type="button">&#9654; Chopin &mdash; Waltz in C-sharp minor</button>
    <button class="track-btn" id="trackValentine" type="button">&#9654; My Perfect Valentine &mdash; written by James for Christmin</button>
    <button class="track-btn" id="trackTheme" type="button">&#9654; Across the Cobbled Square &mdash; Theme song</button>
  </p>
  <p><button class="track-btn" id="musicFab" type="button">Pause music</button></p>
  <p class="hint">Pachelbel&rsquo;s Canon in D starts playing when the flipbook opens; the Chopin waltz, &ldquo;My Perfect Valentine&rdquo; and the theme song &ldquo;Across the Cobbled Square&rdquo; play only when you choose them. This file works fully offline &mdash; the pictures and music are inside it.</p>
</div>

<audio id="audio" loop preload="auto"></audio>

<script>
var pages = Array.prototype.slice.call(document.querySelectorAll('.page'));
var N = pages.length;
var cur = 0;
var label = document.getElementById('pageLabel');
var prevBtn = document.getElementById('prevBtn');
var nextBtn = document.getElementById('nextBtn');
function pageName(i){
  if (i === 0) return 'Cover';
  if (i === 1) return 'Dedication';
  return 'Day ' + (i - 1) + ' of __DAYS_INCLUDED__';
}
function render(){
  pages.forEach(function(p, i){
    p.classList.toggle('flipped', i < cur);
    if (i < cur) p.style.zIndex = i + 1;
    else if (i === cur) p.style.zIndex = N + 1;
    else p.style.zIndex = N - i;
  });
  label.textContent = pageName(cur) + '  ·  ' + (cur + 1) + ' / ' + N;
  prevBtn.disabled = cur === 0;
  nextBtn.disabled = cur === N - 1;
}
function go(i){
  cur = Math.max(0, Math.min(N - 1, i));
  render();
}
prevBtn.onclick = function(){ go(cur - 1); };
nextBtn.onclick = function(){ go(cur + 1); };
document.addEventListener('keydown', function(e){
  if (e.key === 'ArrowLeft') go(cur - 1);
  if (e.key === 'ArrowRight') go(cur + 1);
});
var startX = null, dragging = false;
var book = document.getElementById('book');
book.addEventListener('pointerdown', function(e){ startX = e.clientX; dragging = true; });
book.addEventListener('pointerup', function(e){
  if (!dragging || startX === null) return;
  var dx = e.clientX - startX;
  if (Math.abs(dx) > 50) go(cur + (dx < 0 ? 1 : -1));
  dragging = false; startX = null;
});
book.addEventListener('pointercancel', function(){ dragging = false; startX = null;
});
book.addEventListener('click', function(e){
  var r = book.getBoundingClientRect();
  var x = e.clientX - r.left;
  if (x > r.width * 0.72) go(cur + 1);
  else if (x < r.width * 0.28) go(cur - 1);
});
render();

/* Music: three tracks, all embedded. Canon plays by default. */
var TRACKS = {
  canon: { title: 'Canon in D', file: '__CANON_URI__', label: 'Canon in D major \u2014 Johann Pachelbel' },
  chopin: { title: 'Chopin', file: '__CHOPIN_URI__', label: 'Waltz in C-sharp minor, Op. 64 No. 2 \u2014 Fr\u00e9d\u00e9ric Chopin' },
  valentine: { title: 'My Perfect Valentine', file: '__VALENTINE_URI__', label: 'My Perfect Valentine \u2014 written by James for Christmin' },
  theme: { title: 'Across the Cobbled Square', file: '__THEME_URI__', label: 'Across the Cobbled Square \u2014 Theme song for the trip' }
};
var audio = document.getElementById('audio');
var fab = document.getElementById('musicFab');
var nowPlaying = document.getElementById('nowPlaying');
var currentKey = 'canon';
function setTrack(key){
  currentKey = key;
  audio.src = TRACKS[key].file;
  nowPlaying.textContent = TRACKS[key].label;
  document.getElementById('trackCanon').classList.toggle('active', key === 'canon');
  document.getElementById('trackChopin').classList.toggle('active', key === 'chopin');
  document.getElementById('trackValentine').classList.toggle('active', key === 'valentine');
  document.getElementById('trackTheme').classList.toggle('active', key === 'theme');
  audio.play().then(function(){
    fab.textContent = 'Pause music';
  }).catch(function(){
    fab.textContent = 'Tap to play ' + TRACKS[key].title;
  });
}
document.getElementById('trackCanon').onclick = function(){ setTrack('canon'); };
document.getElementById('trackChopin').onclick = function(){ setTrack('chopin'); };
document.getElementById('trackValentine').onclick = function(){ setTrack('valentine'); };
document.getElementById('trackTheme').onclick = function(){ setTrack('theme'); };
fab.onclick = function(){
  if (audio.paused) {
    audio.play().then(function(){ fab.textContent = 'Pause music'; })
      .catch(function(){ fab.textContent = 'Tap again to play'; });
  } else {
    audio.pause();
    fab.textContent = 'Play ' + TRACKS[currentKey].title;
  }
};
/* Canon starts on load; if the browser blocks autoplay, the button
   offers a tap to start it. */
audio.src = TRACKS.canon.file;
audio.play().then(function(){
  fab.textContent = 'Pause music';
}).catch(function(){
  fab.textContent = 'Tap to play Canon in D';
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
