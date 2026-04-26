const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const { Pool } = require("pg");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 4002;

const pool = new Pool({
  connectionString:
    process.env.DATABASE_URL ||
    "postgres://boutique:boutique@postgres-service:5432/boutiquedb"
});

const seedProducts = [
  {
    name: "Silk Evening Dress",
    category: "dresses",
    description: "Elegant silk evening dress for special occasions.",
    price: 129.99,
    image_url: "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446"
  },
  {
    name: "Leather Handbag",
    category: "handbags",
    description: "Premium leather handbag with minimalist design.",
    price: 89.5,
    image_url: "https://images.unsplash.com/photo-1594223274512-ad4803739b7c"
  },
  {
    name: "Classic Heels",
    category: "shoes",
    description: "Comfortable and stylish classic heels.",
    price: 69.0,
    image_url: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2"
  },
  {
    name: "Hydrating Serum",
    category: "skincare",
    description: "Daily hydrating serum for glowing skin.",
    price: 39.99,
    image_url: "https://images.unsplash.com/photo-1556228578-8c89e6adf883"
  },
  {
    name: "Gold Necklace",
    category: "accessories",
    description: "Delicate gold necklace for everyday style.",
    price: 54.95,
    image_url: "https://images.unsplash.com/photo-1611085583191-a3b181a88401"
  },
  {
    name: "Bracelet Kit Deals",
    category: "bracelet-accessories",
    description: "All-in-one starter kit with colorful beads and tools.",
    price: 24.99,
    image_url: "https://picsum.photos/seed/bracelet-kit-deals/600/600"
  },
  {
    name: "Alphabets",
    category: "bracelet-accessories",
    description: "Alphabet beads for custom name and message bracelets.",
    price: 7.99,
    image_url: "https://picsum.photos/seed/alphabet-beads/600/600"
  },
  {
    name: "Charms",
    category: "bracelet-accessories",
    description: "Cute charm pieces to personalize every bracelet design.",
    price: 6.49,
    image_url: "https://picsum.photos/seed/bracelet-charms/600/600"
  },
  {
    name: "Stainless Steel Permanent Chain Collection",
    category: "bracelet-accessories",
    description: "Durable stainless steel chains for long-lasting jewelry.",
    price: 14.99,
    image_url: "https://picsum.photos/seed/steel-chain-collection/600/600"
  },
  {
    name: "Ready Loreal Crystal 4mm",
    category: "bracelet-accessories",
    description: "Ready-to-use crystal beads in a versatile 4mm size.",
    price: 9.99,
    image_url: "https://picsum.photos/seed/ready-loreal-crystal-4mm/600/600"
  },
  {
    name: "Crystal Beads 4mm",
    category: "bracelet-accessories",
    description: "Bright crystal bead strand ideal for delicate bracelets.",
    price: 8.49,
    image_url: "https://picsum.photos/seed/crystal-beads-4mm/600/600"
  },
  {
    name: "Jewelry Accessories",
    category: "bracelet-accessories",
    description: "Essential findings and connectors for jewelry making.",
    price: 11.25,
    image_url: "https://picsum.photos/seed/jewelry-accessories/600/600"
  },
  {
    name: "Organizer Box",
    category: "bracelet-accessories",
    description: "Multi-compartment organizer box for neat storage.",
    price: 5.99,
    image_url: "https://picsum.photos/seed/organizer-box/600/600"
  },
  {
    name: "Magnet Charms Collection",
    category: "bracelet-accessories",
    description: "Magnetic charm set with playful themed pieces.",
    price: 10.5,
    image_url: "https://picsum.photos/seed/magnet-charms-collection/600/600"
  },
  {
    name: "Crystal Glass 6mm",
    category: "bracelet-accessories",
    description: "6mm crystal glass bead strands with high shine finish.",
    price: 12.99,
    image_url: "https://picsum.photos/seed/crystal-glass-6mm/600/600"
  },
  {
    name: "Double Tune",
    category: "bracelet-accessories",
    description: "Double tone floral beads for colorful bracelet accents.",
    price: 6.99,
    image_url: "https://picsum.photos/seed/double-tune-beads/600/600"
  },
  {
    name: "Metal Charms",
    category: "bracelet-accessories",
    description: "Detailed metal charms to elevate handmade jewelry.",
    price: 9.49,
    image_url: "https://picsum.photos/seed/metal-charms/600/600"
  },
  {
    name: "Crystal Glass 8mm",
    category: "bracelet-accessories",
    description: "Larger 8mm crystal beads for statement bracelet patterns.",
    price: 13.49,
    image_url: "https://picsum.photos/seed/crystal-glass-8mm/600/600"
  },
  {
    name: "Matte Plastic Beads",
    category: "bracelet-accessories",
    description: "Soft matte pastel beads for modern bracelet looks.",
    price: 7.25,
    image_url: "https://picsum.photos/seed/matte-plastic-beads/600/600"
  },
  {
    name: "Opic Multicolor Beads",
    category: "bracelet-accessories",
    description: "Multicolor round beads perfect for playful designs.",
    price: 8.75,
    image_url: "https://picsum.photos/seed/opic-multicolor-beads/600/600"
  },
  {
    name: "Kancha Glass Collection",
    category: "bracelet-accessories",
    description: "Glossy kancha style glass beads for premium finish.",
    price: 10.99,
    image_url: "https://picsum.photos/seed/kancha-glass-collection/600/600"
  },
  {
    name: "Green Pearl Collection",
    category: "bracelet-accessories",
    description: "Fresh green and white pearl mix for elegant sets.",
    price: 9.25,
    image_url: "https://picsum.photos/seed/green-pearl-collection/600/600"
  },
  {
    name: "Lavender Pearl Collection",
    category: "bracelet-accessories",
    description: "Lavender pearl strands for soft and dreamy styles.",
    price: 9.25,
    image_url: "https://picsum.photos/seed/lavender-pearl-collection/600/600"
  },
  {
    name: "Ruby Glass Collection",
    category: "bracelet-accessories",
    description: "Deep ruby glass beads for rich contrast designs.",
    price: 10.25,
    image_url: "https://picsum.photos/seed/ruby-glass-collection/600/600"
  },
  {
    name: "Red Pearl Collection",
    category: "bracelet-accessories",
    description: "Red and white pearl strands for festive pieces.",
    price: 9.99,
    image_url: "https://picsum.photos/seed/red-pearl-collection/600/600"
  },
  {
    name: "Candy Mix Collection",
    category: "bracelet-accessories",
    description: "Candy color mix beads to create vibrant bracelets.",
    price: 8.99,
    image_url: "https://picsum.photos/seed/candy-mix-collection/600/600"
  },
  {
    name: "Violet Pearl Collection",
    category: "bracelet-accessories",
    description: "Violet pearl strands for a soft pastel finish.",
    price: 9.49,
    image_url: "https://picsum.photos/seed/violet-pearl-collection/600/600"
  },
  {
    name: "Sunflower Yellow Collection",
    category: "bracelet-accessories",
    description: "Sunny yellow beads that brighten every bracelet set.",
    price: 8.75,
    image_url: "https://picsum.photos/seed/sunflower-yellow-collection/600/600"
  },
  {
    name: "Pearl White Collection",
    category: "bracelet-accessories",
    description: "Classic pearl white strands for timeless jewelry.",
    price: 9.99,
    image_url: "https://picsum.photos/seed/pearl-white-collection/600/600"
  }
];

