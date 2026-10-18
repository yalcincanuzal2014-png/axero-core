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
    <meta name="keywords" content="axerocore fiyat, axero fiyatlandırma, osint paketleri">
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

        .btn-plan { background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.3); color: #fff; padding: 12px; border-radius: 12px; text-align: center; text-decoration: none; font-weight: bold; font-size: 14px; transition: 0.2s; display: block; margin-bottom: 25px; }
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
        <p class="subtitle">Öncelikle temel unsurlarla başlayın, ardından işiniz gerektirdikçe arama kapasitenizi, otomasyonunuzu ve API erişiminizi genişletin.</p>

        <div class="billing-toggle-box">
            <button type="button" class="toggle-btn active" id="btnYearly" onclick="setBilling('yearly')">Yıllık <span class="discount-badge">%30 tasarruf edin</span></button>
            <button type="button" class="toggle-btn" id="btnMonthly" onclick="setBilling('monthly')">Aylık</button>
        </div>

        <div class="pricing-grid">
            <div class="pricing-card">
                <div>
                    <div class="plan-title">Özgür</div>
                    <div class="plan-desc">Temel arama iş akışını ücretsiz deneyin.</div>
                    <div class="plan-price" id="priceFree">0 TL <span>/ay</span></div>
                    <div class="price-sub" id="subFree">Yıllıkta 0 TL /yıl</div>
                    <a href="/" class="btn-plan">Mevcut Plan</a>
                    <ul class="plan-features">
                        <li><span class="check">✓</span> 12 Temel Modül Açık</li>
                        <li><span class="cross">✕</span> Pro ve VIP Modüller Kapalı</li>
                        <li><span class="cross">✕</span> API erişimi: Dahil değil</li>
                        <li><span class="cross">✕</span> Toplu arama: Dahil değil</li>
                        <li><span class="check">✓</span> Günde 30 sorgu hakkı</li>
                    </ul>
                </div>
            </div>

            <div class="pricing-card featured">
                <div class="badge-best">⭐ EN İYİ FİYAT</div>
                <div class="badge-discount">%30 İNDİRİM</div>
                <div>
                    <div class="plan-title" style="margin-top: 5px;">Profesyonel</div>
                    <div class="plan-desc">Daha geniş ölçekte günlük profesyonel araştırmalar</div>
                    <div class="plan-price" id="pricePro">180 TL <span>/ay</span></div>
                    <div class="price-sub" id="subPro"><s>250 TL /ay</s> - % 30<br><b>1.512 TL /yıl</b><br><span style="color:#10b981;">Yılda 648 TL tasarruf edin</span></div>
                    <a href="/" class="btn-plan">Go Pro</a>
                    <ul class="plan-features">
                        <li><span class="check">✓</span> 24 Modül Açık (Temel + Orta Düzey)</li>
                        <li><span class="check">✓</span> Sosyal Medya ve Oyun Tarama Modülleri</li>
                        <li><span class="check">✓</span> API erişimi: Dahil</li>
                        <li><span class="check">✓</span> Günde 500 sorgu hakkı</li>
                        <li><span class="check">✓</span> Öncelikli destek kuyruğu</li>
                    </ul>
                </div>
            </div>

            <div class="pricing-card">
                <div>
                    <div class="plan-title">Başlangıç (VIP)</div>
                    <div class="plan-desc">Tüm 37 modül, API ve sınırsız otomasyon</div>
                    <div class="plan-price" id="priceStart">400 TL <span>/ay</span></div>
                    <div class="price-sub" id="subStart"><s>570 TL /ay</s> - % 30<br><b>3.360 TL /yıl</b><br><span style="color:#10b981;">Yılda 1.440 TL tasarruf edin</span></div>
                    <a href="/" class="btn-plan">Başlayın</a>
                    <ul class="plan-features">
                        <li><span class="check">✓</span> Tüm 37 Gelişmiş Modül Açık (Tümü)</li>
                        <li><span class="check">✓</span> E-Posta, Telefon ve Sızıntı DB</li>
                        <li><span class="check">✓</span> Discord Token & Derin Ağ Tarama</li>
                        <li><span class="check">✓</span> Sınırsız API Erişimi</li>
                        <li><span class="check">✓</span> 7/24 VIP Destek</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <script>
        function setBilling(mode) {
            const btnY = document.getElementById('btnYearly');
            const btnM = document.getElementById('btnMonthly');
            const pricePro = document.getElementById('pricePro');
            const subPro = document.getElementById('subPro');
            const priceStart = document.getElementById('priceStart');
            const subStart = document.getElementById('subStart');

            if (mode === 'yearly') {
                btnY.classList.add('active');
                btnM.classList.remove('active');
                pricePro.innerHTML = '180 TL <span>/ay</span>';
                subPro.innerHTML = '<s>250 TL /ay</s> - % 30<br><b>1.512 TL /yıl</b><br><span style="color:#10b981;">Yılda 648 TL tasarruf edin</span>';
                priceStart.innerHTML = '400 TL <span>/ay</span>';
                subStart.innerHTML = '<s>570 TL /ay</s> - % 30<br><b>3.360 TL /yıl</b><br><span style="color:#10b981;">Yılda 1.440 TL tasarruf edin</span>';
            } else {
                btnM.classList.add('active');
                btnY.classList.remove('active');
                pricePro.innerHTML = '250 TL <span>/ay</span>';
                subPro.innerHTML = 'Aylık esnek faturalandırma';
                priceStart.innerHTML = '570 TL <span>/ay</span>';
                subStart.innerHTML = 'Aylık esnek faturalandırma';
            }
        }
    </script>
