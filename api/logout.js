const lib = require("./_lib");

module.exports = (req, res) => {
  res.setHeader("Set-Cookie", lib.COOKIE + "=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0");
  res.status(200).json({ ok: true });
};