async function init() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS products (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      description TEXT NOT NULL,
      price NUMERIC(10, 2) NOT NULL,
      image_url TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  await pool.query("CREATE UNIQUE INDEX IF NOT EXISTS products_name_unique ON products(name);");

  for (const product of seedProducts) {
    await pool.query(
      `
        INSERT INTO products(name, category, description, price, image_url)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (name)
        DO UPDATE SET
          category = EXCLUDED.category,
          description = EXCLUDED.description,
          price = EXCLUDED.price,
          image_url = EXCLUDED.image_url;
      `,
      [product.name, product.category, product.description, product.price, product.image_url]
    );
  }
}

app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "product-service" });
});

app.get("/products", async (req, res) => {
  try {
    const { category } = req.query;

    if (category) {
      const result = await pool.query("SELECT * FROM products WHERE category = $1 ORDER BY id", [category]);
      return res.json(result.rows);
    }

    const result = await pool.query("SELECT * FROM products ORDER BY id");
    return res.json(result.rows);
  } catch (error) {
    return res.status(500).json({ message: "failed to fetch products", error: error.message });
  }
});

app.get("/products/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query("SELECT * FROM products WHERE id = $1", [id]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: "product not found" });
    }

    return res.json(result.rows[0]);
  } catch (error) {
    return res.status(500).json({ message: "failed to fetch product", error: error.message });
  }
});

init()
  .then(() => {
    app.listen(port, () => {
      console.log(`Product service is running on port ${port}`);
    });
  })
  .catch((error) => {
    console.error("Failed to initialize product service", error);
    process.exit(1);
  });
