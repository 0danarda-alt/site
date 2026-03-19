const axios = require('axios');
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