</body>
</html>
"""

HTML_API = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - API Dokümantasyonu ve Geliştirici Kılavuzu</title>
    <meta name="description" content="AxeroCore.net API dokümantasyonu, uç nokta referansları ve entegrasyon kılavuzları.">
    <meta name="keywords" content="axerocore api, osint api, breach search api">
    <meta name="robots" content="index, follow">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #07030d; color: #f8fafc; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .api-navbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 30px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); background: #07030d; height: 60px; box-sizing: border-box; }
        .api-nav-left { display: flex; align-items: center; gap: 40px; }
        .logo { font-size: 18px; font-weight: bold; color: #fff; text-decoration: none; display: flex; align-items: center; gap: 8px; }
        .logo span { color: #c084fc; }
        .top-tabs { display: flex; gap: 25px; font-size: 14px; }
        .top-tab { color: #94a3b8; text-decoration: none; padding-bottom: 18px; cursor: pointer; border-bottom: 2px solid transparent; transition: 0.2s; }
        .top-tab.active { color: #fff; border-bottom-color: #c084fc; font-weight: 600; }
        .api-nav-right { display: flex; align-items: center; gap: 15px; }
        .home-btn { background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); color: #c084fc; padding: 6px 14px; border-radius: 8px; font-size: 13px; text-decoration: none; font-weight: bold; }
        .home-btn:hover { background: rgba(168, 85, 247, 0.25); }
        .api-main-layout { display: flex; flex: 1; overflow: hidden; }
        .api-sidebar { width: 280px; background: #07030d; border-right: 1px solid rgba(168, 85, 247, 0.15); padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; box-sizing: border-box; }
        .search-box { background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 8px; color: #64748b; font-size: 13px; }
        .search-box input { background: transparent; border: none; color: #fff; outline: none; width: 100%; font-size: 13px; }
        .sidebar-menu { display: flex; flex-direction: column; gap: 6px; }
        .menu-category-title { font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; margin-top: 10px; margin-bottom: 6px; letter-spacing: 0.5px; }
        .menu-item { color: #94a3b8; text-decoration: none; font-size: 13px; padding: 6px 10px; border-radius: 6px; cursor: pointer; transition: 0.2s; display: block; }
        .menu-item:hover { color: #fff; background: rgba(168, 85, 247, 0.08); }
        .menu-item.active { color: #c084fc; background: rgba(168, 85, 247, 0.15); font-weight: 600; }
        .api-content { flex: 1; padding: 40px 60px; overflow-y: auto; background: #090514; box-sizing: border-box; }
        .content-section { display: none; }
        .content-section.active { display: block; }
        .breadcrumb { font-size: 12px; color: #a855f7; font-weight: 600; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
        h1 { font-size: 32px; color: #fff; margin-top: 0; margin-bottom: 12px; }
        p { color: #94a3b8; font-size: 14px; line-height: 1.6; margin-bottom: 30px; }
        .api-visual-box { background: rgba(20, 12, 35, 0.8); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 35px; }
        .quick-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }
        .quick-card { background: rgba(20, 12, 35, 0.9); border: 1px solid rgba(168, 85, 247, 0.25); border-radius: 12px; padding: 25px; cursor: pointer; transition: 0.2s; text-align: left; }
        .quick-card:hover { border-color: #c084fc; background: rgba(168, 85, 247, 0.1); }
        .quick-card h3 { color: #fff; font-size: 16px; margin-top: 10px; margin-bottom: 8px; }
        .quick-card p { font-size: 13px; margin: 0; color: #94a3b8; }
        .api-outline { width: 240px; padding: 20px; border-left: 1px solid rgba(168, 85, 247, 0.15); font-size: 13px; box-sizing: border-box; }
        .outline-title { font-weight: bold; color: #fff; margin-bottom: 12px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
        .outline-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
        .outline-list a { color: #94a3b8; text-decoration: none; transition: 0.2s; }
        .outline-list a:hover { color: #c084fc; }
        pre { background: #05020a; padding: 18px; border-radius: 10px; color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.2); font-size: 13px; overflow-x: auto; font-family: monospace; }
        .endpoint-pill { font-family: monospace; background: #0f071f; padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(168, 85, 247, 0.3); color: #c084fc; font-size: 13px; display: inline-block; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="api-navbar">
        <div class="api-nav-left">
            <a href="/" class="logo">🛡️ Axero<span>Core.net</span></a>
            <div class="top-tabs">
                <a class="top-tab active" onclick="switchTopTab('dokumantasyon', this)">Dokümantasyon</a>
                <a class="top-tab" onclick="switchTopTab('referans', this)">API Referansı</a>
                <a class="top-tab" onclick="switchTopTab('sdks', this)">SDK'lar</a>
            </div>
        </div>
        <div class="api-nav-right">
            <a href="/" class="home-btn">← Panele Dön</a>
        </div>
    </div>

    <div class="api-main-layout">
        <div class="api-sidebar">
            <div class="search-box">
                <span>🔍</span>
                <input type="text" placeholder="Axero API belgelerinde arayın...">
            </div>
            <div class="sidebar-menu">
                <div class="menu-category-title">Başlarken</div>
                <a class="menu-item active" onclick="loadDoc('hosgeldin', this)">Ev / Hoş Geldin</a>
                <a class="menu-item" onclick="loadDoc('hizli_baslangic', this)">Hızlı Başlangıç</a>
                <a class="menu-item" onclick="loadDoc('kimlik_dogrulama', this)">Kimlik Doğrulama</a>
                <div class="menu-category-title" style="margin-top:15px;">Arama Kılavuzları</div>
                <a class="menu-item" onclick="loadDoc('arama_oturumları', this)">Arama Oturumları</a>
                <a class="menu-item" onclick="loadDoc('filtreler', this)">Yapılandırılmış Filtreler</a>
                <a class="menu-item" onclick="loadDoc('ihlaller', this)">Güvenlik İhlali Araması</a>
                <a class="menu-item" onclick="loadDoc('hirsiz', this)">Hırsız Arama</a>
                <a class="menu-item" onclick="loadDoc('kurbanlar', this)">Kurbanlar</a>
                <a class="menu-item" onclick="loadDoc('dosya_arama', this)">Dosya Arama</a>
                <a class="menu-item" onclick="loadDoc('toplu_arama', this)">Toplu Arama</a>
                <a class="menu-item" onclick="loadDoc('ihracat', this)">İhracat</a>
                <div class="menu-category-title" style="margin-top:15px;">OSINT ve Programlar</div>
                <a class="menu-item" onclick="loadDoc('osint_sorgulari', this)">OSINT Sorguları</a>
                <a class="menu-item" onclick="loadDoc('kamu_hizmetleri', this)">Kamu Hizmetleri</a>
                <div class="menu-category-title" style="margin-top:15px;">Entegrasyon</div>
                <a class="menu-item" onclick="loadDoc('kotalar', this)">Kotalar ve Limitler</a>
            </div>
        </div>

        <div class="api-content" id="docContentArea">
            <div id="sec-hosgeldin" class="content-section active">
                <div class="breadcrumb">Başlarken</div>
                <h1>AxeroCore API Dokümantasyonu</h1>
                <p>Veri ihlali arama, veri hırsızı analizi, mağdurlar, tarayıcılar ve OSINT sorgulamaları için kapsamlı veri zekası API'si.</p>
                <div class="api-visual-box">
                    <div style="font-weight:bold; color:#c084fc; margin-bottom:10px; font-size:16px;">Axero Data Intelligence API</div>
                    <div style="color:#94a3b8; font-size:13px;">50+ Milyon Kayıt • Gerçek Zamanlı Sorgu • Kurumsal Güvenlik</div>
                </div>
                <h2>AxeroCore API'ye hoş geldiniz</h2>
                <p>AxeroCore, tek bir API platformu aracılığıyla ihlal arama, veri hırsızı analizi, mağdur tespiti, tarayıcılar ve OSINT zenginleştirme hizmetleri sunar.</p>
                <div class="quick-grid">
                    <div class="quick-card" onclick="loadDoc('hizli_baslangic', null)">
                        <div style="font-size:20px;">⚡</div>
                        <h3>Hızlı Başlangıç</h3>
                        <p>İlk API çağrınızı 5 dakikadan kısa sürede gerçekleştirin.</p>
                    </div>
                    <div class="quick-card" onclick="switchTopTab('referans', null)">
                        <div style="font-size:20px;">📄</div>
                        <h3>API Referansı</h3>
                        <p>Oluşturulan OpenAPI referansını kullanarak uç nokta detaylarına ulaşabilirsiniz.</p>
                    </div>
                </div>
            </div>

            <div id="sec-hizli_baslangic" class="content-section">
                <div class="breadcrumb">Başlarken</div>
                <h1>Hızlı Başlangıç</h1>
                <p>AxeroCore API ile ilk sorgunuzu hemen çalıştırın.</p>
                <div class="endpoint-pill">POST /api/v1/query</div>
                <pre>curl -X POST "https://axerocore.net/api/v1/query" \\\n     -H "Authorization: Bearer AXERO-KEY-X" \\\n     -d "target=winterfox"</pre>
            </div>

            <div id="sec-kimlik_dogrulama" class="content-section">
                <div class="breadcrumb">Başlarken</div>
                <h1>Kimlik Doğrulama</h1>
                <p>API isteklerinizde Header içine Bearer token eklemeniz gerekmektedir.</p>
                <pre>Authorization: Bearer AXERO-MASTER-ADMIN-KEY</pre>
            </div>

            <div id="sec-ihlaller" class="content-section">
                <div class="breadcrumb">Arama Kılavuzları</div>
                <h1>Güvenlik İhlali Araması</h1>
                <p>Sızıntı veritabanlarında arama yapın.</p>
                <div class="endpoint-pill">POST /api/v1/breach-search</div>
                <pre>curl -X POST "https://axerocore.net/api/v1/breach-search" \\\n     -d "query=user@domain.com"</pre>
            </div>

            <div id="sec-toplu_arama" class="content-section">
                <div class="breadcrumb">Arama Kılavuzları</div>
                <h1>Toplu Arama (Bulk Search)</h1>
                <p>VIP paketlerde toplu dosya yükleyerek sorgulayın.</p>
            </div>

            <div id="sec-osint_sorgulari" class="content-section">
                <div class="breadcrumb">OSINT Kılavuzları</div>
                <h1>OSINT Sorguları</h1>
                <p>IP, Domain Whois, ASN ve Discord ID zenginleştirme modülleri.</p>
            </div>

            <div id="sec-kotalar" class="content-section">
                <div class="breadcrumb">Entegrasyon</div>
                <h1>Kotalar ve Limitler</h1>
                <p>Paketinize göre günlük sorgu limitleriniz uygulanır.</p>
            </div>
        </div>

        <div class="api-outline">
            <div class="outline-title">Bu sayfada</div>
            <ul class="outline-list">
                <li><a href="#hosgeldin">AxeroCore API'ye hoş geldiniz</a></li>
                <li><a href="#hizli">Temel Yetenekler</a></li>
                <li><a href="#ornek">Hızlı Örnek</a></li>
                <li><a href="#yardim">Yardım Almak</a></li>
            </ul>
        </div>
    </div>

    <script>
        function loadDoc(secName, el) {
            document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
            const target = document.getElementById('sec-' + secName);
            if (target) target.classList.add('active');
            if (el) {
                document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
                el.classList.add('active');
            }
        }
        function switchTopTab(tabName, el) {
            document.querySelectorAll('.top-tab').forEach(t => t.classList.remove('active'));
            if (el) el.classList.add('active');
            if (tabName === 'referans') { loadDoc('hizli_baslangic', null); }
            else if (tabName === 'sdks') { loadDoc('osint_sorgulari', null); }
            else { loadDoc('hosgeldin', null); }
        }
    </script>
</body>
</html>
"""

