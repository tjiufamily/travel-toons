const lib = require("./_lib");

module.exports = (req, res) => {
  const email = lib.readSession(req);
  if (!email) { res.status(401).json({ ok: false, error: "Not signed in" }); return; }
  res.status(200).json({ ok: true, email });
};
