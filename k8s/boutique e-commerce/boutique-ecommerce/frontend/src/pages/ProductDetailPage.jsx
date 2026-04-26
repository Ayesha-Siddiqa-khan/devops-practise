import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../api";

const USER_ID = 1;

function ProductDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .productById(id)
      .then((data) => setProduct(data))
      .catch((err) => setError(err.message));
  }, [id]);

  const handleAdd = async () => {
    if (!product) {
      return;
    }

    try {
      await api.addToCart({
        userId: USER_ID,
        productId: product.id,
        productName: product.name,
        price: product.price,
        quantity: 1
      });
      setMessage("Added to cart successfully");
      setTimeout(() => navigate("/cart"), 500);
    } catch (err) {
      setError(err.message);
    }
  };

  if (!product && !error) {
    return <p>Loading product...</p>;
  }

  if (error) {
    return <p className="error">{error}</p>;
  }

  return (
    <section className="detail-card">
      <img src={product.image_url} alt={product.name} />
      <div className="detail-content">
        <p className="category-pill">{product.category}</p>
        <h2>{product.name}</h2>
        <p>{product.description}</p>
        <h3 className="detail-price">${Number(product.price).toFixed(2)}</h3>
        <button onClick={handleAdd}>Add To Cart</button>
        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
      </div>
    </section>
  );
}

export default ProductDetailPage;
