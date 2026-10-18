from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
import random
import string
import sqlite3
import socket
import urllib.request
import json
import dns.resolver

app = FastAPI()

# SQLite Veritabanı Otomatik Kurulumu
def init_db():
    conn = sqlite3.connect("axero_leak.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT UNIQUE,
            target_type TEXT,
            discord_id TEXT,
            password TEXT,
            password_hash TEXT,
            token TEXT,
            ip_address TEXT,
            email TEXT,
            phone TEXT,
            isp TEXT
        )
    """)
    # Test için örnek Discord ID kaydı
    cursor.execute("""
        INSERT OR IGNORE INTO leaks (target, target_type, discord_id, password, password_hash, token, ip_address, email, phone, isp)
        VALUES ('826161709538476094', 'Discord ID', '826161709538476094', 'axero2026!', '$2y$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'OTg5MjQzODEzNj...X91a', '185.156.60.22', 'yalcin@axerocore.net', '+90 555 444 3322', 'Türk Telekom')
    """)
    conn.commit()
    conn.close()

init_db()

DATABASE_KEYS = {
    "AXERO-MASTER-ADMIN-KEY": {"type": "VIP", "limit": 37},
    "AXERO-PRO-TESTKEY": {"type": "PRO", "limit": 24}
}

USER_SESSION = {"logged_in": False, "key": "", "tier": "VIP", "limit": 37, "is_admin": False}
GLOBAL_STATS = {"total_scans": 1680, "nodes_active": 37}

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
    </style>
</head>
<body>
    <div class="login-left">
        <div class="logo-area">🛡️ Axero<span>Core.net</span></div>
        <div class="hero-text">
            <h2>AxeroCore SQLite<br>Leak DB Engine</h2>
            <p>Real-time database querying and intelligence platform.</p>
        </div>
        <div style="font-size: 11px; color: #475569;">AxeroCore.net Secure Gateway</div>
    </div>
    <div class="login-right">
        <h1>Giriş Yap</h1>
        <form action="/login" method="POST">
            <div class="input-group">
                <label>Lisans Anahtarı</label>
                <input type="text" name="license_key" placeholder="Lisans Anahtarınızı Girin..." required>
            </div>
            <button type="submit" class="btn-signin">Sisteme Giriş →</button>
        </form>
        <a href="/oauth-login?provider=FreeGuest" class="btn-free">🚀 Tek Tıkla VIP Oturum Aç</a>
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
    <title>AxeroCore.net - SQLite Leak Platform</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: radial-gradient(circle at 50% 10%, #1c0e38 0%, #090514 80%); color: #f8fafc; margin: 0; padding: 0; min-height: 100vh; }
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 40px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); background: rgba(9, 5, 20, 0.9); }
        .logo { font-size: 20px; font-weight: bold; color: #fff; text-decoration: none; display: flex; gap: 8px; }
        .logo span { color: #c084fc; }
        .nav-links { display: flex; gap: 20px; font-size: 14px; align-items: center; }
        .nav-links a { color: #94a3b8; text-decoration: none; }
        .user-badge { background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); padding: 6px 14px; border-radius: 20px; color: #c084fc; font-weight: bold; font-size: 13px; }
        .container { max-width: 1100px; margin: 40px auto; padding: 0 20px; }
        
        .search-pill-container { background: rgba(20, 12, 35, 0.85); border: 1px solid rgba(168, 85, 247, 0.35); padding: 10px 14px; border-radius: 40px; display: flex; align-items: center; margin-bottom: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }
        .pill-input { flex: 1; background: transparent; border: none; color: #fff; font-size: 15px; outline: none; padding: 0 10px; }
        .pill-search-btn { background: linear-gradient(135deg, #9333ea, #7e22ce); color: white; border: none; padding: 12px 28px; border-radius: 30px; cursor: pointer; font-weight: bold; font-size: 14px; }
        
        .terminal-box { background: #040208; border: 1px solid rgba(56, 189, 248, 0.4); border-radius: 14px; padding: 20px; margin-bottom: 25px; font-family: monospace; font-size: 13px; color: #38bdf8; max-height: 180px; overflow-y: auto; }
        .terminal-box .line { margin-bottom: 5px; }

        .dashboard-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 30px; }
        .dash-card { background: rgba(20, 12, 35, 0.9); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 14px; padding: 20px; }
        .dash-card h4 { color: #c084fc; margin: 0 0 10px 0; font-size: 14px; display: flex; justify-content: space-between; align-items: center; }
        .dash-value { font-size: 18px; font-weight: bold; color: #fff; margin-bottom: 5px; word-break: break-all; }
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
            <span class="user-badge">SQLite DB Bağlı ({TIER_NAME})</span>
            <a href="/logout" style="color: #f43f5e; font-weight: bold;">Çıkış Yap</a>
        </div>
    </div>

    <div class="container">
        <form action="/sorgula" method="POST">
            <div class="search-pill-container">
                <div style="color: #c084fc; font-size: 18px; margin-left: 10px;">🔍</div>
                <input type="text" name="target" class="pill-input" placeholder="Veritabanında aranacak Discord ID, E-posta veya IP girin..." required>
                <button type="submit" class="pill-search-btn">SQLite DB Ara →</button>
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
    panel = HTML_PANEL.replace("{TIER_NAME}", USER_SESSION["tier"]).replace("{%RESULT_SECTION%}", "")
    return HTMLResponse(content=panel)

@app.get("/oauth-login", response_class=HTMLResponse)
def oauth_login(provider: str):
    USER_SESSION["logged_in"] = True
    USER_SESSION["tier"] = "VIP"
    return RedirectResponse(url="/", status_code=303)

@app.post("/login", response_class=HTMLResponse)
def login(license_key: str = Form(...)):
    USER_SESSION["logged_in"] = True
    USER_SESSION["tier"] = "VIP"
    return RedirectResponse(url="/", status_code=303)

@app.get("/logout", response_class=HTMLResponse)
def logout():
    USER_SESSION["logged_in"] = False
    return RedirectResponse(url="/", status_code=303)

@app.post("/sorgula", response_class=HTMLResponse)
async def run_osint(target: str = Form(...)):
    if not USER_SESSION["logged_in"]:
        return RedirectResponse(url="/", status_code=303)
        
    target_clean = target.strip()
    GLOBAL_STATS["total_scans"] += 1

    # SQLite Veritabanından Sorgu Yapma
    conn = sqlite3.connect("axero_leak.db")
    cursor = conn.cursor()
    cursor.execute("SELECT target_type, discord_id, password, password_hash, token, ip_address, email, phone, isp FROM leaks WHERE target = ?", (target_clean,))
    row = cursor.fetchone()
    conn.close()

    cards_html = ""
    details_html = ""
    terminal_logs = f"""
    <div class="line">[+] AxeroCore SQLite DB Engine connected...</div>
    <div class="line">[+] Executing SQL query for target: {target_clean}</div>
    """

    if row:
        target_type, d_id, pwd, pwd_hash, token, ip, email, phone, isp = row
        terminal_logs += f'<div class="line" style="color: #10b981;">[✓] MATCH FOUND in axero_leak.db!</div>'
        
        cards_html = f"""
        <div class="dash-card">
            <h4>Discord ID <span>🔥 Eşleşti</span></h4>
            <div class="dash-value">{d_id}</div>
            <div class="dash-desc">Veritabanı Kaydı Doğrulandı</div>
        </div>
        <div class="dash-card">
            <h4>Şifre & Hash <span>🔑</span></h4>
            <div class="dash-value">{pwd}</div>
            <div class="dash-desc">Hash: {pwd_hash[:20]}...</div>
        </div>
        <div class="dash-card">
            <h4>IP & İletişim <span>🌐</span></h4>
            <div class="dash-value">{ip}</div>
            <div class="dash-desc">ISP: {isp} | Tel: {phone}</div>
        </div>
        """
        details_html = f"""
        <div class="result-item"><b>[LEAK_DB]</b> Hedef: {target_clean} | Şifre: {pwd} | Token: {token} | E-Posta: {email} | IP: {ip}</div>
        """
    else:
        terminal_logs += f'<div class="line" style="color: #f43f5e;">[!] No record found in SQLite database for: {target_clean}</div>'
        cards_html = """
        <div class="dash-card">
            <h4>Sorgu Sonucu <span>⚠️</span></h4>
            <div class="dash-value">Kayıt Bulunamadı</div>
            <div class="dash-desc">Bu hedef veritabanında mevcut değil.</div>
        </div>
        """
        details_html = f"""<div class="result-item"><b>[NOT_FOUND]</b> '{target_clean}' için veritabanında eşleşen kayıt bulunamadı.</div>"""

    result_section = f"""
    <div class="terminal-box">
        <div style="color: #f43f5e; margin-bottom: 8px; font-weight: bold;">🚨 AxeroCore SQLite LeakDB Stream</div>
        {terminal_logs}
    </div>
    <div class="dashboard-grid">{cards_html}</div>
    <div class="result-details-box">
        <h3>
            <span>🔍 SQLite Veritabanı Eşleşme Raporu ({target_clean})</span>
            <a href="/download-report?target={target_clean}" class="btn-download" target="_blank">📥 Raporu İndir (.txt)</a>
        </h3>
        {details_html}
    </div>
    """

    panel = HTML_PANEL.replace("{TIER_NAME}", USER_SESSION["tier"]).replace("{%RESULT_SECTION%}", result_section)
    return HTMLResponse(content=panel)

@app.get("/download-report", response_class=PlainTextResponse)
def download_report(target: str):
    conn = sqlite3.connect("axero_leak.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leaks WHERE target = ?", (target,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return f"AXEROCORE SQLITE LEAK REPORT\nTarget: {target}\nData Found: {row}"
    return "Record not found."
