const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 4006;

app.use(cors());
app.use(express.json());
app.use(morgan("dev"));

app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "payment-service" });
});

app.post("/payments/process", (req, res) => {
  const { amount, paymentMethod, forceStatus } = req.body;

  if (!amount) {
    return res.status(400).json({ success: false, message: "amount is required" });
  }

  let success;
  if (forceStatus === "success") {
    success = true;
  } else if (forceStatus === "failure") {
    success = false;
  } else {
    success = Math.random() >= 0.2;
  }

  if (!success) {
    return res.status(200).json({
      success: false,
      transactionId: null,
      message: "payment declined by bank simulator",
      paymentMethod: paymentMethod || "card"
    });
  }

  return res.status(200).json({
    success: true,
    transactionId: `txn_${Date.now()}`,
    message: "payment successful",
    paymentMethod: paymentMethod || "card"
  });
});

app.listen(port, () => {
  console.log(`Payment service is running on port ${port}`);
});
