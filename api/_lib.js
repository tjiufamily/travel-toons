// Travel Toons auth helpers. Mirrors Cornerstone's api/_lib.js exactly in
// mechanism: the password is only ever checked against a salted scrypt hash
// held in the TRAVEL_TOONS_PASSWORD_HASH environment variable, format
// "saltHex:hashHex". Sessions are HMAC-signed cookies, 90 days.
// The family password is the SAME one as Cornerstone; only the env var names
// differ (per-project). Never put the password or its hash in a file.
const crypto = require("crypto");

const ALLOWLIST = ["tjiunardi.family@gmail.com"];
const COOKIE = "tt_session";
const MAX_AGE = 90 * 24 * 60 * 60; // 90 days, in seconds

function hashPassword(password, saltHex) {
  const salt = saltHex ? Buffer.from(saltHex, "hex") : crypto.randomBytes(16);
  const hash = crypto.scryptSync(String(password), salt, 64);
  return salt.toString("hex") + ":" + hash.toString("hex");
}

function verifyPassword(password, stored) {
  if (!stored || stored.indexOf(":") < 0) return false;
  const parts = stored.split(":");
  const expected = Buffer.from(parts[1], "hex");
  const actual = crypto.scryptSync(String(password), Buffer.from(parts[0], "hex"), 64);
  return expected.length === actual.length && crypto.timingSafeEqual(expected, actual);
}

function signSession(email) {
  const payload = Buffer.from(JSON.stringify({ e: email, exp: Math.floor(Date.now() / 1000) + MAX_AGE })).toString("base64url");
  const sig = crypto.createHmac("sha256", process.env.TRAVEL_TOONS_SESSION_SECRET || "").update(payload).digest("base64url");
  return payload + "." + sig;
}

function readSession(req) {
  const secret = process.env.TRAVEL_TOONS_SESSION_SECRET;
  if (!secret) return null;
  const header = req.headers.cookie || "";
  const match = header.split(";").map(s => s.trim()).find(s => s.indexOf(COOKIE + "=") === 0);
  if (!match) return null;
  const value = match.slice(COOKIE.length + 1);
  const dot = value.lastIndexOf(".");
  if (dot < 0) return null;
  const payload = value.slice(0, dot), sig = value.slice(dot + 1);
  const expected = crypto.createHmac("sha256", secret).update(payload).digest("base64url");
  const a = Buffer.from(sig), b = Buffer.from(expected);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  try {
    const data = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    if (!data.exp || data.exp < Math.floor(Date.now() / 1000)) return null;
    if (ALLOWLIST.indexOf(String(data.e || "").toLowerCase()) < 0) return null;
    return data.e;
  } catch (e) { return null; }
}

module.exports = { ALLOWLIST, COOKIE, MAX_AGE, hashPassword, verifyPassword, signSession, readSession };
