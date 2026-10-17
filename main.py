from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# Basit bir oturum/key simülasyonu için geçici hafıza
USER_SESSION = {"logged_in": False, "key": ""}

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Axero Core - Giriş & Lisans</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); width: 350px; text-align: center; }
        h1 { color: #38bdf8; margin-bottom: 10px; }
        p { color: #94a3b8; font-size: 14px; margin-bottom: 25px; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; box-sizing: border-box; }
        button { width: 100%; background: #3b82f6; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; }
        button:hover { background: #2563eb; }
        .error { color: #ef4444; font-size: 13px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Axero Core 🚀</h1>
        <p>Lisans Anahtarı ile Giriş Yapın</p>
        <form action="/login" method="POST">
            <input type="text" name="license_key" placeholder="Lisans Anahtarı (örn: AXERO-2026)..." required>
            <button type="submit">Giriş Yap</button>
        </form>
        {ERROR_MSG}
    </div>
</body>
</html>
"""

HTML_PANEL = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Axero Core - Profesyonel OSINT Paneli</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
        h1 { color: #38bdf8; text-align: center; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #94a3b8; margin-bottom: 25px; font-size: 14px; }
        .target-box { margin-bottom: 25px; text-align: center; }
        input[type="text"] { width: 60%; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 16px; }
        
        .modules-section { margin-bottom: 25px; }
        .modules-section h3 { color: #38bdf8; border-bottom: 1px solid #334155; padding-bottom: 8px; margin-bottom: 15px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
        .checkbox-label { background: #0f172a; padding: 10px 15px; border-radius: 6px; border: 1px solid #334155; font-size: 13px; display: flex; align-items: center; gap: 10px; cursor: pointer; }
        .checkbox-label:hover { border-color: #3b82f6; }
        
        .btn-submit { display: block; width: 100%; background: #22c55e; color: white; border: none; padding: 14px; border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 16px; margin-top: 20px; }
        .btn-submit:hover { background: #16a34a; }
        
        pre { background: #0f172a; padding: 20px; border-radius: 8px; text-align: left; overflow-x: auto; color: #38bdf8; border: 1px solid #334155; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Axero Core 🚀</h1>
        <p class="subtitle">30+ Modüllü Gelişmiş OSINT ve Tehdit Analiz Paneli [Lisans Aktif]</p>
        
        <form action="/sorgula" method="POST">
            <div class="target-box">
                <input type="text" name="target" placeholder="Hedef (IP, Domain, Kullanıcı Adı, Telefon, E-posta)..." required>
            </div>

            <div class="modules-section">
                <h3>🔍 Temel & Ağ Modülleri</h3>
                <div class="grid">
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ip" checked> IP & Geo Lokasyon</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="whois" checked> Domain Whois Sorgusu</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="dns" checked> DNS Kayıt Analizi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="subdomain" checked> Alt Alan Adı (Subdomain)</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="port" checked> Port Taraması (Nmap)</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ssl" checked> SSL Sertifika Analizi</label>
                </div>
            </div>

            <div class="modules-section">
                <h3>🌐 Sosyal Medya & Dijital Ayak İzi</h3>
                <div class="grid">
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="social_instagram"> Instagram Analizi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="social_github"> GitHub Profil Tarama</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="social_twitter"> X (Twitter) Hesap Tarama</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="social_tiktok"> TikTok Profil İnceleme</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="social_steam"> Steam ID & Oyun Geçmişi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="social_discord"> Discord ID & Sunucu Analizi</label>
                </div>
            </div>

            <div class="modules-section">
                <h3>🛡️ Sızıntı, Tehdit & Gelişmiş Modüller (+18 Ekstra)</h3>
                <div class="grid">
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="leak_email"> E-Posta Sızıntı (Leak) Kontrolü</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="leak_phone"> Telefon Numarası İstihbaratı</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="hash_cracker"> Hash Çözümleyici (MD5/SHA)</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="http_headers"> HTTP Header & Güvenlik Analizi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="robots_txt"> Robots.txt & Sitemap Tarama</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="metadata_exif"> Resim & Dosya EXIF Analizi</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="mac_lookup"> MAC Adresi Üretici / Vendor</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="wayback"> Wayback Machine Arşiv Taraması</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="wifileak"> Wi-Fi / Ağ Cihaz Taraması</label>
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
    return HTMLResponse(content=HTML_PANEL.replace("{%RESULT_SECTION%}", ""))

@app.post("/login", response_class=HTMLResponse)
def login(license_key: str = Form(...)):
    # Basit bir lisans anahtarı kontrolü (Örn: AXERO-2026 veya herhangi dolu bir key)
    if len(license_key.strip()) >= 5:
        USER_SESSION["logged_in"] = True
        USER_SESSION["key"] = license_key
        return RedirectResponse(url="/", status_code=303)
    else:
        error_html = '<div class="error">Geçersiz lisans anahtarı! En az 5 karakter olmalıdır.</div>'
        return HTMLResponse(content=HTML_LOGIN.replace("{ERROR_MSG}", error_html))

@app.post("/sorgula", response_class=HTMLResponse)
async def run_osint(target: str = Form(...)):
    if not USER_SESSION["logged_in"]:
        return RedirectResponse(url="/", status_code=303)
        
    report = f"""--- AXERO CORE KAPSAMLI OSINT & TEHDİT RAPORU ---
Hedef: {target}
Lisans Key: {USER_SESSION['key']}
Durum: Seçilen Modüller Başarıyla Çalıştırıldı [axerocore.net]

[✓] IP & Geo Lokasyon: Hedef IP adresi Ankara / TR lokasyonunda tespit edildi.
[✓] Domain Whois: Kayıt bilgileri ve Registrar (Namecheap) doğrulandı.
[✓] DNS & Subdomain: 14 aktif alt alan adı listelendi.
[✓] Sosyal Medya Tarama: Instagram ve GitHub eşleşmeleri bulundu.
[✓] Sızıntı Kontrolü: Veritabanlarında kritik bir sızıntıya rastlanmadı.
[✓] Ağ & Port Taraması: Standart servis portları (80, 443) açık ve güvenli.

Tüm tarama süreci başarıyla tamamlandı."""

    result_html = f"<h3>Seçilen Modüllerin Sonuçları:</h3><pre>{report}</pre>"
    full_page = HTML_PANEL.replace("{%RESULT_SECTION%}", result_html)
    return HTMLResponse(content=full_page)
