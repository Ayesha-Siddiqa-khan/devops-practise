const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const { Pool } = require("pg");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 4004;

const paymentServiceUrl = process.env.PAYMENT_SERVICE_URL || "http://payment-service:4006";

const pool = new Pool({
  connectionString:
    process.env.DATABASE_URL ||
    "postgres://boutique:boutique@postgres-service:5432/boutiquedb"
});

async function init() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS orders (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL,
      items JSONB NOT NULL,
      total_amount NUMERIC(10, 2) NOT NULL,
      payment_status TEXT NOT NULL,
      order_status TEXT NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);
}

app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "order-service" });
});

app.post("/orders/place", async (req, res) => {
  try {
    const { userId, items, totalAmount, paymentMethod } = req.body;

    if (!userId || !Array.isArray(items) || items.length === 0 || !totalAmount) {
      return res.status(400).json({ message: "invalid order payload" });
    }

    const paymentResponse = await fetch(`${paymentServiceUrl}/payments/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        userId,
        amount: totalAmount,
        paymentMethod: paymentMethod || "card"
      })
    });

    const paymentResult = await paymentResponse.json();

    if (!paymentResult.success) {
      return res.status(402).json({ message: "payment failed", payment: paymentResult });
    }

    const result = await pool.query(
      "INSERT INTO orders(user_id, items, total_amount, payment_status, order_status) VALUES($1, $2::jsonb, $3, $4, $5) RETURNING *",
      [userId, JSON.stringify(items), totalAmount, "paid", "placed"]
    );

    return res.status(201).json(result.rows[0]);
  } catch (error) {
    return res.status(500).json({ message: "failed to place order", error: error.message });
  }
});

app.get("/orders/:userId", async (req, res) => {
  try {
    const { userId } = req.params;

    const result = await pool.query(
      "SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC",
      [userId]
    );

    return res.json(result.rows);
  } catch (error) {
    return res.status(500).json({ message: "failed to fetch orders", error: error.message });
  }
});

init()
  .then(() => {
    app.listen(port, () => {
      console.log(`Order service is running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to initialize order service", error);
    process.exit(1);
  });
