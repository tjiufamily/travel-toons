// Temporary guest pass-through: open the page without a password.
// James asked 5 Nov 2026 to leave the guest button on for 48 hours;
// remove this file and its button from index.html ONLY when he says to.
// Each tap signs in for 24 hours; the 24-hour window is not to be
// extended without his word.
const lib = require("./_lib");

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.status(405).json({ ok: false, error: "Method not allowed" }); return; }
  const session = lib.signSession(lib.ALLOWLIST[0], 24 * 60 * 60);
  res.setHeader("Set-Cookie", lib.COOKIE + "=" + session + "; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=86400");
  res.status(200).json({ ok: true });
};
