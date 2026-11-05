# Travel Toons — our cartoon trips

A beautiful page that shows our travel cartoons, one trip at a time.
The first trip on it is **Highlights of Eastern Europe** (November 2026).

## How to add a new trip (no coding needed)

1. **Make the cartoon pictures** for the new trip, one picture per day,
   landscape (wide) pictures, just like the Eastern Europe ones.
2. **Shrink them for the web.** Open each picture and save a smaller copy:
   about 1600 pixels wide, JPEG quality around 80. (The originals are
   about 3 MB each — too big for a fast page. The copies on this site
   are about 300 KB each.) Put the small copies in a new folder, for
   example `images/victoria-falls/day-01.jpg`, `day-02.jpg`, and so on.
   Small preview copies (480 pixels wide) go in `images/victoria-falls/thumbs/`.
3. **Add one entry to `trips.json`.** Open `trips.json` and copy the
   Eastern Europe entry. Change the trip name, dates, dedication,
   cover picture, music file, and the list of days. For any day whose
   cartoon is not ready yet, write `"image": null` — the page will
   show a pretty "Coming soon" card for that day, and it will fill in
   automatically once the picture is added.
4. **Music (optional).** If the new trip needs its own song, put the
   MP3 file in the `music/` folder and name it in the trip's entry.
   Only use music that is free to use — for example a public-domain
   classical recording from Musopen, or a track from Pixabay Music.
   Write the track name, performer and licence in the entry so the
   credit shows on the page.
5. **Publish.** Run `python3 deploy.py` from this folder. That is all —
   the live page updates. Nothing else needs changing.

## How to finish Days 7–13 of Eastern Europe

Same as above, but even simpler: when a new day's cartoon is ready,
save its small web copy as `images/day-07.jpg` (and a 480-pixel copy
in `images/thumbs/day-07.jpg`), then change that day's entry in
`trips.json` from `"image": null` to `"image": "images/day-07.jpg"`
(and the same for `"thumb"`), and run `python3 deploy.py`.
The design does not change at all.

## What is in this folder

- `index.html` — the page itself (the design, the swipe carousel, the music button).
- `trips.json` — all the words and pictures for every trip. This is the
  only file you need to edit to add a trip or a day.
- `images/` — the web-sized cartoon pictures and their small previews.
  These live in the GitHub repo too and are served to the page through
  the jsDelivr CDN (see the `CDN` line at the top of `index.html`),
  because Vercel's file-upload path cannot take single files over
  about 95 KB. Nothing to do — it just works.
- `music/` — the song for each trip. Eastern Europe uses Chopin's
  Waltz in C-sharp minor, Op. 64 No. 2, performed by Aaron Dunn
  (Musopen, public domain — CC0 1.0).
- `deploy.py` — publishes the folder to Vercel.
- `.project.json` — created automatically the first time you publish;
  it remembers which Vercel project this is. Do not delete it.

## Notes

- The page is public, with no sign-in and no data collected.
- The music never plays by itself — visitors tap the music button.
- The original full-size cartoons stay in
  `~/workspace/gemini-gems/travel-toon-director/images/` and are
  not published here; only the smaller web copies are.
