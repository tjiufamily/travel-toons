# Travel Toons — our cartoon trips

Live page: https://travel-toons-tjiufamilys-projects.vercel.app/
Pictures and music: https://github.com/tjiufamily/travel-toons

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
   automatically once the picture is added. Do not touch the site
   hero (`images/hero.jpg`) — it is the same for every trip, and each
   trip's own cover is its own Day 1 picture.
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
  only file you need to edit to add a trip or a day. It is a list of
  trips (an array), so the site is built for many trips, not just one:
  each trip has its own name, dates, dedication, cover (its own Day 1),
  music and days. The page currently shows the first trip in the list;
  when a second trip is added, the home page will need a trip list so
  visitors can choose a trip — the data is ready, the chooser is not
  built yet.
- `images/hero.jpg` — the generic site hero at the top of the page: a
  travelling couple looking over a golden valley at sunset. It belongs
  to the whole site, not to any one trip, and it never changes when a
  new trip is added. It was drawn for this site (not a photo, no credit
  needed). A trip's own cover is its own Day 1 picture, shown in the
  carousel, not here.
- `images/` — the web-sized cartoon pictures and their small previews.
  These live in the GitHub repo too and are served to the page through
  the jsDelivr CDN (see the `CDN` line at the top of `index.html`),
  because Vercel's file-upload path cannot take single files over
  about 95 KB. Nothing to do — it just works.
- `music/` — the song for each trip. Eastern Europe uses "My Perfect
  Valentine", written and sung by James for Christmin (a family
  original, `music/my-perfect-valentine.mp3`).
- `deploy.py` — publishes the folder to Vercel.
- `.project.json` — created automatically the first time you publish;
  it remembers which Vercel project this is. Do not delete it.

## Password protection (same as Cornerstone)

The page is family-only, with the same sign-in as Cornerstone: the family
email (`tjiunardi.family@gmail.com`) plus the same family password.
The gate works exactly like Cornerstone's: `api/login.js` checks the
password against a salted scrypt hash in the `TRAVEL_TOONS_PASSWORD_HASH`
environment variable, sets a signed 90-day cookie, and the trip data is
served only to a signed-in session via `api/trip.js` (so `trips.json`
itself is never published as a file). The password and its hash are
never written into any file.

To set the secrets on Vercel (one-off, after a fresh project): run
`python3 set_env.py` in this folder and type the family password when
asked. It hashes the password and creates both
`TRAVEL_TOONS_PASSWORD_HASH` and `TRAVEL_TOONS_SESSION_SECRET` as
sensitive production env vars. Then redeploy.

Note: the cartoon pictures and the music are still served from the
public GitHub repo through the jsDelivr CDN, so anyone who already
knows a direct picture or music link can open that single file. The
page itself — the trip, the dedication, the carousel — is behind the
sign-in. Moving the pictures behind the sign-in too would mean moving
them off the public repo into protected storage; that is a separate job.

## Editing trips.json

`trips.json` is the local source of truth, but it is no longer deployed
as a file. After editing it, run `python3 regen_trip.py` (it embeds the
JSON into `api/trip.js`), then run `python3 deploy.py` as usual.

## Notes

- The page is family-only, with no data collected.
- Install icon: `manifest.json` (name "Travel Toons", theme colour
  `#0d0b09`) plus `images/icon-192.png`, `images/icon-512.png`, a
  maskable `images/icon-maskable-512.png` and
  `images/apple-touch-icon.png`, all cropped from the generic hero
  artwork. The icons live in the GitHub repo and are served through
  the jsDelivr CDN, like the other pictures.
- Music: two tracks. The Chopin waltz AUTOPLAYS when the page opens,
  after sign-in (James's word, 5 Nov 2026: "I want Chopin to auto
  play"). "My Perfect Valentine" never autoplays — it plays only when
  the listener taps its track button. The floating button plays or
  pauses whichever track is current, and its label names that track.
  If a browser blocks the autoplay, the button offers a tap to start
  the Chopin instead.
- The original full-size cartoons stay in
  `~/workspace/gemini-gems/travel-toon-director/images/` and are
  not published here; only the smaller web copies are.
