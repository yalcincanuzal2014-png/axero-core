from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import random
import string
import socket
import urllib.request
import json
import datetime

app = FastAPI()

DATABASE_KEYS = {
    "AXERO-MASTER-ADMIN-KEY": {"type": "VIP", "limit": 37}
}

USER_SESSION = {"logged_in": False, "key": "", "tier": "", "limit": 0, "is_admin": False}

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - Welcome Back</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #07030d; color: #f8fafc; margin: 0; padding: 0; height: 100vh; display: flex; overflow: hidden; }
        
        /* Sol Taraf: Gradyan ve Tanıtım Alanı */
        .login-left { flex: 1.2; background: radial-gradient(circle at 20% 40%, #3b0764 0%, #07030d 70%); display: flex; flex-direction: column; justify-content: space-between; padding: 60px; position: relative; }
        .logo-area { font-size: 22px; font-weight: bold; color: #fff; display: flex; align-items: center; gap: 8px; }
        .logo-area span { color: #c084fc; }
        .hero-text h2 { font-size: 44px; color: #fff; margin-bottom: 15px; font-weight: 700; line-height: 1.2; }
        .hero-text p { color: #94a3b8; font-size: 15px; max-width: 420px; line-height: 1.5; }
        
        .steps-box { display: flex; flex-direction: column; gap: 12px; margin-top: 30px; max-width: 400px; }
        .step-item { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); padding: 14px 18px; border-radius: 12px; font-size: 14px; color: #cbd5e1; display: flex; align-items: center; gap: 12px; }
        .step-item.active { background: #fff; color: #000; font-weight: 600; }

        /* Sağ Taraf: Giriş Formu Alanı */
        .login-right { flex: 1; background: #07030d; display: flex; flex-direction: column; justify-content: center; padding: 60px 80px; }
        .login-right h1 { font-size: 32px; color: #fff; margin-bottom: 25px; font-weight: 600; }
        
        .social-logins { display: flex; gap: 12px; margin-bottom: 20px; }
        .social-btn { flex: 1; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); padding: 12px; border-radius: 10px; color: #fff; font-size: 13px; font-weight: 600; cursor: pointer; text-align: center; transition: 0.2s; }
        .social-btn:hover { background: rgba(255, 255, 255, 0.08); }

        .divider { text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.08); line-height: 0.1rem; margin: 25px 0; }
        .divider span { background: #07030d; padding: 0 15px; color: #64748b; font-size: 12px; }

        .input-group { margin-bottom: 18px; }
        .input-group label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
        .input-group input { width: 100%; padding: 14px 16px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); background: #0f0a1a; color: #fff; font-size: 14px; outline: none; box-sizing: border-box; transition: 0.2s; }
        .input-group input:focus { border-color: #a855f7; box-shadow: 0 0 10px rgba(168, 85, 247, 0.3); }

        .btn-signin { width: 100%; background: #f1f5f9; color: #0f172a; border: none; padding: 14px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 15px; transition: 0.2s; margin-top: 10px; }
        .btn-signin:hover { background: #fff; box-shadow: 0 0 15px rgba(255, 255, 255, 0.4); }

        .error { color: #f43f5e; font-size: 13px; margin-top: 10px; text-align: center; }
        .admin-link { display: block; margin-top: 20px; color: #94a3b8; font-size: 12px; text-align: center; text-decoration: none; }
        .admin-link:hover { color: #c084fc; text-decoration: underline; }
    </style>
</head>
<body>

    <div class="login-left">
        <div class="logo-area">🛡️ Axero<span>Core.net</span></div>
        <div class="hero-text">
            <p style="color: #a78bfa; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Threat Intelligence, made useful</p>
            <h2>Your investigations<br>are waiting.</h2>
            <p>Search breach records, stealer intelligence, and open-source data in one focused view.</p>
            
            <div class="steps-box">
                <div class="step-item active">✓ Secure sign in</div>
                <div class="step-item">🔒 Resume your investigations</div>
                <div class="step-item">⚡ Keep monitoring what matters</div>
            </div>
        </div>
        <div style="font-size: 11px; color: #475569;">AxeroCore.net Security Infrastructure</div>
    </div>

    <div class="login-right">
        <h1>Welcome back</h1>
        
        <div class="social-logins">
            <div class="social-btn">Google</div>
            <div class="social-btn">GitHub</div>
            <div class="social-btn">Discord</div>
        </div>

        <div class="divider"><span>OR</span></div>

        <form action="/login" method="POST">
            <div class="input-group">
                <label>Lisans Anahtarı veya Kullanıcı Adı</label>
                <input type="text" name="license_key" placeholder="Lisans Anahtarınızı Girin..." required>
            </div>
            <button type="submit" class="btn-signin">Sign in →</button>
        </form>
        {ERROR_MSG}
        <a href="/admin-login" class="admin-link">🔒 Admin Paneline Git</a>
    </div>

</body>
</html>
"""

HTML_ADMIN_LOGIN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - Admin Girişi</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #07030d; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: rgba(30, 20, 50, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(244, 63, 94, 0.2); padding: 40px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.8); width: 380px; text-align: center; }
        h1 { color: #f43f5e; margin-bottom: 10px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid rgba(244, 63, 94, 0.3); background: #0f071f; color: #fff; box-sizing: border-box; outline: none; }
        button { width: 100%; background: #f43f5e; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; }
        button:hover { background: #e11d48; box-shadow: 0 0 15px rgba(244, 63, 94, 0.6); }
        .error { color: #f43f5e; font-size: 13px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Admin Paneli 🔒</h1>
        <p style="color:#94a3b8; font-size:14px;">Yönetici Şifresini Girin</p>
        <form action="/admin-auth" method="POST">
            <input type="password" name="admin_pass" placeholder="Admin Şifresi..." required>
            <button type="submit">Giriş Yap</button>
        </form>
        {ERROR_MSG}
    </div>
</body>
</html>
"""

HTML_ADMIN_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - Key Yönetim Paneli</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #090514; color: #f8fafc; margin: 0; padding: 30px; }
        .container { max-width: 800px; margin: auto; background: rgba(30, 20, 50, 0.7); backdrop-filter: blur(16px); border: 1px solid rgba(168, 85, 247, 0.2); padding: 30px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.8); }
        h1 { color: #f43f5e; text-align: center; }
        .form-group { margin-bottom: 20px; text-align: center; }
        select, button { padding: 12px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.3); background: #0f071f; color: #fff; font-size: 16px; }
        button { background: #10b981; cursor: pointer; font-weight: bold; border: none; }
        button:hover { background: #059669; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0f071f; border-radius: 8px; overflow: hidden; }
        th, td { padding: 14px; border-bottom: 1px solid rgba(168, 85, 247, 0.1); text-align: left; font-size: 14px; }
        th { background: rgba(168, 85, 247, 0.2); color: #c084fc; }
        .back-link { color: #c084fc; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Ana Sayfaya Dön</a>
        <h1>🔑 Admin Lisans Üretim Paneli</h1>
        
        <form action="/admin-create-key" method="POST" class="form-group">
            <select name="tier_type">
                <option value="FREE">Free (12 Modül)</option>
                <option value="PRO">Pro (12 Modül)</option>
                <option value="VIP">VIP (13 Modül - Tümü)</option>
            </select>
            <button type="submit">Yeni Lisans Key Üret</button>
        </form>

        <h3>Aktif Lisans Anahtarları</h3>
        <table>
            <tr>
                <th>Lisans Anahtarı</th>
                <th>Paket Türü</th>
                <th>Modül Limiti</th>
            </tr>
            {KEY_LIST_ROWS}
        </table>
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
        
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 40px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); background: rgba(9, 5, 20, 0.9); backdrop-filter: blur(12px); }
        .logo { font-size: 20px; font-weight: bold; color: #fff; display: flex; align-items: center; gap: 8px; }
        .logo span { color: #c084fc; }
        .nav-links { display: flex; gap: 20px; font-size: 14px; color: #94a3b8; align-items: center; }
        .nav-links a { color: #94a3b8; text-decoration: none; transition: 0.2s; }
        .nav-links a:hover { color: #c084fc; }
        .user-badge { background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); padding: 6px 14px; border-radius: 20px; color: #c084fc; font-weight: bold; font-size: 13px; }
        .logout-btn { color: #f43f5e !important; font-weight: bold; }

        .container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        
        .hero { text-align: center; margin-bottom: 30px; }
        .hero h1 { font-size: 38px; color: #fff; margin-bottom: 8px; font-weight: 700; }
        .hero h1 span { color: #c084fc; }
        .hero p { color: #94a3b8; font-size: 14px; }

        .search-card { background: rgba(25, 15, 45, 0.8); backdrop-filter: blur(16px); border: 1px solid rgba(168, 85, 247, 0.3); padding: 25px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); margin-bottom: 30px; }
        .search-box { display: flex; gap: 15px; }
        input[type="text"] { flex: 1; padding: 14px 20px; border-radius: 10px; border: 1px solid rgba(168, 85, 247, 0.3); background: #0f071f; color: #fff; font-size: 15px; outline: none; }
        input[type="text"]:focus { border-color: #c084fc; box-shadow: 0 0 12px rgba(192, 132, 252, 0.4); }
        .btn-search { background: linear-gradient(135deg, #9333ea, #7e22ce); color: white; border: none; padding: 0 30px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 15px; transition: 0.3s; }
        .btn-search:hover { background: linear-gradient(135deg, #a855f7, #9333ea); box-shadow: 0 0 15px rgba(168, 85, 247, 0.6); }

        .modules-section { margin-bottom: 25px; background: rgba(20, 12, 35, 0.5); border: 1px solid rgba(168, 85, 247, 0.1); padding: 20px; border-radius: 14px; }
        .modules-section h3 { color: #c084fc; border-bottom: 1px solid rgba(168, 85, 247, 0.2); padding-bottom: 8px; margin-bottom: 15px; font-size: 15px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        
        .checkbox-label { background: #0f071f; padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.15); font-size: 13px; display: flex; align-items: center; gap: 10px; cursor: pointer; color: #cbd5e1; }
        .checkbox-label:hover { border-color: rgba(168, 85, 247, 0.5); background: rgba(168, 85, 247, 0.05); }
        .checkbox-label input { accent-color: #a855f7; transform: scale(1.1); }
        .checkbox-label.locked { opacity: 0.35; cursor: not-allowed; }

        .results-grid { display: grid; grid-template-columns: 360px 1fr; gap: 20px; margin-top: 30px; }
        .left-widgets { display: flex; flex-direction: column; gap: 20px; }
        
        .widget-card { background: rgba(20, 12, 35, 0.9); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 16px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.6); }
        .widget-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px solid rgba(168, 85, 247, 0.2); padding-bottom: 10px; }
        .widget-title { font-weight: bold; color: #fff; font-size: 15px; display: flex; align-items: center; gap: 8px; }
        
        .ip-sub-box { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }
        .ip-sub-item { background: #0f071f; padding: 12px; border-radius: 10px; border: 1px solid rgba(168, 85, 247, 0.15); font-size: 12px; color: #94a3b8; }
        .ip-sub-item span { color: #fff; font-weight: bold; display: block; margin-top: 4px; font-size: 13px; }

        .discord-profile-preview { background: #0f071f; border-radius: 12px; overflow: hidden; border: 1px solid rgba(168, 85, 247, 0.2); margin-top: 10px; }
        .discord-banner { height: 90px; background: linear-gradient(45deg, #3b0764, #7e22ce); }
        .discord-body { padding: 15px; position: relative; }
        .discord-avatar { width: 55px; height: 55px; border-radius: 50%; border: 3px solid #0f071f; position: absolute; top: -35px; background: #5865f2; }
        .discord-name { font-weight: bold; font-size: 16px; color: #fff; margin-top: 15px; }
        .discord-meta { font-size: 12px; color: #94a3b8; margin-top: 4px; }
        .badge-tag { display: inline-block; background: rgba(168, 85, 247, 0.2); border: 1px solid rgba(168, 85, 247, 0.4); padding: 4px 10px; border-radius: 6px; font-size: 11px; color: #c084fc; margin-top: 10px; font-weight: bold; }

        .right-leaks { background: rgba(20, 12, 35, 0.9); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 16px; padding: 25px; box-shadow: 0 8px 30px rgba(0,0,0,0.6); }
        .right-leaks h3 { color: #f43f5e; margin-top: 0; border-bottom: 1px solid rgba(244, 63, 94, 0.2); padding-bottom: 10px; font-size: 16px; }
        
        pre { background: #0b0414; padding: 20px; border-radius: 12px; text-align: left; overflow-x: auto; color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); font-family: 'Courier New', Courier, monospace; font-size: 13px; line-height: 1.6; }
    </style>
</head>
<body>

    <div class="navbar">
        <div class="logo">🛡️ Axero<span>Core.net</span></div>
        <div class="nav-links">
            <a href="/">Ev</a>
            <a href="#">Fiyatlandırma</a>
            <a href="#">API</a>
            <span class="user-badge">Paket: {TIER_NAME} ({LIMIT_TEXT})</span>
            <a href="/logout" class="logout-btn">Çıkış Yap</a>
        </div>
    </div>

    <div class="container">
        
        <div class="hero">
            <h1>Review your exposure <br><span>AxeroCore.net</span> ile</h1>
            <p>Veri sızıntısı olup olmadığını kontrol etmek için e-posta adreslerini, kullanıcı adlarını ve IP adreslerini inceleyin.</p>
        </div>

        <form action="/sorgula" method="POST">
            <div class="search-card">
                <div class="search-box">
                    <input type="text" name="target" placeholder="e.g. 185.146.115.107 veya kullanıcı adı / Discord ID..." required>
                    <button type="submit" class="btn-search">Aramak →</button>
                </div>
            </div>

            <div class="modules-section">
                <h3>🟢 Temel İstihbarat Modülleri (Free - 12 Modül)</h3>
                <div class="grid">
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ip" checked> IP & Geo Lokasyon</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="whois" checked> Domain Whois Sorgusu</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="dns"> DNS Kayıt Analizi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="subdomain"> Alt Alan Adı (Subdomain)</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="port"> Port Taraması (Temel)</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ssl"> SSL Sertifika Kontrolü</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="http_headers"> HTTP Header Analizi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="robots_txt"> Robots.txt & Sitemap</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="mac_lookup"> MAC Adresi Vendor</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ping_test"> Ping & Latency Testi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="http_status"> HTTP Status Checker</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="asn_lookup"> ASN / ISP Bilgi Sorgu</label>
                </div>
            </div>

            <div class="modules-section">
                <h3>🔵 Orta Düzey İstihbarat (Pro - 12 Modül)</h3>
                <div class="grid">
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_instagram" {PRO_DISABLED}> Instagram Tarama</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_github" {PRO_DISABLED}> GitHub Profil Analizi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_twitter" {PRO_DISABLED}> X (Twitter) Hesap Tarama</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_tiktok" {PRO_DISABLED}> TikTok Profil İnceleme</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_steam" {PRO_DISABLED}> Steam ID & Oyun Geçmişi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_discord" {PRO_DISABLED}> Discord ID & Sunucu</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_reddit" {PRO_DISABLED}> Reddit Hesap Analizi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_telegram" {PRO_DISABLED}> Telegram Kullanıcı Kontrolü</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="domain_history" {PRO_DISABLED}> Domain Geçmişi (Age)</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="mail_server" {PRO_DISABLED}> MX & Mail Sunucu Testi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="security_txt" {PRO_DISABLED}> Security.txt Tarama</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="firewall_detect" {PRO_DISABLED}> WAF / Güvenlik Duvarı</label>
                </div>
            </div>

            <div class="modules-section">
                <h3>⭐ Gelişmiş Tehdit & Sızıntı İstihbaratı (VIP - 13 Modül)</h3>
                <div class="grid">
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="discord_token_lookup" {VIP_DISABLED}> 🤖 Discord Token & Profil</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="cctv_mobese" {VIP_DISABLED}> 🚨 MOBESE & Canlı Kamera</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="leak_email" {VIP_DISABLED}> E-Posta Sızıntı (Leak) DB</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="leak_phone" {VIP_DISABLED}> Telefon Numarası İstihbaratı</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="hash_cracker" {VIP_DISABLED}> Hash Çözümleyici (MD5/SHA)</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="metadata_exif" {VIP_DISABLED}> EXIF & Dosya Analizi</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="wayback" {VIP_DISABLED}> Wayback Machine Arşivi</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="deep_scan" {VIP_DISABLED}> Derin Ağ Tehdit Taraması</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="ip_reputation" {VIP_DISABLED}> IP Blacklist & Spam DB</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="cve_lookup" {VIP_DISABLED}> CVE Güvenlik Açığı Veri</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="ssl_cipher" {VIP_DISABLED}> SSL Cipher Suite Testi</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="dns_sec" {VIP_DISABLED}> DNSSEC Doğrulama Testi</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="full_audit" {VIP_DISABLED}> Tam Otomatik Tehdit Audit</label>
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
                      .replace("{%RESULT_SECTION%}", "")
    return HTMLResponse(content=panel)

@app.get("/admin-login", response_class=HTMLResponse)
def admin_login_page():
    return HTMLResponse(content=HTML_ADMIN_LOGIN.replace("{ERROR_MSG}", ""))

@app.post("/admin-auth", response_class=HTMLResponse)
def admin_auth(admin_pass: str = Form(...)):
    if admin_pass == "yalcin123":
        USER_SESSION["is_admin"] = True
        return RedirectResponse(url="/admin-panel", status_code=303)
    else:
        err = '<div class="error">Hatalı yönetici şifresi!</div>'
        return HTMLResponse(content=HTML_ADMIN_LOGIN.replace("{ERROR_MSG}", err))

@app.get("/admin-panel", response_class=HTMLResponse)
def admin_panel():
    if not USER_SESSION["is_admin"]:
        return RedirectResponse(url="/admin-login", status_code=303)
    
    rows = ""
    for k, v in DATABASE_KEYS.items():
        rows += f"<tr><td><b>{k}</b></td><td>{v['type']}</td><td>{v['limit']} Modül</td></tr>"
        
    page = HTML_ADMIN_PANEL.replace("{KEY_LIST_ROWS}", rows)
    return HTMLResponse(content=page)

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
    else:
        err = '<div class="error">Geçersiz lisans anahtarı!</div>'
        return HTMLResponse(content=HTML_LOGIN.replace("{ERROR_MSG}", err))

@app.get("/logout", response_class=HTMLResponse)
def logout():
    USER_SESSION["logged_in"] = False
    USER_SESSION["is_admin"] = False
    USER_SESSION["key"] = ""
    USER_SESSION["tier"] = ""
    USER_SESSION["limit"] = 0
    return RedirectResponse(url="/", status_code=303)

@app.post("/sorgula", response_class=HTMLResponse)
async def run_osint(target: str = Form(...), modules: list = Form(default=[])):
    if not USER_SESSION["logged_in"]:
        return RedirectResponse(url="/", status_code=303)
        
    results = [f"=== AXEROCORE.NET EXPOSURE INTELLIGENCE RAPORU ==="]
    results.append(f"Aranan Hedef: {target} | Yetki: {USER_SESSION['tier']}")
    results.append(f"Çalıştırılan Modül: {len(modules)}\n" + "="*50)

    clean_target = target.split(":")[0].replace("https://", "").replace("http://", "").strip("/")

    ip_info_html = ""
    discord_info_html = ""

    for mod in modules:
        try:
            if mod == "ip":
                try:
                    ip_addr = socket.gethostbyname(clean_target) if not clean_target.replace('.','').isdigit() else clean_target
                    url = f"http://ip-api.com/json/{ip_addr}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=4) as response:
                        data = json.loads(response.read().decode())
                        if data.get("status") == "success":
                            c_name = data.get('country')
                            c_code = data.get('countryCode')
                            city = data.get('city')
                            region = data.get('regionName')
                            isp = data.get('isp')
                            asn = data.get('as')
                            
                            results.append(f"[🌐 IP İstihbaratı] {ip_addr} -> {c_name} / {city} ({isp})")
                            
                            ip_info_html = f"""
                            <div class="widget-card">
                                <div class="widget-header">
                                    <div class="widget-title">🌐 IP İstihbaratı</div>
                                    <span style="font-size:11px; color:#c084fc;">Konum • ASN</span>
                                </div>
                                <div style="color:#38bdf8; font-weight:bold; font-size:14px; margin-bottom:10px;">📶 {ip_addr}</div>
                                <div class="ip-sub-box">
                                    <div class="ip-sub-item">KONUM ({c_code})<span>{city}, {c_name}</span></div>
                                    <div class="ip-sub-item">SERVİS SAĞLAYICI<span>{isp}</span></div>
                                </div>
                                <div style="margin-top:10px; font-size:12px; color:#94a3b8;">ASN: <span>{asn}</span></div>
                            </div>
                            """
                except:
                    pass

            elif mod == "discord_token_lookup" or mod == "social_discord":
                user_id = clean_target.strip()
                if user_id.isdigit():
                    try:
                        url = f"https://discordlookup.mesalabs.org/v1/user/{user_id}"
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=4) as response:
                            data = json.loads(response.read().decode())
                            uname = data.get('username')
                            gname = data.get('global_name', 'Bilinmiyor')
                            avatar = f"https://cdn.discordapp.com/avatars/{user_id}/{data.get('avatar', '')}.png"
                            
                            results.append(f"[🤖 Discord Profil] @{uname} ({gname}) ID: {user_id}")
                            
                            discord_info_html = f"""
                            <div class="widget-card">
                                <div class="widget-header">
                                    <div class="widget-title">💬 Discord Profiles</div>
                                    <span style="font-size:11px; color:#c084fc;">1 profile</span>
                                </div>
                                <div class="discord-profile-preview">
                                    <div class="discord-banner"></div>
                                    <div class="discord-body">
                                        <div class="discord-avatar" style="background-image: url('{avatar}'); background-size: cover;"></div>
                                        <div class="discord-name">{gname}</div>
                                        <div class="discord-meta">@{uname} • ID: {user_id}</div>
                                        <div class="badge-tag">HypeSquad Bravery</div>
                                    </div>
                                </div>
                            </div>
                            """
                    except:
                        pass
            else:
                results.append(f"[{mod.upper()}] Modül başarıyla yürütüldü.")
        except:
            pass

    report = "\n".join(results)

    tier = USER_SESSION["tier"]
    pro_lock = "" if tier in ["PRO", "VIP"] else "locked"
    pro_disabled = "" if tier in ["PRO", "VIP"] else "disabled"
    vip_lock = "" if tier == "VIP" else "locked"
    vip_disabled = "" if tier == "VIP" else "disabled"
    
    result_html = f"""
    <div class="results-grid">
        <div class="left-widgets">
            {ip_info_html}
            {discord_info_html}
        </div>
        <div class="right-leaks">
            <h3>🔍 Veri İhlalleri & İstihbarat Raporu</h3>
            <pre>{report}</pre>
        </div>
    </div>
    """

    panel = HTML_PANEL.replace("{TIER_NAME}", tier)\
                      .replace("{LIMIT_TEXT}", f"{USER_SESSION['limit']} Modül")\
                      .replace("{PRO_LOCK}", pro_lock)\
                      .replace("{PRO_DISABLED}", pro_disabled)\
                      .replace("{VIP_LOCK}", vip_lock)\
                      .replace("{VIP_DISABLED}", vip_disabled)\
                      .replace("{%RESULT_SECTION%}", result_html)
    return HTMLResponse(content=panel)
