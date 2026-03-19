const axios = require("axios");

async function steamLogin(username, password) {
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
    // finalizelogin’in istediği ek parametreleri buraya ekleyeceğiz
  });

  try {
    const resp = await axios.post(
      "https://steamcommunity.com/login/finalizelogin",
      body,
      { headers }
    );
    console.log(resp.data);
    return resp.data;
  } catch (err) {
    console.error("Login isteği hata verdi:", err.response?.data || err.message);
  }
}

// Test
steamLogin("seninKullaniciAdin", "seninSifren");
