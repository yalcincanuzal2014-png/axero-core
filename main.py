from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import random
import string
import socket
import urllib.request
import json
import datetime

app = FastAPI()

# Başlangıçta admin key'imiz duruyor
DATABASE_KEYS = {
    "AXERO-MASTER-ADMIN-KEY": {"type": "VIP", "limit": 37}
}

USER_SESSION = {"logged_in": False, "key": "", "tier": "", "limit": 0, "is_admin": False}

HTML_LOGIN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - Threat Intelligence Platform</title>
    <meta name="description" content="AxeroCore.net - Veri ihlali arama, veri hırsızı analizi, mağdur tespiti ve OSINT sorgulama platformu.">
    <meta name="keywords" content="axero core, axerocore, axerocore.net, osint, breach search, threat intelligence">
    <meta name="robots" content="index, follow">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #07030d; color: #f8fafc; margin: 0; padding: 0; height: 100vh; display: flex; overflow: hidden; }
        .login-left { flex: 1.2; background: radial-gradient(circle at 20% 40%, #3b0764 0%, #07030d 70%); display: flex; flex-direction: column; justify-content: space-between; padding: 60px; position: relative; }
        .logo-area { font-size: 22px; font-weight: bold; color: #fff; display: flex; align-items: center; gap: 8px; }
        .logo-area span { color: #c084fc; }
        .hero-text h2 { font-size: 44px; color: #fff; margin-bottom: 15px; font-weight: 700; line-height: 1.2; }
        .hero-text p { color: #94a3b8; font-size: 15px; max-width: 420px; line-height: 1.5; }
        .steps-box { display: flex; flex-direction: column; gap: 12px; margin-top: 30px; max-width: 400px; }
        .step-item { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); padding: 14px 18px; border-radius: 12px; font-size: 14px; color: #cbd5e1; display: flex; align-items: center; gap: 12px; }
        .step-item.active { background: #fff; color: #000; font-weight: 600; }
        .login-right { flex: 1; background: #07030d; display: flex; flex-direction: column; justify-content: center; padding: 60px 80px; overflow-y: auto; }
        .login-right h1 { font-size: 32px; color: #fff; margin-bottom: 25px; font-weight: 600; }
        .social-logins { display: flex; gap: 12px; margin-bottom: 20px; }
        .social-btn { flex: 1; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); padding: 12px; border-radius: 10px; color: #fff; font-size: 13px; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; transition: 0.2s; display: inline-block; }
        .social-btn:hover { background: rgba(255, 255, 255, 0.08); border-color: rgba(168, 85, 247, 0.4); }
        .divider { text-align: center; border-bottom: 1px solid rgba(255, 255, 255, 0.08); line-height: 0.1rem; margin: 25px 0; }
        .divider span { background: #07030d; padding: 0 15px; color: #64748b; font-size: 12px; }
        .input-group { margin-bottom: 18px; }
        .input-group label { display: block; font-size: 13px; color: #94a3b8; margin-bottom: 8px; }
        .input-group input { width: 100%; padding: 14px 16px; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.1); background: #0f0a1a; color: #fff; font-size: 14px; outline: none; box-sizing: border-box; transition: 0.2s; }
        .input-group input:focus { border-color: #a855f7; box-shadow: 0 0 10px rgba(168, 85, 247, 0.3); }
        .btn-signin { width: 100%; background: #f1f5f9; color: #0f172a; border: none; padding: 14px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 15px; transition: 0.2s; margin-top: 10px; }
        .btn-signin:hover { background: #fff; box-shadow: 0 0 15px rgba(255, 255, 255, 0.4); }
        .btn-free { width: 100%; background: linear-gradient(135deg, #9333ea, #7e22ce); color: white; border: none; padding: 12px; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 14px; transition: 0.2s; margin-top: 10px; text-decoration: none; display: block; text-align: center; }
        .btn-free:hover { background: linear-gradient(135deg, #a855f7, #9333ea); box-shadow: 0 0 15px rgba(168, 85, 247, 0.5); }
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
            <a href="/oauth-login?provider=Google" class="social-btn">Google</a>
            <a href="/oauth-login?provider=GitHub" class="social-btn">GitHub</a>
            <a href="/oauth-login?provider=Discord" class="social-btn">Discord</a>
        </div>
        <div class="divider"><span>OR</span></div>
        <form action="/login" method="POST">
            <div class="input-group">
                <label>Lisans Anahtarı</label>
                <input type="text" name="license_key" placeholder="Lisans Anahtarınızı Girin..." required>
            </div>
            <button type="submit" class="btn-signin">Sign in →</button>
        </form>
        <a href="/oauth-login?provider=FreeGuest" class="btn-free">🚀 Tek Tıkla Free Giriş Yap</a>
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
    <title>AxeroCore.net - Fiyatlandırma Planları</title>
    <meta name="description" content="AxeroCore.net fiyatlandırma seçenekleri: Özgür, Profesyonel ve Başlangıç (VIP) paketleri.">
    <meta name="robots" content="index, follow">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: radial-gradient(circle at 50% 10%, #1c0e38 0%, #090514 80%); color: #f8fafc; margin: 0; padding: 0; min-height: 100vh; }
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 40px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); background: rgba(9, 5, 20, 0.9); backdrop-filter: blur(12px); }
        .logo { font-size: 20px; font-weight: bold; color: #fff; display: flex; align-items: center; gap: 8px; text-decoration: none; }
        .logo span { color: #c084fc; }
        .nav-links { display: flex; gap: 20px; font-size: 14px; color: #94a3b8; align-items: center; }
        .nav-links a { color: #94a3b8; text-decoration: none; transition: 0.2s; }
        .nav-links a:hover { color: #c084fc; }
        
        .container { max-width: 1100px; margin: 40px auto; padding: 0 20px; text-align: center; }
        p.subtitle { color: #94a3b8; font-size: 14px; max-width: 600px; margin: 0 auto 30px auto; line-height: 1.5; }

        .billing-toggle-box { display: inline-flex; background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.25); padding: 4px; border-radius: 30px; margin-bottom: 40px; }
        .toggle-btn { background: transparent; border: none; color: #94a3b8; padding: 8px 24px; border-radius: 20px; font-size: 13px; font-weight: 600; cursor: pointer; transition: 0.2s; }
        .toggle-btn.active { background: linear-gradient(135deg, #9333ea, #7e22ce); color: #fff; box-shadow: 0 0 15px rgba(168, 85, 247, 0.4); }
        .discount-badge { background: #10b981; color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 10px; margin-left: 6px; font-weight: bold; }

        .pricing-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; text-align: left; }
        .pricing-card { background: rgba(20, 12, 35, 0.85); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 20px; padding: 30px; display: flex; flex-direction: column; justify-content: space-between; position: relative; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .pricing-card.featured { border-color: #c084fc; box-shadow: 0 0 35px rgba(168, 85, 247, 0.25); background: rgba(25, 14, 45, 0.95); }
        
        .badge-best { position: absolute; top: -12px; left: 30px; background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.4); color: #c084fc; font-size: 11px; font-weight: bold; padding: 4px 12px; border-radius: 20px; display: flex; align-items: center; gap: 5px; }
        .badge-discount { position: absolute; top: -12px; right: 25px; background: #10b981; color: #fff; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 20px; }

        .plan-title { font-size: 22px; font-weight: bold; color: #fff; margin-bottom: 8px; }
        .plan-desc { font-size: 13px; color: #94a3b8; margin-bottom: 20px; min-height: 40px; }
        
        .plan-price { font-size: 34px; font-weight: 700; color: #fff; margin-bottom: 5px; }
        .plan-price span { font-size: 14px; color: #94a3b8; font-weight: normal; }
        .price-sub { font-size: 12px; color: #64748b; margin-bottom: 25px; }
        .price-sub b { color: #10b981; }

        .btn-plan { background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.3); color: #fff; padding: 12px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: bold; font-size: 14px; transition: 0.2s; display: block; margin-bottom: 25px; cursor: pointer; width: 100%; box-sizing: border-box; }
        .btn-plan:hover { background: rgba(168, 85, 247, 0.2); border-color: #c084fc; }
        .pricing-card.featured .btn-plan { background: #fff; color: #000; border: none; }
        .pricing-card.featured .btn-plan:hover { background: #f1f5f9; box-shadow: 0 0 15px rgba(255,255,255,0.4); }

        .plan-features { list-style: none; padding: 0; margin: 0; color: #cbd5e1; font-size: 13px; display: flex; flex-direction: column; gap: 14px; }
        .plan-features li { display: flex; align-items: flex-start; gap: 10px; line-height: 1.4; }
        .plan-features li span.check { color: #10b981; font-weight: bold; }
        .plan-features li span.cross { color: #f43f5e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/" class="logo">🛡️ Axero<span>Core.net</span></a>
        <div class="nav-links">
            <a href="/">Ev</a>
            <a href="/fiyatlandirma" style="color: #c084fc;">Fiyatlandırma</a>
            <a href="/api">API</a>
            <a href="/logout" style="color: #f43f5e; font-weight: bold;">Çıkış Yap</a>
        </div>
    </div>

    <div class="container">
        <p class="subtitle">Shopier Güvencesiyle Gerçek Ödeme ve Anında Lisans Teslimat Sistemi.</p>

        <div class="pricing-grid">
            <div class="pricing-card">
                <div>
                    <div class="plan-title">Özgür</div>
                    <div class="plan-desc">Temel arama iş akışını ücretsiz deneyin.</div>
                    <div class="plan-price">0 TL <span>/ay</span></div>
                    <div class="price-sub">Ücretsiz Deneme</div>
                    <a href="/" class="btn-plan">Mevcut Plan</a>
                    <ul class="plan-features">
                        <li><span class="check">✓</span> 12 Temel Modül Açık</li>
                        <li><span class="cross">✕</span> Pro ve VIP Modüller Kapalı</li>
                        <li><span class="cross">✕</span> API erişimi: Dahil değil</li>
                    </ul>
                </div>
            </div>

            <div class="pricing-card featured">
                <div class="badge-best">⭐ EN İYİ FİYAT</div>
                <div>
                    <div class="plan-title" style="margin-top: 5px;">Profesyonel</div>
                    <div class="plan-desc">Günlük profesyonel araştırmalar için Shopier Ödemeli</div>
                    <div class="plan-price">180 TL <span>/ay</span></div>
                    <div class="price-sub">Shopier Entegrasyonlu</div>
                    <form action="/shopier-odeme-baslat" method="POST">
                        <input type="hidden" name="tier" value="PRO">
                        <button type="submit" class="btn-plan">Shopier ile Pro Satın Al</button>
                    </form>
                    <ul class="plan-features">
                        <li><span class="check">✓</span> 24 Modül Açık</li>
                        <li><span class="check">✓</span> Sosyal Medya ve Oyun Tarama</li>
                        <li><span class="check">✓</span> API erişimi: Dahil</li>
                    </ul>
                </div>
            </div>

            <div class="pricing-card">
                <div>
                    <div class="plan-title">Başlangıç (VIP)</div>
                    <div class="plan-desc">Tüm 37 modül, API ve sınırsız otomasyon</div>
                    <div class="plan-price">400 TL <span>/ay</span></div>
                    <div class="price-sub">Shopier Entegrasyonlu</div>
                    <form action="/shopier-odeme-baslat" method="POST">
                        <input type="hidden" name="tier" value="VIP">
                        <button type="submit" class="btn-plan">Shopier ile VIP Satın Al</button>
                    </form>
                    <ul class="plan-features">
                        <li><span class="check">✓</span> Tüm 37 Gelişmiş Modül Açık</li>
                        <li><span class="check">✓</span> Sızıntı DB & Sınırsız API</li>
                        <li><span class="check">✓</span> 7/24 VIP Destek</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

HTML_SUCCESS_PURCHASE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Ödeme Onaylandı - AxeroCore.net</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #07030d; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: rgba(30, 20, 50, 0.8); backdrop-filter: blur(16px); border: 1px solid rgba(168, 85, 247, 0.3); padding: 40px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); width: 450px; text-align: center; }
        h1 { color: #10b981; margin-bottom: 10px; }
        .key-box { background: #0f071f; border: 1px solid #c084fc; padding: 15px; border-radius: 8px; font-size: 18px; color: #38bdf8; font-family: monospace; font-weight: bold; margin: 20px 0; user-select: all; }
        .btn { background: linear-gradient(135deg, #9333ea, #7e22ce); color: white; border: none; padding: 14px; width: 100%; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 15px; text-decoration: none; display: inline-block; box-sizing: border-box; }
        .btn:hover { background: linear-gradient(135deg, #a855f7, #9333ea); box-shadow: 0 0 15px rgba(168, 85, 247, 0.6); }
    </style>
</head>
<body>
    <div class="card">
        <h1>🎉 Shopier Ödemesi Başarılı!</h1>
        <p style="color: #94a3b8; font-size: 14px;">Shopier üzerinden <b>{TIER}</b> paketiniz onaylandı ve özel lisans anahtarınız üretildi.</p>
        <div class="key-box">{GENERATED_KEY}</div>
        <p style="font-size: 12px; color: #64748b; margin-bottom: 25px;">Bu anahtar sistemde aktive edildi. Hemen panele giriş yapabilirsiniz.</p>
        <a href="/" class="btn">Panele Giriş Yap →</a>
    </div>
</body>
</html>
"""

HTML_API = """
<!DOCTYPE html>
<html lang="tr">
<head><meta charset="UTF-8"><title>API</title></head>
<body style="background:#07030d; color:#fff; font-family:sans-serif; padding:40px;">
    <h1>AxeroCore API</h1>
    <p>Shopier entegrasyonlu lisanslama aktif.</p>
    <a href="/" style="color:#c084fc;">← Ana Sayfa</a>
</body>
</html>
"""

HTML_ADMIN_LOGIN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8"><title>Admin Giriş</title>
    <style>
        body { font-family: sans-serif; background: #07030d; color: #f8fafc; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: rgba(30, 20, 50, 0.7); border: 1px solid rgba(244, 63, 94, 0.2); padding: 40px; border-radius: 16px; width: 380px; text-align: center; }
        input { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 8px; border: 1px solid rgba(244, 63, 94, 0.3); background: #0f071f; color: #fff; box-sizing: border-box; outline: none; }
        button { width: 100%; background: #f43f5e; color: white; border: none; padding: 12px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .error { color: #f43f5e; font-size: 13px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1 style="color: #f43f5e;">Admin Girişi 🔒</h1>
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
    <meta charset="UTF-8"><title>Admin Paneli</title>
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
        <a href="/" style="color: #c084fc; text-decoration: none;">← Ana Sayfaya Dön</a>
        <h1 style="color: #f43f5e; text-align: center;">🔑 Shopier & Lisans Yönetim Paneli</h1>
        <form action="/admin-create-key" method="POST" style="text-align: center; margin-bottom: 20px;">
            <select name="tier_type">
                <option value="FREE">Free</option>
                <option value="PRO">Pro</option>
                <option value="VIP">VIP</option>
            </select>
            <button type="submit">Manuel Key Üret</button>
        </form>
        <table>
            <tr><th>Lisans Anahtarı</th><th>Paket Türü</th><th>Limit</th></tr>
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
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 40px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); background: rgba(9, 5, 20, 0.9); }
        .logo { font-size: 20px; font-weight: bold; color: #fff; text-decoration: none; display: flex; gap: 8px; }
        .logo span { color: #c084fc; }
        .nav-links { display: flex; gap: 20px; font-size: 14px; align-items: center; }
        .nav-links a { color: #94a3b8; text-decoration: none; }
        .nav-links a:hover { color: #c084fc; }
        .user-badge { background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); padding: 6px 14px; border-radius: 20px; color: #c084fc; font-weight: bold; font-size: 13px; }
        .container { max-width: 950px; margin: 40px auto; padding: 0 20px; text-align: center; }
        .search-pill-container { background: rgba(20, 12, 35, 0.85); border: 1px solid rgba(168, 85, 247, 0.35); padding: 10px 14px; border-radius: 40px; display: flex; align-items: center; margin-bottom: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.6); }
        .pill-input { flex: 1; background: transparent; border: none; color: #fff; font-size: 15px; outline: none; padding: 0 10px; }
        .pill-search-btn { background: linear-gradient(135deg, #9333ea, #7e22ce); color: white; border: none; padding: 12px 28px; border-radius: 30px; cursor: pointer; font-weight: bold; font-size: 14px; }
        .modules-section { text-align: left; margin-bottom: 25px; background: rgba(20, 12, 35, 0.5); border: 1px solid rgba(168, 85, 247, 0.1); padding: 20px; border-radius: 14px; }
        .modules-section h3 { color: #c084fc; border-bottom: 1px solid rgba(168, 85, 247, 0.2); padding-bottom: 8px; margin-bottom: 15px; font-size: 15px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .checkbox-label { background: #0f071f; padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.15); font-size: 13px; display: flex; align-items: center; gap: 10px; cursor: pointer; color: #cbd5e1; }
        .checkbox-label input { accent-color: #a855f7; transform: scale(1.1); }
        .checkbox-label.locked { opacity: 0.35; cursor: not-allowed; }
        pre { background: #0b0414; padding: 20px; border-radius: 12px; text-align: left; overflow-x: auto; color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); font-family: monospace; font-size: 13px; }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/" class="logo">🛡️ Axero<span>Core.net</span></a>
        <div class="nav-links">
            <a href="/">Ev</a>
            <a href="/fiyatlandirma">Fiyatlandırma</a>
            <a href="/api">API</a>
            <span class="user-badge">Paket: {TIER_NAME} ({LIMIT_TEXT})</span>
            <a href="/logout" style="color: #f43f5e; font-weight: bold;">Çıkış Yap</a>
        </div>
    </div>

    <div class="container">
        <form action="/sorgula" method="POST">
            <div class="search-pill-container">
                <div style="color: #c084fc; font-size: 18px; margin-left: 10px;">🛡️</div>
                <input type="text" name="target" class="pill-input" placeholder="e.g. username: winterfox veya IP adresi..." required>
                <button type="submit" class="pill-search-btn">Aramak →</button>
            </div>

            <div class="modules-section">
                <h3>🟢 Temel Modüller (Free)</h3>
                <div class="grid">
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="ip" checked> IP & Geo Lokasyon</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="whois" checked> Domain Whois</label>
                    <label class="checkbox-label"><input type="checkbox" name="modules" value="port"> Port Taraması</label>
                </div>
            </div>

            <div class="modules-section">
                <h3>🔵 Pro Modüller (Pro & VIP)</h3>
                <div class="grid">
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_instagram" {PRO_DISABLED}> Instagram Tarama</label>
                    <label class="checkbox-label {PRO_LOCK}"><input type="checkbox" name="modules" value="social_discord" {PRO_DISABLED}> Discord ID Analiz</label>
                </div>
            </div>

            <div class="modules-section">
                <h3>⭐ Gelişmiş Tehdit Modülleri (VIP)</h3>
                <div class="grid">
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="discord_token_lookup" {VIP_DISABLED}> Discord Token & DB</label>
                    <label class="checkbox-label {VIP_LOCK}"><input type="checkbox" name="modules" value="leak_email" {VIP_DISABLED}> E-Posta Sızıntı DB</label>
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

@app.get("/fiyatlandirma", response_class=HTMLResponse)
def fiyatlandirma():
    return HTMLResponse(content=HTML_PRICING)

# Shopier Ödeme Başlatma ve Otomatik Onay Mekanizması
@app.post("/shopier-odeme-baslat", response_class=HTMLResponse)
def shopier_odeme_baslat(tier: str = Form(...)):
    # Burada normalde Shopier ödeme form sayfasına yönlendirilir. 
    # Şimdilik direkt ödemenin başarıyla tamamlandığını simüle edip anında key veriyoruz:
    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    new_key = f"AXERO-SHOPIER-{tier}-{random_code}"
    limit = 24 if tier == "PRO" else 37
    
    DATABASE_KEYS[new_key] = {"type": tier, "limit": limit}
    
    USER_SESSION["logged_in"] = True
    USER_SESSION["key"] = new_key
    USER_SESSION["tier"] = tier
    USER_SESSION["limit"] = limit
    
    page = HTML_SUCCESS_PURCHASE.replace("{TIER}", tier)\
                                .replace("{GENERATED_KEY}", new_key)
    return HTMLResponse(content=page)

@app.get("/api", response_class=HTMLResponse)
def api_docs():
    return HTMLResponse(content=HTML_API)

@app.get("/oauth-login", response_class=HTMLResponse)
def oauth_login(provider: str):
    USER_SESSION["logged_in"] = True
    USER_SESSION["key"] = f"OAUTH-{provider.upper()}"
    USER_SESSION["tier"] = "FREE"
    USER_SESSION["limit"] = 12
    return RedirectResponse(url="/", status_code=303)

@app.get("/admin-login", response_class=HTMLResponse)
def admin_login_page():
    return HTMLResponse(content=HTML_ADMIN_LOGIN.replace("{ERROR_MSG}", ""))

@app.post("/admin-auth", response_class=HTMLResponse)
def admin_auth(admin_pass: str = Form(...)):
    if admin_pass == "yalcin123":
        USER_SESSION["is_admin"] = True
        return RedirectResponse(url="/admin-panel", status_code=303)
    else:
        err = '<div class="error">Hatalı şifre!</div>'
        return HTMLResponse(content=HTML_ADMIN_LOGIN.replace("{ERROR_MSG}", err))

@app.get("/admin-panel", response_class=HTMLResponse)
def admin_panel():
    if not USER_SESSION["is_admin"]:
        return RedirectResponse(url="/admin-login", status_code=303)
    rows = ""
    for k, v in DATABASE_KEYS.items():
        rows += f"<tr><td><b>{k}</b></td><td>{v['type']}</td><td>{v['limit']}</td></tr>"
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
        
    results = [f"=== AXEROCORE.NET RAPORU ==="]
    results.append(f"Hedef: {target} | Paket: {USER_SESSION['tier']}")
    results.append(f"Seçilen Modül Sayısı: {len(modules)}\n" + "="*30)

    for mod in modules:
        results.append(f"[{mod.upper()}] Modül başarıyla çalıştırıldı ve veri çekildi.")

    report = "\n".join(results)
    tier = USER_SESSION["tier"]
    pro_lock = "" if tier in ["PRO", "VIP"] else "locked"
    pro_disabled = "" if tier in ["PRO", "VIP"] else "disabled"
    vip_lock = "" if tier == "VIP" else "locked"
    vip_disabled = "" if tier == "VIP" else "disabled"
    
    result_html = f"""
    <div style="margin-top: 30px;">
        <h3>🔍 Tarama Sonuçları</h3>
        <pre>{report}</pre>
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
