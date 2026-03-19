const express = require("express");
const axios = require("axios");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Steam login deneme endpoint'i
app.post("/login", async (req, res) => {
  const { username, password } = req.body;

  const headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Origin": "https://steamcommunity.com",
    "Referer": "https://steamcommunity.com/",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "sessionid=ee387dfa1888c4c8101b7a99"
  };

  const body = new URLSearchParams({
    username,
    password
    // Eğer finalizelogin başka parametre istiyorsa buraya ekleyeceğiz
  });

  try {
    const resp = await axios.post(
      "https://steamcommunity.com/login/finalizelogin",
      body,
      { headers }
    );

    // Dönen cevabı direkt kullanıcıya gönder
    res.json(resp.data);
  } catch (err) {
    console.error("Login isteği hata verdi:", err.message);
    res.status(500).json({ error: err.message, details: err.response?.data });
  }
});

// Render için port ayarı
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server çalışıyor: http://localhost:${PORT}`);
});
