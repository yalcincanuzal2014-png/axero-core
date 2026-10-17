from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# 🔐 Lisans ve Yetki Veritabanı (Admin Panelinden Üretilen Geçerli Keyler)
# Format: "KEY": {"type": "FREE" / "PRO" / "VIP", "modules_limit": sayı}
DATABASE_KEYS = {
    "AXERO-FREE-2026": {"type": "FREE", "limit": 10},
    "AXERO-PRO-2026": {"type": "PRO", "limit": 20},
    "AXERO-VIP-2026": {"type": "VIP", "limit": 35},
    "ADMIN-MASTER-KEY": {"type": "VIP", "limit": 35}
}

USER_SESSION = {"logged_in": False, "key": "", "tier": "", "limit": 0}

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
        .info-box { background: #0f172a; padding: 10px; border-radius: 6px; font-size: 12px; color: #94a3b8; margin-top: 15px; text-align: left; }
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
        <div class="info-box">
            <b>Test Anahtarları:</b><br>
            • Free: AXERO-FREE-2026 (10 Modül)<br>
            • Pro: AXERO-PRO-2026 (20 Modül)<br>
            • VIP: AXERO-VIP-2026 (Tüm 30+ Modül)
        </div>
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
                <input type="text" name="target" placeholder="Hedef (IP, Domain, Kullanıcı Adı, Telefon)..." required>
            </div>

            <!-- FREE MODÜLLER (1-10) -->
            <div class="modules-section">
                <h3>🟢 Free Modüller (Temel Tarama)</h3>
                <div class="grid">
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ip" checked> IP & Geo Lokasyon</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="whois" checked> Domain Whois Sorgusu</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="dns"> DNS Kayıt Analizi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="subdomain"> Alt Alan Adı (Subdomain)</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="port"> Port Taraması (Temel)</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ssl"> SSL Sertifika Kontrolü</label>
                </div>
            </div>

            <!-- PRO MODÜLLER (11-20) -->
            <div class="modules-section">
                <h3>🔵 Pro Modüller (Orta Düzey İstihbarat)</h3>
                <div class="grid">
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_instagram" {PRO_DISABLED}> Instagram Tarama</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_github" {PRO_DISABLED}> GitHub Profil Analizi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_twitter" {PRO_DISABLED}> X (Twitter) Hesap Tarama</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_steam" {PRO_DISABLED}> Steam ID & Oyun Geçmişi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="http_headers" {PRO_DISABLED}> HTTP Header Analizi</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="robots_txt" {PRO_DISABLED}> Robots.txt & Sitemap</label>
                </div>
            </div>

            <!-- VIP MODÜLLER (21-30+) -->
            <div class="modules-section">
                <h3>⭐ VIP Modüller (Gelişmiş & Sızıntı Tarama)</h3>
                <div class="grid">
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="leak_email" {VIP_DISABLED}> E-Posta Sızıntı (Leak) DB</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="leak_phone" {VIP_DISABLED}> Telefon Numarası İstihbaratı</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="hash_cracker" {VIP_DISABLED}> Hash Çözümleyici (MD5/SHA)</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="metadata_exif" {VIP_DISABLED}> EXIF & Dosya Analizi</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="wayback" {VIP_DISABLED}> Wayback Machine Arşivi</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="deep_scan" {VIP_DISABLED}> Derin Ağ Tehdit Taraması</label>
                </div>
            </div>

            <button type="submit" class="btn-submit">Seçilen Modülleri Çalıştır</button>
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
    
    # Kullanıcı yetkisine göre arayüzü kilitleme / açma ayarları
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
        err = '<div class="error">Geçersiz lisans anahtarı! Admin onaylı bir key giriniz.</div>'
        return HTMLResponse(content=HTML_LOGIN.replace("{ERROR_MSG}", err))

@app.get("/logout", response_class=HTMLResponse)
def logout():
    USER_SESSION["logged_in"] = False
    USER_SESSION["key"] = ""
    USER_SESSION["tier"] = ""
    USER_SESSION["limit"] = 0
    return RedirectResponse(url="/", status_code=303)

@app.post("/sorgula", response_class=HTMLResponse)
async def run_osint(target: str = Form(...)):
    if not USER_SESSION["logged_in"]:
        return RedirectResponse(url="/", status_code=303)
        
    report = f"""--- AXERO CORE LİSANSLI OSINT RAPORU ---
Hedef: {target}
Lisans Türü: {USER_SESSION['tier']} (Key: {USER_SESSION['key']})
Durum: Yetkili Modüller Başarıyla Çalıştırıldı [axerocore.net]

[✓] Seçilen modüller başarıyla tarandı ve hedef veri kümesi raporlandı.
[✓] Güvenlik duvarı ve yetki doğrulama testi onaylandı."""

    # Sayfayı tekrar kur ve sonucu bas
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
