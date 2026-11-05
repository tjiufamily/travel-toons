const lib = require("./_lib");

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.status(405).json({ ok: false, error: "Method not allowed" }); return; }
  let body = req.body;
  if (typeof body === "string") { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  body = body || {};
  const email = String(body.email || "").trim().toLowerCase();
  const password = String(body.password || "");
  const stored = process.env.TRAVEL_TOONS_PASSWORD_HASH || "";
  const allowed = lib.ALLOWLIST.indexOf(email) >= 0;
  const ok = allowed && lib.verifyPassword(password, stored);
  if (!ok) {
    await new Promise(r => setTimeout(r, 600));
    res.status(401).json({ ok: false, error: "That email and password do not match our family login. Please check and try again." });
    return;
  }
  const session = lib.signSession(email);
  res.setHeader("Set-Cookie", lib.COOKIE + "=" + session + "; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=" + lib.MAX_AGE);
  res.status(200).json({ ok: true, email });
};