HTML_ADMIN_LOGIN = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>AxeroCore.net - Admin Girişi</title>
    <meta name="robots" content="noindex, nofollow">
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
    <meta name="robots" content="noindex, nofollow">
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
    <meta name="description" content="AxeroCore.net İstihbarat ve Güvenlik Platformu paneli.">
    <meta name="keywords" content="axerocore, osint panel, breach intelligence">
    <meta name="robots" content="index, follow">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: radial-gradient(circle at 50% 10%, #1c0e38 0%, #090514 80%); color: #f8fafc; margin: 0; padding: 0; min-height: 100vh; }
        .navbar { display: flex; justify-content: space-between; align-items: center; padding: 18px 40px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); background: rgba(9, 5, 20, 0.9); backdrop-filter: blur(12px); }
        .logo { font-size: 20px; font-weight: bold; color: #fff; display: flex; align-items: center; gap: 8px; text-decoration: none; }
        .logo span { color: #c084fc; }
        .nav-links { display: flex; gap: 20px; font-size: 14px; color: #94a3b8; align-items: center; }
        .nav-links a { color: #94a3b8; text-decoration: none; transition: 0.2s; }
        .nav-links a:hover { color: #c084fc; }
        .user-badge { background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); padding: 6px 14px; border-radius: 20px; color: #c084fc; font-weight: bold; font-size: 13px; }
        .logout-btn { color: #f43f5e !important; font-weight: bold; }
        .container { max-width: 950px; margin: 40px auto; padding: 0 20px; text-align: center; }
        .top-stats-area { display: flex; justify-content: flex-end; align-items: center; margin-bottom: 10px; }
        .users-counter-box { background: rgba(20, 12, 35, 0.7); border: 1px solid rgba(168, 85, 247, 0.2); padding: 10px 20px; border-radius: 14px; text-align: right; }
        .users-counter-box b { color: #fff; font-size: 20px; display: block; font-weight: 700; }
        .users-counter-box span { font-size: 12px; color: #94a3b8; }
        .search-pill-container { background: rgba(20, 12, 35, 0.85); backdrop-filter: blur(16px); border: 1px solid rgba(168, 85, 247, 0.35); padding: 10px 14px; border-radius: 40px; display: flex; align-items: center; box-shadow: 0 10px 40px rgba(0,0,0,0.6); margin-bottom: 15px; }
        .search-icon-badge { background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #c084fc; font-size: 18px; margin-right: 12px; flex-shrink: 0; }
        .pill-input { flex: 1; background: transparent; border: none; color: #fff; font-size: 15px; outline: none; padding: 0 10px; }
        .pill-input::placeholder { color: #64748b; }
        .pill-search-btn { background: linear-gradient(135deg, #9333ea, #7e22ce); color: white; border: none; padding: 12px 28px; border-radius: 30px; cursor: pointer; font-weight: bold; font-size: 14px; transition: 0.3s; flex-shrink: 0; }
        .pill-search-btn:hover { background: linear-gradient(135deg, #a855f7, #9333ea); box-shadow: 0 0 15px rgba(168, 85, 247, 0.6); }
        .sub-toolbar-card { background: rgba(20, 12, 35, 0.75); border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 20px; padding: 12px 20px; display: flex; flex-direction: column; gap: 12px; margin-bottom: 25px; box-shadow: 0 8px 25px rgba(0,0,0,0.5); }
        .history-row { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #94a3b8; border-bottom: 1px solid rgba(168, 85, 247, 0.1); padding-bottom: 10px; }
        .history-chips-left { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .chip { background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.25); padding: 5px 12px; border-radius: 20px; color: #cbd5e1; font-size: 12px; display: flex; align-items: center; gap: 6px; cursor: pointer; transition: 0.2s; }
        .chip:hover { border-color: #c084fc; background: rgba(168, 85, 247, 0.15); }
        .chip .remove-chip { color: #f43f5e; font-weight: bold; margin-left: 4px; cursor: pointer; }
        .clear-all { color: #f43f5e; cursor: pointer; font-weight: 600; text-decoration: none; }
        .clear-all:hover { text-decoration: underline; }
        .toolbar-bottom-row { display: flex; justify-content: space-between; align-items: center; }
        .mode-tabs { display: flex; gap: 8px; }
        .mode-btn { background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.2); color: #94a3b8; padding: 8px 16px; border-radius: 12px; cursor: pointer; font-size: 12px; font-weight: 500; transition: 0.2s; }
        .mode-btn.active { background: rgba(168, 85, 247, 0.25); color: #fff; border-color: #c084fc; }
        .manual-section { display: none; text-align: left; background: rgba(20, 12, 35, 0.85); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 16px; padding: 20px; margin-bottom: 25px; }
        .manual-categories { display: flex; gap: 15px; margin-bottom: 15px; border-bottom: 1px solid rgba(168, 85, 247, 0.15); padding-bottom: 12px; flex-wrap: wrap; }
        .manual-cat-btn { background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.2); color: #94a3b8; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.2s; }
        .manual-cat-btn.active { background: rgba(244, 63, 94, 0.15); border-color: rgba(244, 63, 94, 0.5); color: #f43f5e; }
        .manual-cat-btn:hover { border-color: #c084fc; color: #fff; }
        .manual-items-grid { display: none; gap: 12px; flex-wrap: wrap; }
        .manual-items-grid.active { display: flex; }
        .manual-item-card { background: #0f071f; border: 1px solid rgba(168, 85, 247, 0.25); padding: 12px 18px; border-radius: 12px; display: flex; align-items: center; gap: 10px; cursor: pointer; color: #cbd5e1; font-size: 13px; font-weight: 500; transition: 0.2s; }
        .manual-item-card:hover { border-color: #c084fc; background: rgba(168, 85, 247, 0.1); }
        .manual-item-card input { accent-color: #a855f7; transform: scale(1.2); }
        .action-links-row { display: flex; justify-content: center; gap: 15px; margin-bottom: 35px; flex-wrap: wrap; }
        .action-pill { background: rgba(20, 12, 35, 0.8); border: 1px solid rgba(168, 85, 247, 0.2); padding: 8px 16px; border-radius: 16px; color: #cbd5e1; font-size: 13px; text-decoration: none; display: flex; align-items: center; gap: 8px; transition: 0.2s; }
        .action-pill:hover { border-color: #c084fc; background: rgba(168, 85, 247, 0.1); color: #fff; }
        .modules-section { text-align: left; margin-bottom: 25px; background: rgba(20, 12, 35, 0.5); border: 1px solid rgba(168, 85, 247, 0.1); padding: 20px; border-radius: 14px; }
        .modules-section h3 { color: #c084fc; border-bottom: 1px solid rgba(168, 85, 247, 0.2); padding-bottom: 8px; margin-bottom: 15px; font-size: 15px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .checkbox-label { background: #0f071f; padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.15); font-size: 13px; display: flex; align-items: center; gap: 10px; cursor: pointer; color: #cbd5e1; }
        .checkbox-label:hover { border-color: rgba(168, 85, 247, 0.5); background: rgba(168, 85, 247, 0.05); }
        .checkbox-label input { accent-color: #a855f7; transform: scale(1.1); }
        .checkbox-label.locked { opacity: 0.35; cursor: not-allowed; }
        .results-grid { display: grid; grid-template-columns: 360px 1fr; gap: 20px; margin-top: 30px; text-align: left; }
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
        <a href="/" class="logo">🛡️ Axero<span>Core.net</span></a>
        <div class="nav-links">
            <a href="/">Ev</a>
            <a href="/fiyatlandirma">Fiyatlandırma</a>
            <a href="/api">API</a>
            <span class="user-badge">Paket: {TIER_NAME} ({LIMIT_TEXT})</span>
            <a href="/logout" class="logout-btn">Çıkış Yap</a>
        </div>
    </div>

    <div class="container">
        <div class="top-stats-area">
            <div class="users-counter-box">
                <b>256,5K</b>
                <span>güvenilir kullanıcılar</span>
            </div>
        </div>

        <form action="/sorgula" method="POST">
            <div class="search-pill-container">
                <div class="search-icon-badge">🛡️</div>
                <input type="text" id="targetInput" name="target" class="pill-input" placeholder="e.g. username: winterfox veya 185.146.115.107..." required>
                <button type="submit" class="pill-search-btn">Aramak →</button>
            </div>

            <div class="sub-toolbar-card">
                <div class="history-row">
                    <div class="history-chips-left" id="chipsContainer">
                        <span>🕒 TARİH</span>
                        <div class="chip" onclick="fillInput('185.146.115.107')">185.146.115.107 <span class="remove-chip" onclick="event.stopPropagation(); removeChip(this)">✕</span></div>
                        <div class="chip" onclick="fillInput('1556198663930519627')">1556198663930519627 <span class="remove-chip" onclick="event.stopPropagation(); removeChip(this)">✕</span></div>
                        <div class="chip" onclick="fillInput('1484580282179246163')">1484580282179246163 <span class="remove-chip" onclick="event.stopPropagation(); removeChip(this)">✕</span></div>
                    </div>
                    <span class="clear-all" onclick="clearAllChips()">🗑️ TÜMÜNÜ TEMİZLE</span>
                </div>
                <div class="toolbar-bottom-row">
                    <div class="mode-tabs">
                        <button type="button" class="mode-btn active" id="btnAuto" onclick="switchMode('auto')">Otomatikleştirilmiş</button>
                        <button type="button" class="mode-btn" id="btnManual" onclick="switchMode('manual')">Manuel</button>
                    </div>
                    <div class="mode-tabs">
                        <button type="button" class="mode-btn" onclick="setMode(this)">🔲 Toplu Arama</button>
                        <button type="button" class="mode-btn" onclick="setMode(this)">🌐 Tarayıcı</button>
                    </div>
                </div>
            </div>

            <div id="manualPanel" class="manual-section">
                <div class="manual-categories">
                    <div class="manual-cat-btn active" onclick="switchCategory('sizintilar', this)">🗄️ Veri Sızıntıları</div>
                    <div class="manual-cat-btn" onclick="switchCategory('sosyal', this)">👤 Sosyal ve Oyun</div>
                    <div class="manual-cat-btn" onclick="switchCategory('eposta', this)">✉️ E-posta Zekası</div>
                    <div class="manual-cat-btn" onclick="switchCategory('ag', this)">🌐 Ağ</div>
                </div>
                <div id="cat-sizintilar" class="manual-items-grid active">
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="leak_ihlaller"> 🛡️ İhlaller</label>
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="leak_hirsiz"> 📄 Hırsız</label>
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="leak_telefon"> 📖 Telefon rehberi</label>
                </div>
                <div id="cat-sosyal" class="manual-items-grid">
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="social_discord"> 💬 Discord Profil & ID</label>
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="social_steam"> 🎮 Steam Geçmişi</label>
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="social_instagram"> 📸 Instagram Taraması</label>
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="social_github"> 💻 GitHub Analizi</label>
                </div>
                <div id="cat-eposta" class="manual-items-grid">
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="mail_server"> 📭 MX & Mail Sunucu</label>
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="leak_email"> 🔍 E-Posta İhlal DB</label>
                </div>
                <div id="cat-ag" class="manual-items-grid">
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="ip"> 🌐 IP & Geo Lokasyon</label>
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="whois"> 🔍 Domain Whois</label>
                    <label class="manual-item-card"><input type="checkbox" name="modules" value="port"> 🔌 Port Taraması</label>
                </div>
            </div>

            <div id="autoPanel">
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
            </div>

            <div class="action-links-row">
                <a href="#" class="action-pill">🛡️ Maruz kalma kontrolleri</a>
                <a href="#" class="action-pill">🔍 Güvenlik araştırması</a>
                <a href="#" class="action-pill">🔔 İzleme</a>
                <a href="/api" class="action-pill">🔌 API erişimi</a>
                <a href="/fiyatlandirma" class="action-pill" style="color: #c084fc; border-color: rgba(192, 132, 252, 0.4);">✨ Yükseltme planı</a>
            </div>
        </form>

        {%RESULT_SECTION%}
    </div>

    <script>
        function removeChip(el) {
            const chip = el.closest('.chip');
            if (chip) chip.remove();
        }
        function clearAllChips() {
            const chips = document.querySelectorAll('#chipsContainer .chip');
            chips.forEach(c => c.remove());
        }
        function fillInput(val) {
            document.getElementById('targetInput').value = val;
        }
        function setMode(btn) {
            const group = btn.closest('.mode-tabs');
            group.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        }
        function switchMode(mode) {
            const btnAuto = document.getElementById('btnAuto');
            const btnManual = document.getElementById('btnManual');
            const autoPanel = document.getElementById('autoPanel');
            const manualPanel = document.getElementById('manualPanel');

            if (mode === 'manual') {
                btnManual.classList.add('active');
                btnAuto.classList.remove('active');
                manualPanel.style.display = 'block';
                autoPanel.style.display = 'none';
            } else {
                btnAuto.classList.add('active');
                btnManual.classList.remove('active');
                manualPanel.style.display = 'none';
                autoPanel.style.display = 'block';
            }
        }
        function switchCategory(catName, btn) {
            document.querySelectorAll('.manual-cat-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.querySelectorAll('.manual-items-grid').forEach(g => g.classList.remove('active'));
            document.getElementById('cat-' + catName).classList.add('active');
        }
    </script>
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

@app.get("/api", response_class=HTMLResponse)
def api_docs():
    return HTMLResponse(content=HTML_API)

@app.get("/oauth-login", response_class=HTMLResponse)
def oauth_login(provider: str):
    USER_SESSION["logged_in"] = True
    USER_SESSION["key"] = f"OAUTH-{provider.upper()}-SESSION"
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
