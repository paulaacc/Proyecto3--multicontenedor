const express = require("express");
const { Pool } = require("pg");

const app = express();
const pool = new Pool({
  host: process.env.POSTGRES_HOST || "db",
  database: process.env.POSTGRES_DB,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  port: 5432,
});

async function ensureTable() {
  for (;;) {
    try {
      await pool.query(`CREATE TABLE IF NOT EXISTS votes (
        voter_id VARCHAR(64) PRIMARY KEY, vote VARCHAR(50) NOT NULL)`);
      console.log("[result] conectado a PostgreSQL");
      return;
    } catch (e) {
      console.log("[result] esperando PostgreSQL:", e.message);
      await new Promise((r) => setTimeout(r, 2000));
    }
  }
}

app.get("/api/results", async (_req, res) => {
  try {
    const { rows } = await pool.query(
      "SELECT vote, COUNT(*)::int AS total FROM votes GROUP BY vote");
    res.json(rows);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get("/health", (_req, res) => res.json({ status: "ok" }));
app.use(express.static("public"));

ensureTable().then(() => app.listen(80, () => console.log("[result] escuchando en :80")));
