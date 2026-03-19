const express = require("express");
const cors = require("cors");
const checkAccount = require("./checkAccount");

const app = express();
app.use(cors());
app.use(express.json());

// Statik dosyaları public klasöründen sun
app.use(express.static("public"));

app.post("/checkAccount", async (req, res) => {
  const { user, pass } = req.body;
  const result = await checkAccount(user, pass);
  res.json(result);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server ${PORT} portunda çalışıyor`));
