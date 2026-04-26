import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

function HomePage() {
  const [featuredProducts, setFeaturedProducts] = useState([]);

  useEffect(() => {
    api
      .products()
      .then((data) => {
        setFeaturedProducts(data.slice(0, 6));
      })
      .catch(() => {
        setFeaturedProducts([]);
      });
  }, []);

  return (
    <section className="home-layout">
      <div className="hero">
        <div className="hero-copy">
          <span className="badge">New Season Collection</span>
          <h2>Boutique style, delivered to your doorstep.</h2>
          <p>
            Explore premium dresses, handbags, shoes, skincare and accessories crafted for modern everyday luxury.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="primary-btn">
              Shop Now
            </Link>
            <Link to="/cart" className="ghost-btn">
              View Cart ahmad
            </Link>
          </div>
          <div className="hero-metrics">
            <article>
              <strong>2K+</strong>
              <span>Monthly orders</span>
            </article>
            <article>
              <strong>24h</strong>
              <span>Fast dispatch</span>
            </article>
            <article>
              <strong>4.9/5</strong>
              <span>Customer rating</span>
            </article>
          </div>
        </div>
        <div className="hero-card">
          <h3>Top Categories</h3>
          <ul>
            <li>Dresses</li>
            <li>Handbags</li>
            <li>Shoes</li>
            <li>Skincare</li>
            <li>Accessories</li>
          </ul>
          <p className="muted">Handpicked drops refreshed every week.</p>
        </div>
      </div>

      <div className="section-head">
        <h2>Featured Products</h2>
        <p className="muted">Fresh picks from your latest catalog.</p>
      </div>

      <div className="grid home-grid">
        {featuredProducts.map((product) => (
          <article key={product.id} className="product-card">
            <img src={product.image_url} alt={product.name} />
            <div className="product-meta">
              <p className="category-pill">{product.category}</p>
              <h3>{product.name}</h3>
              <strong>${Number(product.price).toFixed(2)}</strong>
            </div>
            <Link className="link-btn" to={`/products/${product.id}`}>
              View Details
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}

export default HomePage;
