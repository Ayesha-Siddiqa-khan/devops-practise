import { NavLink, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import ProductsPage from "./pages/ProductsPage";
import ProductDetailPage from "./pages/ProductDetailPage";
import CartPage from "./pages/CartPage";
import CheckoutPage from "./pages/CheckoutPage";

function App() {
  return (
    <div className="app-shell">
      <header className="topbar panel">
        <div className="brand-wrap">
          <p className="eyebrow">Modern handmade collections</p>
          <h1>ZeenKaar Boutique</h1>
          <p>Curated fashion and beauty essentials</p>
        </div>
        <nav className="topnav">
          <NavLink to="/" className={({ isActive }) => (isActive ? "active" : "")}>Home</NavLink>
          <NavLink to="/products" className={({ isActive }) => (isActive ? "active" : "")}>Products</NavLink>
          <NavLink to="/cart" className={({ isActive }) => (isActive ? "active" : "")}>Cart</NavLink>
          <NavLink to="/checkout" className={({ isActive }) => (isActive ? "active" : "")}>Checkout</NavLink>
        </nav>
      </header>

      <main className="content panel">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/:id" element={<ProductDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
