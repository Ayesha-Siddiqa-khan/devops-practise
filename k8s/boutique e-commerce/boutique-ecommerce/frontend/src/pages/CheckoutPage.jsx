import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const USER_ID = 1;

function CheckoutPage() {
  const navigate = useNavigate();
  const [cartItems, setCartItems] = useState([]);
  const [address, setAddress] = useState({
    shippingAddress: "",
    city: "",
    country: "",
    postalCode: ""
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [placingOrder, setPlacingOrder] = useState(false);

  const totalAmount = useMemo(
    () => cartItems.reduce((sum, item) => sum + Number(item.price) * Number(item.quantity), 0),
    [cartItems]
  );

  useEffect(() => {
    Promise.all([api.cart(USER_ID), api.getAddress(USER_ID)])
      .then(([items, savedAddress]) => {
        setCartItems(items);
        setAddress({
          shippingAddress: savedAddress.shipping_address || "",
          city: savedAddress.city || "",
          country: savedAddress.country || "",
          postalCode: savedAddress.postal_code || ""
        });
      })
      .catch((err) => setError(err.message));
  }, []);

  const placeOrder = async () => {
    if (cartItems.length === 0) {
      setError("Your cart is empty");
      return;
    }

    try {
      setPlacingOrder(true);
      setError("");

      await api.updateAddress(USER_ID, address);

      const order = await api.placeOrder({
        userId: USER_ID,
        items: cartItems,
        totalAmount,
        paymentMethod: "card"
      });

      await api.clearCart(USER_ID);

      setMessage(`Order #${order.id} placed successfully`);
      setTimeout(() => navigate("/products"), 1200);
    } catch (err) {
      setError(err.message);
    } finally {
      setPlacingOrder(false);
    }
  };

  return (
    <section>
      <div className="section-head">
        <h2>Checkout</h2>
        <p className="muted">Fill your shipping details and place your order securely.</p>
      </div>
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      <div className="form-grid">
        <label>
          Shipping Address
          <input
            value={address.shippingAddress}
            placeholder="Street address"
            onChange={(e) => setAddress({ ...address, shippingAddress: e.target.value })}
          />
        </label>
        <label>
          City
          <input
            value={address.city}
            placeholder="City"
            onChange={(e) => setAddress({ ...address, city: e.target.value })}
          />
        </label>
        <label>
          Country
          <input
            value={address.country}
            placeholder="Country"
            onChange={(e) => setAddress({ ...address, country: e.target.value })}
          />
        </label>
        <label>
          Postal Code
          <input
            value={address.postalCode}
            placeholder="Postal code"
            onChange={(e) => setAddress({ ...address, postalCode: e.target.value })}
          />
        </label>
      </div>

      <div className="summary-card">
        <h3>Order Summary</h3>
        {cartItems.map((item) => (
          <p key={item.id}>
            {item.product_name} x {item.quantity} = ${
              (Number(item.price) * Number(item.quantity)).toFixed(2)
            }
          </p>
        ))}
        <h3>Total: ${totalAmount.toFixed(2)}</h3>

        <button onClick={placeOrder} disabled={placingOrder}>
          {placingOrder ? "Placing order..." : "Place Order"}
        </button>
      </div>
    </section>
  );
}

export default CheckoutPage;
