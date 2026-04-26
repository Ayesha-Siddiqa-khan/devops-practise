const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const { Pool } = require("pg");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 4005;

const pool = new Pool({
  connectionString:
    process.env.DATABASE_URL ||
    "postgres://boutique:boutique@postgres-service:5432/boutiquedb"
});

async function init() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS user_profiles (
      id SERIAL PRIMARY KEY,
      user_id INTEGER UNIQUE NOT NULL,
      full_name TEXT,
      phone TEXT,
      shipping_address TEXT,
      city TEXT,
      country TEXT,
      postal_code TEXT,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);
}

app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "user-service" });
});

app.get("/users/:userId/profile", async (req, res) => {
  try {
    const { userId } = req.params;
    const result = await pool.query("SELECT * FROM user_profiles WHERE user_id = $1", [userId]);

    if (result.rows.length === 0) {
      return res.json({
        user_id: Number(userId),
        full_name: "",
        phone: "",
        shipping_address: "",
        city: "",
        country: "",
        postal_code: ""
      });
    }

    return res.json(result.rows[0]);
  } catch (error) {
    return res.status(500).json({ message: "failed to fetch profile", error: error.message });
  }
});

app.put("/users/:userId/profile", async (req, res) => {
  try {
    const { userId } = req.params;
    const { fullName, phone } = req.body;

    const result = await pool.query(
      `
      INSERT INTO user_profiles(user_id, full_name, phone)
      VALUES($1, $2, $3)
      ON CONFLICT (user_id)
      DO UPDATE SET
        full_name = EXCLUDED.full_name,
        phone = EXCLUDED.phone,
        updated_at = CURRENT_TIMESTAMP
      RETURNING *
      `,
      [userId, fullName || "", phone || ""]
    );

    return res.json(result.rows[0]);
  } catch (error) {
    return res.status(500).json({ message: "failed to update profile", error: error.message });
  }
});

app.put("/users/:userId/address", async (req, res) => {
  try {
    const { userId } = req.params;
    const { shippingAddress, city, country, postalCode } = req.body;

    const result = await pool.query(
      `
      INSERT INTO user_profiles(user_id, shipping_address, city, country, postal_code)
      VALUES($1, $2, $3, $4, $5)
      ON CONFLICT (user_id)
      DO UPDATE SET
        shipping_address = EXCLUDED.shipping_address,
        city = EXCLUDED.city,
        country = EXCLUDED.country,
        postal_code = EXCLUDED.postal_code,
        updated_at = CURRENT_TIMESTAMP
      RETURNING *
      `,
      [userId, shippingAddress || "", city || "", country || "", postalCode || ""]
    );

    return res.json(result.rows[0]);
  } catch (error) {
    return res.status(500).json({ message: "failed to update address", error: error.message });
  }
});

app.get("/users/:userId/address", async (req, res) => {
  try {
    const { userId } = req.params;
    const result = await pool.query(
      "SELECT shipping_address, city, country, postal_code FROM user_profiles WHERE user_id = $1",
      [userId]
    );

    if (result.rows.length === 0) {
      return res.json({
        shipping_address: "",
        city: "",
        country: "",
        postal_code: ""
      });
    }

    return res.json(result.rows[0]);
  } catch (error) {
    return res.status(500).json({ message: "failed to fetch address", error: error.message });
  }
});

init()
  .then(() => {
    app.listen(port, () => {
      console.log(`User service is running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to initialize user service", error);
    process.exit(1);
  });
