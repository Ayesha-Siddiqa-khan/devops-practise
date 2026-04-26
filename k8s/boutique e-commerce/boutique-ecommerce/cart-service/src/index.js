const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const { Pool } = require("pg");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 4003;

const pool = new Pool({
  connectionString:
    process.env.DATABASE_URL ||
    "postgres://boutique:boutique@postgres-service:5432/boutiquedb"
});

async function init() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS cart_items (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      product_name TEXT NOT NULL,
      price NUMERIC(10, 2) NOT NULL,
      quantity INTEGER NOT NULL DEFAULT 1,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);
}

app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "cart-service" });
});

app.get("/cart/:userId", async (req, res) => {
  try {
    const { userId } = req.params;
    const result = await pool.query("SELECT * FROM cart_items WHERE user_id = $1 ORDER BY id", [userId]);
    return res.json(result.rows);
  } catch (error) {
    return res.status(500).json({ message: "failed to fetch cart", error: error.message });
  }
});

app.post("/cart", async (req, res) => {
  try {
    const { userId, productId, productName, price, quantity } = req.body;

    if (!userId || !productId || !productName || !price) {
      return res.status(400).json({ message: "missing cart fields" });
    }

    const itemQuantity = quantity || 1;

    const existing = await pool.query(
      "SELECT * FROM cart_items WHERE user_id = $1 AND product_id = $2",
      [userId, productId]
    );

    if (existing.rows.length > 0) {
      const updated = await pool.query(
        "UPDATE cart_items SET quantity = quantity + $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 RETURNING *",
        [itemQuantity, existing.rows[0].id]
      );
      return res.status(200).json(updated.rows[0]);
    }

    const result = await pool.query(
      "INSERT INTO cart_items(user_id, product_id, product_name, price, quantity) VALUES($1, $2, $3, $4, $5) RETURNING *",
      [userId, productId, productName, price, itemQuantity]
    );

    return res.status(201).json(result.rows[0]);
  } catch (error) {
    return res.status(500).json({ message: "failed to add item", error: error.message });
  }
});

app.put("/cart/:itemId", async (req, res) => {
  try {
    const { itemId } = req.params;
    const { quantity } = req.body;

    if (!quantity || quantity < 1) {
      return res.status(400).json({ message: "quantity must be greater than zero" });
    }

    const result = await pool.query(
      "UPDATE cart_items SET quantity = $1, updated_at = CURRENT_TIMESTAMP WHERE id = $2 RETURNING *",
      [quantity, itemId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "cart item not found" });
    }

    return res.json(result.rows[0]);
  } catch (error) {
    return res.status(500).json({ message: "failed to update item", error: error.message });
  }
});

app.delete("/cart/:itemId", async (req, res) => {
  try {
    const { itemId } = req.params;

    const result = await pool.query("DELETE FROM cart_items WHERE id = $1 RETURNING *", [itemId]);
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "cart item not found" });
    }

    return res.json({ message: "item removed" });
  } catch (error) {
    return res.status(500).json({ message: "failed to remove item", error: error.message });
  }
});

app.delete("/cart/user/:userId", async (req, res) => {
  try {
    const { userId } = req.params;
    await pool.query("DELETE FROM cart_items WHERE user_id = $1", [userId]);
    return res.json({ message: "cart cleared" });
  } catch (error) {
    return res.status(500).json({ message: "failed to clear cart", error: error.message });
  }
});

init()
  .then(() => {
    app.listen(port, () => {
      console.log(`Cart service is running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to initialize cart service", error);
    process.exit(1);
  });
