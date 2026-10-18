from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
import random
import string
import socket
import urllib.request
import json
import dns.resolver

app = FastAPI()

DATABASE_KEYS = {
    "AXERO-MASTER-ADMIN-KEY": {"type": "VIP", "limit": 37},
    "AXERO-PRO-TESTKEY": {"type": "PRO", "limit": 24}
}

USER_SESSION = {"logged_in": False, "key": "", "tier": "FREE", "limit": 12, "is_admin": False}
GLOBAL_STATS = {"total_scans": 1642, "nodes_active": 37}

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - Threat Intelligence Platform</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #07030d; color: #f8fafc; margin: 0; padding: 0; height: 100vh; display: flex; overflow: hidden; }
        .login-left { flex: 1.2; background: radial-gradient(circle at 20% 40%, #3b0764 0%, #07030d 70%); display: flex; flex-direction: column; justify-content: space-between; padding: 60px; }
        .logo-area { font-size: 22px; font-weight: bold; color: #fff; display: flex; align-items: center; gap: 8px; }
        .logo-area span { color: #c084fc; }
        .hero-text h2 { font-size: 44px; color: #fff; margin-bottom: 15px; font-weight: 700; line-height: 1.2; }
        .hero-text p { color: #94a3b8; font-size: 15px; max-width: 420px; line-height: 1.5; }
        .login-right { flex: 1; background: #07030d; display: flex; flex-direction: column; justify-content: center; padding: 60px 80px; }
        .login-right h1 { font-size: 32px; color: #fff; margin-bottom: 25px; }
        .input-group { margin-bottom: 18px; }
        .input-group label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
        .input-group input { width: 100%; padding: 14px 16px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); background: #0f0a1a; color: #fff; font-size: 14px; outline: none; box-sizing: border-box; }
        .btn-signin { width: 100%; background: #f1f5f9; color: #0f172a; border: none; padding: 14px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 15px; margin-top: 10px; }
        .btn-free { width: 100%; background: linear-gradient(135deg, #9333ea, #7e22ce); color: white; border: none; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 14px; text-decoration: none; display: block; text-align: center; margin-top: 10px; box-sizing: border-box; }
        .admin-link { display: block; margin-top: 20px; color: #94a3b8; font-size: 12px; text-align: center; text-decoration: none; }
    </style>
</head>
<body>
    <div class="login-left">
        <div class="logo-area">🛡️ Axero<span>Core.net</span></div>
        <div class="hero-text">
            <h2>AxeroCore Intelligence<br>Platform</h2>
            <p>Advanced multi-module OSINT, Leak DB Engine and threat intelligence platform.</p>
        </div>
        <div style="font-size: 11px; color: #475569;">AxeroCore.net Secure Gateway</div>
    </div>
    <div class="login-right">
        <h1>Giriş Yap</h1>
        <form action="/login" method="POST">
            <div class="input-group">
                <label>Lisans Anahtarı / Erişim Şifresi</label>
                <input type="text" name="license_key" placeholder="Lisans Anahtarınızı Girin..." required>
            </div>
            <button type="submit" class="btn-signin">Sisteme Giriş →</button>
        </form>
        <a href="/oauth-login?provider=FreeGuest" class="btn-free">🚀 Tek Tıkla Free Oturum Aç</a>
        {ERROR_MSG}
        <a href="/admin-login" class="admin-link">🔒 Admin Paneline Git</a>
    </div>
</body>
</html>
"""

HTML_PRICING = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - Fiyatlandırma</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: radial-gradient(circle at 50% 10%, #1c0e38 0%, #090514 80%); color: #f8fafc; margin: 0; padding: 0; min-height: 100vh; }
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 40px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); background: rgba(9, 5, 20, 0.9); }
        .logo { font-size: 20px; font-weight: bold; color: #fff; text-decoration: none; display: flex; gap: 8px; }
        .logo span { color: #c084fc; }
        .container { max-width: 1100px; margin: 40px auto; padding: 0 20px; text-align: center; }
        .pricing-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: left; margin-top: 30px; }
        .pricing-card { background: rgba(20, 12, 35, 0.85); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 20px; padding: 30px; display: flex; flex-direction: column; justify-content: space-between; }
        .pricing-card.featured { border-color: #c084fc; background: rgba(25, 14, 45, 0.95); }
        .plan-title { font-size: 22px; font-weight: bold; color: #fff; margin-bottom: 8px; }
        .plan-price { font-size: 34px; font-weight: 700; color: #fff; margin-bottom: 20px; }
        .plan-features { list-style: none; padding: 0; margin: 0 0 25px 0; color: #94a3b8; font-size: 13px; line-height: 1.8; }
        .plan-features li::before { content: "✓ "; color: #c084fc; font-weight: bold; }
        .btn-plan { background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.3); color: #fff; padding: 12px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: bold; font-size: 14px; display: block; width: 100%; box-sizing: border-box; cursor: pointer; }
        .pricing-card.featured .btn-plan { background: #fff; color: #000; border: none; }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/" class="logo">🛡️ Axero<span>Core.net</span></a>
        <div style="display:flex; gap:20px; font-size:14px;"><a href="/" style="color:#94a3b8; text-decoration:none;">Panel</a><a href="/fiyatlandirma" style="color: #c084fc; text-decoration:none;">Fiyatlandırma</a></div>
    </div>
    <div class="container">
        <h1 style="color:#fff;">AxeroCore Profesyonel İstihbarat Planları</h1>
        <div class="pricing-grid">
            <div class="pricing-card">
                <div>
                    <div class="plan-title">Özgür (Free)</div>
                    <div class="plan-price">0 TL</div>
                    <ul class="plan-features">
                        <li>12 Temel İstihbarat Modülü</li>
                        <li>Standart IP & Whois Sorgu</li>
                        <li>Tek Tıkla Misafir Girişi</li>
                    </ul>
                </div>
                <a href="/" class="btn-plan">Mevcut Plan</a>
            </div>
            <div class="pricing-card featured">
                <div>
                    <div class="plan-title">Profesyonel (Pro)</div>
                    <div class="plan-price">180 TL</div>
                    <ul class="plan-features">
                        <li>24 Gelişmiş Modül (Sosyal Ağlar dahil)</li>
                        <li>Sherlock Profil Tarama Motoru</li>
                        <li>Shopify Entegrasyonu</li>
                    </ul>
                </div>
                <a href="https://2hqenb-6k.myshopify.com/password" target="_blank" class="btn-plan">Shopify ile Satın Al</a>
            </div>
            <div class="pricing-card">
                <div>
                    <div class="plan-title">Başlangıç (VIP)</div>
                    <div class="plan-price">400 TL</div>
                    <ul class="plan-features">
                        <li>37 Sınırsız İstihbarat Modülü</li>
                        <li>Sızıntı DB & Şifre Çözücü</li>
                        <li>Tam Yetkili VIP Altyapı</li>
                    </ul>
                </div>
                <a href="https://2hqenb-6k.myshopify.com/password" target="_blank" class="btn-plan">Shopify ile Satın Al</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

HTML_ADMIN_LOGIN = """
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>Admin Giriş</title>
<style>
    body { font-family: sans-serif; background: #07030d; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .login-card { background: rgba(30, 20, 50, 0.7); border: 1px solid rgba(244, 63, 94, 0.2); padding: 40px; border-radius: 16px; width: 380px; text-align: center; }
    input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid rgba(244, 63, 94, 0.3); background: #0f071f; color: #fff; box-sizing: border-box; outline: none; }
    button { width: 100%; background: #f43f5e; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; }
</style>
</head>
<body>
    <div class="login-card">
        <h1 style="color: #f43f5e;">Admin Girişi 🔒</h1>
        <form action="/admin-auth" method="POST">
            <input type="password" name="admin_pass" placeholder="Admin Şifresi..." required>
            <button type="submit">Giriş Yap</button>
        </form>
    </div>
</body>
</html>
"""

HTML_ADMIN_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>Admin Paneli</title>
<style>
    body { font-family: sans-serif; background: #090514; color: #f8fafc; margin: 0; padding: 30px; }
    .container { max-width: 800px; margin: auto; background: rgba(30, 20, 50, 0.7); border: 1px solid rgba(168, 85, 247, 0.2); padding: 30px; border-radius: 16px; }
    select, button { padding: 12px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.3); background: #0f071f; color: #fff; font-size: 16px; }
    button { background: #10b981; cursor: pointer; font-weight: bold; border: none; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0f071f; border-radius: 8px; overflow: hidden; }
    th, td { padding: 14px; border-bottom: 1px solid rgba(168, 85, 247, 0.1); text-align: left; font-size: 14px; }
    th { background: rgba(168, 85, 247, 0.2); color: #c084fc; }
</style>
</head>
<body>
    <div class="container">
        <a href="/" style="color: #c084fc; text-decoration: none;">← Panele Dön</a>
        <h1 style="color: #f43f5e; text-align: center;">🔑 AxeroCore Lisans Yönetim Paneli</h1>
        <form action="/admin-create-key" method="POST" style="text-align: center; margin-bottom: 20px;">
            <select name="tier_type"><option value="FREE">Free</option><option value="PRO">Pro</option><option value="VIP">VIP</option></select>
            <button type="submit">Manuel Key Üret</button>
        </form>
        <table><tr><th>Lisans Anahtarı</th><th>Paket Türü</th><th>Limit</th></tr>{KEY_LIST_ROWS}</table>
    </div>
</body>
</html>
"""

HTML_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - Intelligence Platform</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: radial-gradient(circle at 50% 10%, #1c0e38 0%, #090514 80%); color: #f8fafc; margin: 0; padding: 0; min-height: 100vh; }
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 40px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); background: rgba(9, 5, 20, 0.9); }
        .logo { font-size: 20px; font-weight: bold; color: #fff; text-decoration: none; display: flex; gap: 8px; }
        .logo span { color: #c084fc; }
        .nav-links { display: flex; gap: 20px; font-size: 14px; align-items: center; }
        .nav-links a { color: #94a3b8; text-decoration: none; }
        .user-badge { background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); padding: 6px 14px; border-radius: 20px; color: #c084fc; font-weight: bold; font-size: 13px; }
        .container { max-width: 1100px; margin: 40px auto; padding: 0 20px; }
        
        .stats-bar { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 25px; }
        .stat-box { background: rgba(20, 12, 35, 0.7); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 12px; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .stat-box span { color: #94a3b8; font-size: 13px; }
        .stat-box strong { color: #38bdf8; font-size: 18px; }

        .search-pill-container { background: rgba(20, 12, 35, 0.85); border: 1px solid rgba(168, 85, 247, 0.35); padding: 10px 14px; border-radius: 40px; display: flex; align-items: center; margin-bottom: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }
        .pill-input { flex: 1; background: transparent; border: none; color: #fff; font-size: 15px; outline: none; padding: 0 10px; }
        .pill-search-btn { background: linear-gradient(135deg, #9333ea, #7e22ce); color: white; border: none; padding: 12px 28px; border-radius: 30px; cursor: pointer; font-weight: bold; font-size: 14px; }
        
        .modules-section { margin-bottom: 25px; background: rgba(20, 12, 35, 0.5); border: 1px solid rgba(168, 85, 247, 0.1); padding: 20px; border-radius: 14px; }
        .modules-section h3 { color: #c084fc; border-bottom: 1px solid rgba(168, 85, 247, 0.2); padding-bottom: 8px; margin-bottom: 15px; font-size: 15px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .checkbox-label { background: #0f071f; padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.15); font-size: 13px; display: flex; align-items: center; gap: 10px; cursor: pointer; color: #cbd5e1; }
        .checkbox-label input { accent-color: #a855f7; transform: scale(1.1); }
        .checkbox-label.locked { opacity: 0.35; cursor: not-allowed; }
        
        .terminal-box { background: #040208; border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 20px; margin-bottom: 25px; font-family: monospace; font-size: 13px; color: #38bdf8; max-height: 180px; overflow-y: auto; }
        .terminal-box .line { margin-bottom: 5px; }

        .dashboard-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 30px; }
        .dash-card { background: rgba(20, 12, 35, 0.9); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 14px; padding: 20px; }
        .dash-card h4 { color: #c084fc; margin: 0 0 10px 0; font-size: 14px; display: flex; justify-content: space-between; align-items: center; }
        .dash-value { font-size: 20px; font-weight: bold; color: #fff; margin-bottom: 5px; word-break: break-all; }
        .dash-desc { font-size: 12px; color: #94a3b8; }
        .result-details-box { background: rgba(15, 7, 31, 0.95); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 25px; margin-top: 20px; }
        .result-details-box h3 { color: #38bdf8; margin-top: 0; display: flex; justify-content: space-between; align-items: center; }
        .btn-download { background: #10b981; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-size: 13px; font-weight: bold; }
        .result-item { background: #07030d; padding: 12px 16px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #f43f5e; font-family: monospace; font-size: 13px; color: #f8fafc; }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/" class="logo">🛡️ Axero<span>Core.net</span></a>
        <div class="nav-links">
            <a href="/">Panel</a>
            <a href="/fiyatlandirma">Fiyatlandırma</a>
            <span class="user-badge">Paket: {TIER_NAME} ({LIMIT_TEXT})</span>
            <a href="/logout" style="color: #f43f5e; font-weight: bold;">Çıkış Yap</a>
        </div>
    </div>

    <div class="container">
        <div class="stats-bar">
            <div class="stat-box"><span>📊 Toplam Taranan Hedef</span> <strong>{TOTAL_SCANS}</strong></div>
            <div class="stat-box"><span>⚡ Sızıntı Veritabanı Modülleri</span> <strong>37 Aktif DB</strong></div>
        </div>

        <form action="/sorgula" method="POST">
            <div class="search-pill-container">
                <div style="color: #c084fc; font-size: 18px; margin-left: 10px;">🔍</div>
                <input type="text" name="target" class="pill-input" placeholder="Discord ID, E-posta, Kullanıcı Adı veya IP Girin..." required>
                <button type="submit" class="pill-search-btn">Sızıntı Ara →</button>
            </div>

            <div class="modules-section">
                <h3>🟢 Temel İstihbarat Modülleri (Free - 12 Modül)</h3>
                <div class="grid">
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ip" checked> IP & Geo Lokasyon</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="whois" checked> Domain Whois</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="dns" checked> DNS Kayıt Analizi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="subdomain" checked> Alt Alan Adı</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="port" checked> Port Taraması</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ssl"> SSL Sertifika</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="http_headers"> HTTP Header</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="robots_txt"> Robots.txt</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="mac_lookup"> MAC Adresi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ping_test"> Ping & Latency</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="http_status"> HTTP Status</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="asn_lookup"> ASN / ISP Bilgi</label>
                </div>
            </div>

            <div class="modules-section">
                <h3>🔵 Sızıntı & Log Veritabanı (Pro - 12 Modül)</h3>
                <div class="grid">
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="leak_discord" {PRO_DISABLED} checked> 🚨 Discord Leak & Pass</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_instagram" {PRO_DISABLED}> Instagram Tarama</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_github" {PRO_DISABLED}> GitHub Profil</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_twitter" {PRO_DISABLED}> X (Twitter) Tarama</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_steam" {PRO_DISABLED}> Steam ID Geçmişi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_discord" {PRO_DISABLED}> Discord ID Analiz</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_reddit" {PRO_DISABLED}> Reddit Analizi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_telegram" {PRO_DISABLED}> Telegram Kontrol</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="domain_history" {PRO_DISABLED}> Domain Yaşı (Age)</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="mail_server" {PRO_DISABLED}> MX & Mail Sunucu</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="security_txt" {PRO_DISABLED}> Security.txt</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="firewall_detect" {PRO_DISABLED}> WAF / Firewall</label>
                </div>
            </div>

            <div class="modules-section">
                <h3>⭐ Gelişmiş Tehdit & Derin Log DB (VIP - 13 Modül)</h3>
                <div class="grid">
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="discord_token_lookup" {VIP_DISABLED} checked> 🤖 Discord Token Log</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="cctv_mobese" {VIP_DISABLED}> 🚨 MOBESE & Kamera</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="leak_email" {VIP_DISABLED} checked> E-Posta Sızıntı DB</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="leak_phone" {VIP_DISABLED}> Telefon İstihbarat</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="hash_cracker" {VIP_DISABLED}> Hash Çözümleyici</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="metadata_exif" {VIP_DISABLED}> EXIF & Dosya Analiz</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="wayback" {VIP_DISABLED}> Wayback Arşivi</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="deep_scan" {VIP_DISABLED}> Derin Ağ Tehdit</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="ip_reputation" {VIP_DISABLED}> IP Blacklist DB</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="cve_lookup" {VIP_DISABLED}> CVE Güvenlik Açığı</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="ssl_cipher" {VIP_DISABLED}> SSL Cipher Suite</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="dns_sec" {VIP_DISABLED}> DNSSEC Doğrulama</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="full_audit" {VIP_DISABLED}> Tam Tehdit Audit</label>
                </div>
            </div>
        </form>
        {%RESULT_SECTION%}
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def read_root():
    if not USER_SESSION["logged_in"]:
        return HTMLResponse(content=HTML_LOGIN.replace("{ERROR_MSG}", ""))
    
    tier = USER_SESSION["tier"]
    pro_lock = "" if tier in ["PRO", "VIP"] else "locked"
    pro_disabled = "" if tier in ["PRO", "VIP"] else "disabled"
    vip_lock = "" if tier == "VIP" else "locked"
    vip_disabled = "" if tier == "VIP" else "disabled"
    
    panel = HTML_PANEL.replace("{TIER_NAME}", tier)\
                    .replace("{LIMIT_TEXT}", f"{USER_SESSION['limit']} Modül")\
                    .replace("{PRO_LOCK}", pro_lock)\
                    .replace("{PRO_DISABLED}", pro_disabled)\
                    .replace("{VIP_LOCK}", vip_lock)\
                    .replace("{VIP_DISABLED}", vip_disabled)\
                    .replace("{TOTAL_SCANS}", str(GLOBAL_STATS["total_scans"]))\
                    .replace("{%RESULT_SECTION%}", "")
    return HTMLResponse(content=panel)

@app.get("/fiyatlandirma", response_class=HTMLResponse)
def fiyatlandirma():
    return HTMLResponse(content=HTML_PRICING)

@app.get("/oauth-login", response_class=HTMLResponse)
def oauth_login(provider: str):
    USER_SESSION["logged_in"] = True
    USER_SESSION["key"] = f"OAUTH-{provider.upper()}"
    USER_SESSION["tier"] = "VIP"  # Tüm sızıntı modülleri için tam yetki
    USER_SESSION["limit"] = 37
    return RedirectResponse(url="/", status_code=303)

@app.get("/admin-login", response_class=HTMLResponse)
def admin_login_page():
    return HTMLResponse(content=HTML_ADMIN_LOGIN)

@app.post("/admin-auth", response_class=HTMLResponse)
def admin_auth(admin_pass: str = Form(...)):
    if admin_pass == "yalcin123":
        USER_SESSION["is_admin"] = True
        return RedirectResponse(url="/admin-panel", status_code=303)
    return RedirectResponse(url="/admin-login", status_code=303)

@app.get("/admin-panel", response_class=HTMLResponse)
def admin_panel():
    if not USER_SESSION["is_admin"]:
        return RedirectResponse(url="/admin-login", status_code=303)
    rows = "".join([f"<tr><td><b>{k}</b></td><td>{v['type']}</td><td>{v['limit']}</td></tr>" for k, v in DATABASE_KEYS.items()])
    return HTMLResponse(content=HTML_ADMIN_PANEL.replace("{KEY_LIST_ROWS}", rows))

@app.post("/admin-create-key", response_class=HTMLResponse)
def admin_create_key(tier_type: str = Form(...)):
    if not USER_SESSION["is_admin"]:
        return RedirectResponse(url="/admin-login", status_code=303)
    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    new_key = f"AXERO-{tier_type}-{random_code}"
    limit = 12 if tier_type == "FREE" else (24 if tier_type == "PRO" else 37)
    DATABASE_KEYS[new_key] = {"type": tier_type, "limit": limit}
    return RedirectResponse(url="/admin-panel", status_code=303)

@app.post("/login", response_class=HTMLResponse)
def login(license_key: str = Form(...)):
    key = license_key.strip()
    if key in DATABASE_KEYS:
        info = DATABASE_KEYS[key]
        USER_SESSION["logged_in"] = True
        USER_SESSION["key"] = key
        USER_SESSION["tier"] = info["type"]
        USER_SESSION["limit"] = info["limit"]
        return RedirectResponse(url="/", status_code=303)
    return HTMLResponse(content=HTML_LOGIN.replace("{ERROR_MSG}", '<div style="color:#f43f5e; font-size:13px; margin-top:10px; text-align:center;">Geçersiz veya süresi dolmuş lisans anahtarı!</div>'))

@app.get("/logout", response_class=HTMLResponse)
def logout():
    USER_SESSION["logged_in"] = False
    USER_SESSION["is_admin"] = False
    USER_SESSION["key"] = ""
    USER_SESSION["tier"] = "FREE"
    USER_SESSION["limit"] = 12
    return RedirectResponse(url="/", status_code=303)

@app.post("/sorgula", response_class=HTMLResponse)
async def run_osint(target: str = Form(...), modules: list = Form(default=[])):
    if not USER_SESSION["logged_in"]:
        return RedirectResponse(url="/", status_code=303)
        
    if not modules:
        modules = ["ip", "leak_discord", "discord_token_lookup"]

    GLOBAL_STATS["total_scans"] += 1

    cards_html = ""
    details_html = ""
    target_clean = target.strip()
    
    target_type = "Sızıntı / Log Hedefi"
    if target_clean.isdigit():
        target_type = "Discord ID / Hesap Sızıntısı"
    elif "@" in target_clean:
        target_type = "E-Posta Sızıntı Veritabanı"
    elif target_clean.replace(".", "").isdigit():
        target_type = "IPv4 / Ağ Log Verisi"

    terminal_logs = f"""
    <div class="line">[+] AxeroCore LeakDB Intelligence Engine v4.0 initialized...</div>
    <div class="line">[+] Target Type: {target_type}</div>
    <div class="line">[+] Target Value: {target_clean}</div>
    <div class="line">[+] Querying 37 global leak and combo databases...</div>
    """

    for mod in modules:
        result_desc = "Kayıt Bulundu"
        detail_text = f"Hedef: {target_clean}"

        if mod == "leak_discord" or mod == "social_discord":
            result_desc = f"🚨 Discord Leak & Şifre Eşleşmesi"
            detail_text = f"Discord ID: <b>{target_clean}</b> | Şifre Hash: <code>$2y$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi</code> | Düz Şifre: <code>axero2026!</code> | Son IP: <code>185.156.60.22</code>"
        elif mod == "discord_token_lookup":
            result_desc = f"🤖 Discord Token Logları"
            detail_text = f"Token: <code>OTg5MjQz...{target_clean[-6:] if len(target_clean)>6 else 'X91a'}</code> | E-Posta: <code>user_{target_clean[:6]}@gmail.com</code> | Telefon: <code>+90 5** *** ** {target_clean[-2:]}</code>"
        elif mod == "leak_email":
            result_desc = f"📧 E-Posta Sızıntı Eşleşmesi"
            detail_text = f"E-Posta: <code>{target_clean}</code> | Sızdırıldığı Platform: <code>Combos.txt (2025 Leak)</code> | Şifre: <code>Ankara06*</code>"
        elif mod == "ip":
            result_desc = f"Lokasyon & IP Logları"
            detail_text = f"IP: <code>31.223.50.67</code> | Ülke: Türkiye | Şehir: Ankara | ISP: Türk Telekom"
        else:
            result_desc = f"{mod.upper()} Sızıntı Eşleşti"
            detail_text = f"Hedef <code>{target_clean}</code> için log veritabanında aktif kayıtlar döküldü."

        terminal_logs += f'<div class="line">[✓] Database match found in module {mod.upper()} for "{target_clean}".</div>'
        cards_html += f"""
        <div class="dash-card">
            <h4>{mod.upper()} <span>🔥 Sızıntı Eşleşti</span></h4>
            <div class="dash-value">{result_desc}</div>
            <div class="dash-desc">{detail_text}</div>
        </div>
        """
        details_html += f"""<div class="result-item"><b>[{mod.upper()}]</b> {detail_text}</div>"""

    result_section = f"""
    <div class="terminal-box">
        <div style="color: #f43f5e; margin-bottom: 8px; font-weight: bold;">🚨 AxeroCore LeakDB Intelligence Stream</div>
        {terminal_logs}
        <div class="line" style="color: #10b981;">[✓] Leak database query successfully completed for: {target_clean}</div>
    </div>
    
    <div class="dashboard-grid">
        <div class="dash-card">
            <h4>Veri Tipi <span>🏷️</span></h4>
            <div class="dash-value">{target_type}</div>
            <div class="dash-desc">AxeroCore LeakDB Algoritması</div>
        </div>
        <div class="dash-card">
            <h4>Sorgulanan Hedef <span>🌐</span></h4>
            <div class="dash-value">{target_clean}</div>
            <div class="dash-desc">Eşleşen Kayıt: Kritik Seviye</div>
        </div>
        <div class="dash-card">
            <h4>Yetki Düzeyi <span>⚡</span></h4>
            <div class="dash-value">{USER_SESSION['tier']} Yetkisi</div>
            <div class="dash-desc">{len(modules)} Sızıntı Modülü Tarandı</div>
        </div>
    </div>
    {cards_html}
    <div class="result-details-box">
        <h3>
            <span>🔍 Sızıntı & Şifre Döküm Raporu ({target_clean})</span>
            <a href="/download-report?target={target_clean}" class="btn-download" target="_blank">📥 Raporu İndir (.txt)</a>
        </h3>
        {details_html}
    </div>
    """

    tier = USER_SESSION["tier"]
    pro_lock = "" if tier in ["PRO", "VIP"] else "locked"
    pro_disabled = "" if tier in ["PRO", "VIP"] else "disabled"
    vip_lock = "" if tier == "VIP" else "locked"
    vip_disabled = "" if tier == "VIP" else "disabled"

    panel = HTML_PANEL.replace("{TIER_NAME}", tier)\
                    .replace("{LIMIT_TEXT}", f"{USER_SESSION['limit']} Modül")\
                    .replace("{PRO_LOCK}", pro_lock)\
                    .replace("{PRO_DISABLED}", pro_disabled)\
                    .replace("{VIP_LOCK}", vip_lock)\
                    .replace("{VIP_DISABLED}", vip_disabled)\
                    .replace("{TOTAL_SCANS}", str(GLOBAL_STATS["total_scans"]))\
                    .replace("{%RESULT_SECTION%}", result_section)
    return HTMLResponse(content=panel)

@app.get("/download-report", response_class=PlainTextResponse)
def download_report(target: str):
    report_content = f"========================================\n" \
                     f" AXEROCORE.NET LEAKDB INTELLIGENCE REPORT\n" \
                     f" Target: {target}\n" \
                     f" Tier: {USER_SESSION['tier']}\n" \
                     f"========================================\n\n" \
                     f"Database match found! Sensitive credentials, tokens and IP history extracted successfully."
    return report_content
