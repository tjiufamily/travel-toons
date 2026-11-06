#!/usr/bin/env python3
"""Build the VIDEO Travel Toons flipbook (family version).

Reads trips.json (the first trip) plus the per-day subtitle cues in
subtitles-continuous-narration.srt, and writes a single SMALL HTML file
that REFERENCES its media by URL instead of embedding it:

  - each day page shows its 10-second silent day clip from jsDelivr
    (videos/day-NN.mp4), with the day cartoon as its poster image
  - each day page plays its narration slice (audio/narration-day-NN.mp3,
    cut from the continuous Vanessa narration by the SRT cue times)
  - subtitles: the day's SRT cue text as a caption bar BELOW the video
    (never overlaid on the panels, so the words never cover the cartoon),
    shown while the clip plays
  - music: the theme song ONLY ("Across the Cobbled Square", via
    jsDelivr), default ON; it pauses while a day video plays and comes
    back when the video ends, only if the user had it on

The narration slices are cut separately (not by this script):
    ffmpeg -i audio-continuous-narration-vanessa.mp3 \
      -ss <cue start> -to <cue end> -c:a libmp3lame -q:a 3 \
      audio/narration-day-NN.mp3
Cue times come from subtitles-continuous-narration.srt (cues 2-14 are
Days 1-13; cue 1 is the intro, cues 15-16 the ending).

Family version: dedication page and dedication line included, like the
original image flipbook (NOT the shared one). No "My Perfect Valentine"
anywhere, no other music track.

Page-flip structure and geometry are reused from build_flipbook.py:
book 16/14 (16/18 on phones under 700px), swipe/tap/keys/buttons,
day tag line as the only day label, no "Day X of 13" footer on day
pages. Unlike the image flipbook this file is NOT offline: videos,
narration and music stream from jsDelivr, so it needs the internet.

Usage (from this folder):
    python3 build_video_flipbook.py

Output: highlights-of-eastern-europe-video-flipbook.html (small, about
100 KB). Publish through the GitHub repo like the image flipbook:
    git add highlights-of-eastern-europe-video-flipbook.html audio/
    git commit -m "Video flipbook: ..."
    git push origin master:main
    git push origin master
The narration slices in audio/ must be pushed too, or their jsDelivr
URLs 404. The day videos were pushed with the Vercel video update
(commit 83aad6d); jsDelivr @main can lag a new commit by minutes.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "highlights-of-eastern-europe-video-flipbook.html"
CDN = "https://cdn.jsdelivr.net/gh/tjiufamily/travel-toons@main"
SRT = Path.home() / "workspace/gemini-gems/travel-toon-narrator/subtitles-continuous-narration.srt"


def parse_srt(path):
    """Return {day_number: cue text} for cues 2-14 (Days 1-13)."""
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(
        r"(\d+)\n\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d\n(.*?)(?=\n\n|\Z)",
        text, re.S)
    cues = {}
    for num, body in blocks:
        n = int(num)
        if 2 <= n <= 14:
            lines = [ln.strip() for ln in body.strip().split("\n") if ln.strip()]
            cues[n - 1] = "<br>".join(html.escape(ln) for ln in lines)
    return cues


def main():
    data = json.loads((ROOT / "trips.json").read_text())
    trip = data["trips"][0]
    days = [d for d in trip["days"] if d.get("image") and d.get("video")]
    if len(days) != 13:
        raise SystemExit("expected 13 days with image and video, got %d" % len(days))
    cues = parse_srt(SRT)
    if len(cues) != 13:
        raise SystemExit("expected 13 day cues in the SRT, got %d" % len(cues))

    pages = []
    cover = (
        '<div class="page cover" data-i="0">'
        '<p class="cover-eyebrow">A travel toon journey</p>'
        '<h1>' + html.escape(trip["title"]) + '</h1>'
        '<p class="cover-sub">' + html.escape(trip.get("subtitle", "")) + '</p>'
        '<p class="cover-dates">' + html.escape(trip["dates"]) + '</p>'
        '<p class="cover-ded">' + html.escape(trip["dedication"]) + '</p>'
        '<p class="cover-now">Now playing: Across the Cobbled Square &mdash; Theme song</p>'
        '<p class="cover-hint">Tap or swipe to begin &rsaquo;</p></div>'
    )
    pages.append(cover)
    intro = (data.get("dedicationIntro") or "").strip()
    paras = [p.strip() for p in intro.split("\n") if p.strip()] or [intro]
    ded_html = "".join("<p>" + html.escape(p) + "</p>" for p in paras)
    pages.append(
        '<div class="page dedication" data-i="1">'
        '<h2>For Christmin</h2>'
        '<div class="ded-text">' + ded_html + '</div>'
        '<p class="page-num">Dedication</p>'
        '</div>'
    )
    for n, d in enumerate(days):
        i = n + 2
        day = d["day"]
        video_url = CDN + "/" + d["video"]
        poster_url = CDN + "/" + d["image"]
        narr_url = CDN + "/audio/narration-day-%02d.mp3" % day
        pages.append(
            '<div class="page day" data-i="' + str(i) + '">'
            '<div class="video-wrap">'
            '<video class="day-video" controls playsinline preload="metadata" poster="' + poster_url + '">'
            '<source src="' + video_url + '" type="video/mp4">'
            '</video>'
            '</div>'
            '<div class="subtitle-overlay">' + cues[day] + '</div>'
            '<audio class="day-narr" preload="none" src="' + narr_url + '"></audio>'
            '<div class="day-cap">'
            '<p class="day-tag">Day ' + str(day) + ' of 13 &middot; ' + html.escape(d["date"]) + ' &middot; ' + html.escape(d["place"]) + '</p>'
            '<h3>' + html.escape(d["title"]) + '</h3>'
            '<p>' + html.escape(d["blurb"]) + '</p>'
            '<p class="watch-note">Tap &#9654; on the video to watch this day move, with its narration.</p>'
            '</div>'
            '</div>'
        )

    pages_html = "\n".join(pages)
    total = len(pages)

    doc = TEMPLATE
    doc = doc.replace("__TITLE__", html.escape(trip["title"]))
    doc = doc.replace("__DATES__", html.escape(trip["dates"]))
    doc = doc.replace("__DEDICATION__", html.escape(trip["dedication"]))
    doc = doc.replace("__PAGES__", pages_html)
    doc = doc.replace("__TOTAL__", str(total))
    doc = doc.replace("__DAYS_INCLUDED__", str(len(days)))
    doc = doc.replace("__THEME_URL__", CDN + "/" + trip["themeSong"]["file"])

    OUT.write_text(doc, encoding="utf-8")
    size = OUT.stat().st_size
    print("wrote", OUT.name)
    print("days included:", len(days), "(Days " + str(days[0]["day"]) + "–" + str(days[-1]["day"]) + ")")
    print("pages:", total, "(cover + dedication + 13 days)")
    print("size: %d bytes (%.1f KB)" % (size, size / 1024))


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>__TITLE__ — Video Flipbook</title>
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
.cover-now{margin-top:14px;color:var(--gold-soft);font-size:.9rem;letter-spacing:.06em}
.cover-hint{margin-top:26px;color:var(--gold-soft);letter-spacing:.18em;text-transform:uppercase;font-size:.8rem}
.page.dedication h2{font-size:clamp(1.6rem,4vw,2.2rem);margin-bottom:16px}
.ded-text{font-family:var(--serif);font-size:clamp(1rem,2.2vw,1.2rem);line-height:1.85;color:#f7ead0;max-width:640px;text-align:left;overflow-y:auto}
.ded-text p{margin-bottom:14px}
.video-wrap{position:relative;flex:0 0 auto;background:#000}
.page.day video.day-video{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;background:#000}
.subtitle-overlay{display:none;margin:10px 16px 0;background:rgba(0,0,0,.75);color:#fff;padding:8px 12px;border-radius:8px;font-size:.95rem;line-height:1.45;text-align:center}
.subtitle-overlay.show{display:block}
.day-cap{flex:1 1 auto;min-height:0;padding:16px 20px 14px;overflow-y:auto}
@media (max-width:700px){.book{aspect-ratio:16/18}.day-cap{padding:12px 16px 16px}.day-cap h3{font-size:1.25rem}.subtitle-overlay{font-size:.85rem;margin:8px 12px 0}}
.day-tag{color:var(--gold-soft);font-size:.78rem;letter-spacing:.14em;text-transform:uppercase}
.day-cap h3{font-size:clamp(1.3rem,3.4vw,1.8rem);margin:4px 0 6px}
.day-cap p{color:var(--ink-dim)}
.watch-note{margin-top:10px;font-size:.88rem;color:var(--gold-soft)}
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
  <p class="now"><b>Now playing:</b> <span id="nowPlaying">Across the Cobbled Square &mdash; Theme song for the trip</span></p>
  <p><button class="track-btn" id="musicFab" type="button">Pause music</button></p>
  <p class="hint">The theme song plays when the flipbook opens. When you play a day&rsquo;s video, the theme pauses and that day&rsquo;s narration plays instead, then the theme comes back. This flipbook streams its videos, narration and music from the web, so it needs an internet connection.</p>
</div>

<audio id="themeAudio" loop preload="auto" src="__THEME_URL__"></audio>

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
  stopAllDayMedia();
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
  if (e.target.closest('video') || e.target.closest('.day-cap')) return;
  var r = book.getBoundingClientRect();
  var x = e.clientX - r.left;
  if (x > r.width * 0.72) go(cur + 1);
  else if (x < r.width * 0.28) go(cur - 1);
});
render();

/* Theme song only, default ON. The theme pauses while a day video
   plays, and comes back when the video ends, only if the user had
   it on (userMusicOn). */
var theme = document.getElementById('themeAudio');
var fab = document.getElementById('musicFab');
var userMusicOn = true;
var dayVideos = Array.prototype.slice.call(document.querySelectorAll('.day-video'));
var dayNarrs = Array.prototype.slice.call(document.querySelectorAll('.day-narr'));
var daySubs = Array.prototype.slice.call(document.querySelectorAll('.subtitle-overlay'));
function anyVideoPlaying(){
  for (var i = 0; i < dayVideos.length; i++){
    if (!dayVideos[i].paused && !dayVideos[i].ended) return true;
  }
  return false;
}
function anyNarrationPlaying(){
  for (var i = 0; i < dayNarrs.length; i++){
    if (!dayNarrs[i].paused && !dayNarrs[i].ended) return true;
  }
  return false;
}
function maybeResumeTheme(){
  if (userMusicOn && !anyVideoPlaying() && !anyNarrationPlaying()){
    theme.play().then(function(){
      fab.textContent = 'Pause music';
    }).catch(function(){});
  }
}
function stopAllDayMedia(){
  dayVideos.forEach(function(v){ if (!v.paused) v.pause(); });
  dayNarrs.forEach(function(a){ if (!a.paused) a.pause(); });
  daySubs.forEach(function(s){ s.classList.remove('show'); });
  maybeResumeTheme();
}
dayVideos.forEach(function(v, i){
  var a = dayNarrs[i], sub = daySubs[i];
  v.addEventListener('play', function(){
    if (!theme.paused) theme.pause();
    a.currentTime = 0;
    a.play().catch(function(){});
    sub.classList.add('show');
  });
  v.addEventListener('pause', function(){
    if (v.ended) return;
    a.pause();
    sub.classList.remove('show');
    maybeResumeTheme();
  });
  v.addEventListener('ended', function(){
    /* The narration can run up to 0.7s past the 10-second clip; let
       its tail finish, and its own ended handler brings the theme
       back. If the narration already ended, bring the theme back now. */
    if (a.ended || a.paused){
      sub.classList.remove('show');
      maybeResumeTheme();
    }
  });
  a.addEventListener('ended', function(){
    sub.classList.remove('show');
    maybeResumeTheme();
  });
});
fab.onclick = function(){
  userMusicOn = !userMusicOn;
  if (userMusicOn){
    maybeResumeTheme();
    fab.textContent = 'Pause music';
  } else {
    theme.pause();
    fab.textContent = 'Play theme song';
  }
};
/* Theme song starts on load; if the browser blocks autoplay, the
   button offers a tap to start it. */
theme.play().then(function(){
  fab.textContent = 'Pause music';
}).catch(function(){
  fab.textContent = 'Tap to play theme song';
});
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
