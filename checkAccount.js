const express = require("express");
const axios = require("axios");
const bodyParser = require("body-parser");

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.post("/login", async (req, res) => {
  const { username, password } = req.body;

  const headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Origin": "https://steamcommunity.com",
    "Referer": "https://steamcommunity.com/",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/x-www-form-urlencoded",const axios = require('axios');
const { wrapper } = require('axios-cookiejar-support');
const { CookieJar } = require('tough-cookie');
const { JSDOM } = require('jsdom');

module.exports = async (user, pass) => {
    const jar = new CookieJar();
    const client = wrapper(axios.create({ jar, withCredentials: true }));

    try {
        // 1. Login
        const loginResp = await client.post('https://store.steampowered.com/login', {
            email: user,
            password: pass
        });

        if (loginResp.data.success) {
            // 2. Profil sayfasını çek
            const panelResp = await client.get('https://steamcommunity.com/my');
            const dom = new JSDOM(panelResp.data);
            const document = dom.window.document;

            // SteamID64’i bul
            const steamidMatch = panelResp.data.match(/"steamid":"(\d+)"/);
            const steamid = steamidMatch ? steamidMatch[1] : null;

            if (!steamid) {
                return { success: false, status: 'fail', reason: 'SteamID bulunamadı' };
            }

            // 3. Oyun listesi sayfasını çek
            const gamesResp = await client.get(`https://steamcommunity.com/profiles/${steamid}/games/?tab=all`);
            const domGames = new JSDOM(gamesResp.data);
            const docGames = domGames.window.document;

            const games = [];
            docGames.querySelectorAll('.gameListRowItemName').forEach(el => {
                games.push(el.textContent.trim());
            });

            return {
                success: true,
                status: 'hit',
                steamid,
                games
            };
        } else {
            return { success: false, status: 'fail', reason: 'Login başarısız' };
        }
    } catch (e) {
        return { success: false, status: 'fail', reason: "Bağlantı Hatası: " + e.message };
    }
};
    "Cookie": "sessionid=ee387dfa1888c4c8101b7a99"
  };

  const body = new URLSearchParams({
    username,
    password
    // finalizelogin’in istediği ek parametreleri buraya ekleyeceğiz
  });

  try {
    const resp = await axios.post(
      "https://steamcommunity.com/login/finalizelogin",
      body,
      { headers }
    );
    res.json(resp.data);
  } catch (err) {
    console.error("Login isteği hata verdi:", err.message);
    res.status(500).json({ error: err.message, details: err.response?.data });
  }
});

// Render’ın verdiği portu kullan
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server çalışıyor: http://localhost:${PORT}`);
});
