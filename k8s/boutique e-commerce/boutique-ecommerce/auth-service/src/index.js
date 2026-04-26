const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const { Pool } = require("pg");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 4001;
const jwtSecret = process.env.JWT_SECRET || "dev-secret";

const pool = new Pool({
  connectionString:
    process.env.DATABASE_URL ||
    "postgres://boutique:boutique@postgres-service:5432/boutiquedb"
});

async function init() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users_auth (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);
}

app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "auth-service" });
});

app.post("/auth/register", async (req, res) => {
  try {
    const { name, email, password } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ message: "name, email and password are required" });
    }

    const passwordHash = await bcrypt.hash(password, 10);

    const result = await pool.query(
      "INSERT INTO users_auth(name, email, password_hash) VALUES($1, $2, $3) RETURNING id, name, email",
      [name, email, passwordHash]
    );

    return res.status(201).json(result.rows[0]);
  } catch (error) {
    if (error.code === "23505") {
      return res.status(409).json({ message: "email already exists" });
    }
    return res.status(500).json({ message: "registration failed", error: error.message });
  }
});

app.post("/auth/login", async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: "email and password are required" });
    }

    const result = await pool.query("SELECT * FROM users_auth WHERE email = $1", [email]);
    const user = result.rows[0];

    if (!user) {
      return res.status(401).json({ message: "invalid credentials" });
    }

    const isValid = await bcrypt.compare(password, user.password_hash);
    if (!isValid) {
      return res.status(401).json({ message: "invalid credentials" });
    }

    const token = jwt.sign(
      {
        userId: user.id,
        email: user.email,
        name: user.name
      },
      jwtSecret,
      { expiresIn: "1h" }
    );

    return res.json({ token });
  } catch (error) {
    return res.status(500).json({ message: "login failed", error: error.message });
  }
});

app.get("/auth/verify", (req, res) => {
  try {
    const authHeader = req.headers.authorization || "";
    const token = authHeader.replace("Bearer ", "");

    if (!token) {
      return res.status(401).json({ message: "missing token" });
    }

    const decoded = jwt.verify(token, jwtSecret);
    return res.json({ valid: true, user: decoded });
  } catch (error) {
    return res.status(401).json({ valid: false, message: "invalid token" });
  }
});

init()
  .then(() => {
    app.listen(port, () => {
      console.log(`Auth service is running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to initialize auth service", error);
    process.exit(1);
  });
