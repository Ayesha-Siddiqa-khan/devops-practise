const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const { createProxyMiddleware } = require("http-proxy-middleware");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 4000;

const serviceUrls = {
  auth: process.env.AUTH_SERVICE_URL || "http://auth-service:4001",
  products: process.env.PRODUCT_SERVICE_URL || "http://product-service:4002",
  cart: process.env.CART_SERVICE_URL || "http://cart-service:4003",
  orders: process.env.ORDER_SERVICE_URL || "http://order-service:4004",
  users: process.env.USER_SERVICE_URL || "http://user-service:4005",
  payments: process.env.PAYMENT_SERVICE_URL || "http://payment-service:4006"
};

app.use(cors());
app.use(morgan("dev"));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "api-gateway" });
});

app.use(
  "/api/auth",
  createProxyMiddleware({
    target: serviceUrls.auth,
    changeOrigin: true,
    pathRewrite: (_, req) => req.originalUrl.replace(/^\/api\/auth/, "/auth")
  })
);

app.use(
  "/api/products",
  createProxyMiddleware({
    target: serviceUrls.products,
    changeOrigin: true,
    pathRewrite: (_, req) => req.originalUrl.replace(/^\/api\/products/, "/products")
  })
);

app.use(
  "/api/cart",
  createProxyMiddleware({
    target: serviceUrls.cart,
    changeOrigin: true,
    pathRewrite: (_, req) => req.originalUrl.replace(/^\/api\/cart/, "/cart")
  })
);

app.use(
  "/api/orders",
  createProxyMiddleware({
    target: serviceUrls.orders,
    changeOrigin: true,
    pathRewrite: (_, req) => req.originalUrl.replace(/^\/api\/orders/, "/orders")
  })
);

app.use(
  "/api/users",
  createProxyMiddleware({
    target: serviceUrls.users,
    changeOrigin: true,
    pathRewrite: (_, req) => req.originalUrl.replace(/^\/api\/users/, "/users")
  })
);

app.use(
  "/api/payments",
  createProxyMiddleware({
    target: serviceUrls.payments,
    changeOrigin: true,
    pathRewrite: (_, req) => req.originalUrl.replace(/^\/api\/payments/, "/payments")
  })
);

app.listen(port, () => {
  console.log(`API gateway is running on port ${port}`);
});
