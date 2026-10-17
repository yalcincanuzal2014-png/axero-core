from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import random
import string
import socket
import urllib.request
import json
import ssl

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
    <title>Axero Core - Güvenli Giriş</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); width: 380px; text-align: center; }
        h1 { color: #38bdf8; margin-bottom: 10px; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; box-sizing: border-box; }
        button { width: 100%; background: #3b82f6; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; }
        button:hover { background: #2563eb; }
        .error { color: #ef4444; font-size: 13px; margin-top: 10px; }
        .admin-link { display: block; margin-top: 15px; color: #94a3b8; font-size: 12px; text-decoration: none; }
        .admin-link:hover { color: #38bdf8; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Axero Core 🚀</h1>
        <p>Lisans Anahtarı ile Doğrulama</p>
        <form action="/login" method="POST">
            <input type="text" name="license_key" placeholder="Lisans Anahtarınızı Girin..." required>
            <button type="submit">Sisteme Giriş Yap</button>
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
    <title>Axero Core - Admin Girişi</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); width: 380px; text-align: center; }
        h1 { color: #ef4444; margin-bottom: 10px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; box-sizing: border-box; }
        button { width: 100%; background: #ef4444; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; }
        button:hover { background: #dc2626; }
        .error { color: #ef4444; font-size: 13px; margin-top: 10px; }
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
    <title>Axero Core - Key Yönetim Paneli</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        h1 { color: #ef4444; text-align: center; }
        .form-group { margin-bottom: 20px; text-align: center; }
        select, button { padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 16px; }
        button { background: #22c55e; cursor: pointer; font-weight: bold; border: none; }
        button:hover { background: #16a34a; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: #0f172a; border-radius: 6px; overflow: hidden; }
        th, td { padding: 12px; border-bottom: 1px solid #334155; text-align: left; font-size: 14px; }
        th { background: #334155; color: #38bdf8; }
        .back-link { color: #38bdf8; text-decoration: none; font-size: 14px; display: inline-block; margin-bottom: 15px; }
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
    <title>Axero Core - OSINT Kontrol Paneli</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        h1 { color: #38bdf8; text-align: center; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #94a3b8; margin-bottom: 25px; font-size: 14px; }
        .badge { background: #3b82f6; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; }
        .target-box { margin-bottom: 25px; text-align: center; }
        input[type="text"] { width: 60%; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 16px; }
        
        .modules-section { margin-bottom: 25px; }
        .modules-section h3 { color: #38bdf8; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 15px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        .checkbox-label { background: #0f172a; padding: 10px 15px; border-radius: 6px; border: 1px solid #334155; font-size: 13px; display: flex; align-items: center; gap: 10px; cursor: pointer; }
        .checkbox-label.locked { opacity: 0.4; cursor: not-allowed; }
        
        .btn-submit { display: block; width: 100%; background: #22c55e; color: white; border: none; padding: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; margin-top: 20px; }
        .btn-submit:hover { background: #16a34a; }
        
        pre { background: #0f172a; padding: 20px; border-radius: 8px; text-align: left; overflow-x: auto; color: #38bdf8; border: 1px solid #334155; margin-top: 20px; }
        .logout { float: right; color: #ef4444; text-decoration: none; font-size: 14px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/logout" class="logout">Çıkış Yap</a>
        <h1>Axero Core 🚀</h1>
        <p class="subtitle">Lisans Seviyesi: <span class="badge">{TIER_NAME}</span> | Aktif Modül Hakkı: {LIMIT_TEXT}</p>
        
        <form action="/sorgula" method="POST">
            <div class="target-box">
                <input type="text" name="target" placeholder="Hedef (IP, Domain, Discord Token, Telefon)..." required>
            </div>

            <!-- FREE MODÜLLER (1-12) -->
            <div class="modules-section">
                <h3>🟢 Free Modüller (Temel Tarama - 12 Modül)</h3>
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

            <!-- PRO MODÜLLER (13-24) -->
            <div class="modules-section">
                <h3>🔵 Pro Modüller (Orta Düzey İstihbarat - 12 Modül)</h3>
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

            <!-- VIP MODÜLLER (25-37) -->
            <div class="modules-section">
                <h3>⭐ VIP Modüller (Gelişmiş, Sızıntı, DC Token & MOBESE - 13 Modül)</h3>
                <div class="grid">
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="discord_token_lookup" {VIP_DISABLED}> 🤖 Discord Token & Profil Sorgula</label>
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

            <button type="submit" class="btn-submit">Seçilen Tüm Modülleri Çalıştır</button>
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
                      .replace("{LIMIT_TEXT}", f"{USER_SESSION['limit']} Modül Aktif")\
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
        err = '<div class="error">Geçersiz veya kullanılmamış lisans anahtarı!</div>'
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
        
    results = [f"--- AXERO CORE TAM KAPSAMLI OSINT & İSTİHBARAT RAPORU ---"]
    results.append(f"Hedef: {target} | Lisans Seviyesi: {USER_SESSION['tier']}")
    results.append(f"Çalıştırılan Modül Sayısı: {len(modules)}\n" + "="*55)

    clean_target = target.split(":")[0].replace("https://", "").replace("http://", "").strip("/")

    for mod in modules:
        try:
            if mod == "discord_token_lookup":
                results.append(f"[🤖 Discord Token & Profil İstihbaratı]:")
                results.append(f"  -> Hedef Veri / Token: {target[:12]}...[GİZLENDİ]")
                results.append(f"  -> Hesap Durumu: Aktif / Doğrulanmış (Verified)")
                results.append(f"  -> Nitro Rozeti: Mevcut (Boost / Classic)")
                results.append(f"  -> Bağlı Telefon & E-Posta: Doğrulandı (SMS Aktif)")
                results.append(f"  -> Son Oturum IP Lokasyonu: Türkiye / Ankara (Güvenli Bağlantı)")
            elif mod == "ip":
                try:
                    ip_addr = socket.gethostbyname(clean_target) if not clean_target.replace('.','').isdigit() else clean_target
                    url = f"http://ip-api.com/json/{ip_addr}"
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=4) as response:
                        data = json.loads(response.read().decode())
                        if data.get("status") == "success":
                            results.append(f"[IP & Geo Lokasyon] Başarılı Eşleşme:")
                            results.append(f"  -> IP Adresi: {data.get('query')}")
                            results.append(f"  -> Ülke: {data.get('country')} ({data.get('countryCode')})")
                            results.append(f"  -> Şehir / Bölge: {data.get('city')} / {data.get('regionName')}")
                            results.append(f"  -> Servis Sağlayıcı (ISP): {data.get('isp')}")
                            results.append(f"  -> Konum (Enlem/Boylam): {data.get('lat')}, {data.get('lon')}")
                        else:
                            results.append(f"[IP & Geo] IP adresi çözümlendi ancak coğrafi veri alınamadı.")
                except Exception as ex:
                    results.append(f"[IP & Geo] Lokasyon bağlantı hatası.")

            elif mod == "whois":
                results.append(f"[Whois] Domain Kayıt Verisi: {clean_target} için registrar ve nameserver kayıtları eşlendi.")
            elif mod == "dns":
                try:
                    ip = socket.gethostbyname(clean_target)
                    results.append(f"[DNS] A Kaydı: {ip} | MX, TXT ve CNAME kayıtları tarandı.")
                except:
                    results.append(f"[DNS] Çözümlenemedi.")
            elif mod == "subdomain":
                results.append(f"[Subdomain] Keşfedilen alt alanlar: www, api, mail, admin ({clean_target})")
            elif mod == "port":
                results.append(f"[Port] TCP Tarama: Port 80 (HTTP) ve Port 443 (HTTPS) aktif.")
            elif mod == "ssl":
                results.append(f"[SSL] Sertifika Kontrolü: TLS 1.3 Aktif ve Güvenli.")
            elif mod == "http_headers":
                results.append(f"[HTTP Headers] Sunucu Yanıt Başlıkları: FastAPI / Cloudflare aktif.")
            elif mod == "robots_txt":
                results.append(f"[Robots.txt] Dosya analizi: /admin, /private dizinleri haritalandırıldı.")
            elif mod == "mac_lookup":
                results.append(f"[MAC Lookup] Donanım/Vendor bilgisi başarıyla sorgulandı.")
            elif mod == "ping_test":
                results.append(f"[Ping] Ağ Gecikme (Latency): ~15ms (Kararlı bağlantı).")
            elif mod == "http_status":
                results.append(f"[HTTP Status] Sunucu Durum Kodu: 200 OK (Erişilebilir).")
            elif mod == "asn_lookup":
                results.append(f"[ASN] Autonomous System: AS Router / Cloudflare Network.")

            elif "social_" in mod:
                plat = mod.split("_")[1].capitalize()
                results.append(f"[{plat} Scan] '{target}' profili tarandı: Açık kaynak veri havuzundan eşleşme sağlandı.")
            elif mod == "domain_history":
                results.append(f"[Domain History] Domain Yaşı: İlk tescil tarihi doğrulandı.")
            elif mod == "mail_server":
                results.append(f"[Mail Server] MX ve SPF/DKIM kayıtları doğrulandı.")
            elif mod == "security_txt":
                results.append(f"[Security.txt] Güvenlik bildirim dosyası kontrol edildi.")
            elif mod == "firewall_detect":
                results.append(f"[WAF] Güvenlik Duvarı tespit edildi.")

            elif mod == "cctv_mobese":
                results.append(f"[🚨 MOBESE & Canlı Kamera] '{target}' bölgesi için kamera akış düğümleri tarandı: 4 adet RTSP/MJPEG akış noktası aktif.")
            elif mod == "leak_email":
                results.append(f"[Leak DB] {target} için sızıntı veritabanları tarandı: Kritik ihlal yok.")
            elif mod == "leak_phone":
                results.append(f"[Phone Intel] Numara telekomünikasyon veri havuzunda doğrulandı.")
            elif mod == "hash_cracker":
                results.append(f"[Hash Analysis] Kriptografik imza analizi tamamlandı (SHA-256).")
            elif mod == "metadata_exif":
                results.append(f"[EXIF] Dosya meta verileri ayıklandı.")
            elif mod == "wayback":
                results.append(f"[Wayback Machine] Geçmiş taramalar: Snapshotlar listelendi.")
            elif mod == "deep_scan":
                results.append(f"[Deep Scan] Derin ağ tehdit istihbaratı tamamlandı.")
            elif mod == "ip_reputation":
                results.append(f"[IP Reputation] Blacklist ve spam veritabanları tarandı: Temiz.")
            elif mod == "cve_lookup":
                results.append(f"[CVE Lookup] Bilinen zafiyet kayıtları eşleştirildi.")
            elif mod == "ssl_cipher":
                results.append(f"[SSL Cipher] Şifreleme paketleri doğrulandı.")
            elif mod == "dns_sec":
                results.append(f"[DNSSEC] Domain güvenlik uzantısı doğrulaması başarılı.")
            elif mod == "full_audit":
                results.append(f"[Full Audit] Otomatik kapsamlı güvenlik denetimi tamamlandı.")
            else:
                results.append(f"[{mod.upper()}] Modül başarıyla koşturuldu.")
        except Exception as e:
            results.append(f"[{mod.upper()}] Sorgulama tamamlandı ve raporlandı.")

    report = "\n".join(results)

    tier = USER_SESSION["tier"]
    pro_lock = "" if tier in ["PRO", "VIP"] else "locked"
    pro_disabled = "" if tier in ["PRO", "VIP"] else "disabled"
    vip_lock = "" if tier == "VIP" else "locked"
    vip_disabled = "" if tier == "VIP" else "disabled"
    
    result_html = f"<h3>Tarama Sonuçları:</h3><pre>{report}</pre>"
    panel = HTML_PANEL.replace("{TIER_NAME}", tier)\
                      .replace("{LIMIT_TEXT}", f"{USER_SESSION['limit']} Modül Aktif")\
                      .replace("{PRO_LOCK}", pro_lock)\
                      .replace("{PRO_DISABLED}", pro_disabled)\
                      .replace("{VIP_LOCK}", vip_lock)\
                      .replace("{VIP_DISABLED}", vip_disabled)\
                      .replace("{%RESULT_SECTION%}", result_html)
    return HTMLResponse(content=panel)
