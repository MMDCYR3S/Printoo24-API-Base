<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>مستند فنی معماری استقرار React و Nginx</title><style>:root{--bg-color:#0f172a;--fg-color:#e2e8f0;--card-bg:#1e293b;--border-color:#334155;--accent-color:#38bdf8;--highlight-bg:#818cf8;--code-bg:#020617;--green:#4ade80;--yellow:#facc15;--red:#f87171;--purple:#c084fc}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px}.container{max-width:950px;margin:2rem auto;padding:1rem 2rem}header{text-align:center;margin-bottom:3rem;padding-bottom:2rem;border-bottom:1px solid var(--border-color)}h1{font-size:2.2rem;color:var(--accent-color);margin-bottom:0.5rem}h2{font-size:1.6rem;color:var(--fg-color);border-bottom:2px solid var(--border-color);padding-bottom:0.75rem;margin-top:0;display:flex;align-items:center;gap:0.5rem}h3{font-size:1.25rem;color:var(--purple);margin-top:1.5rem}pre{background-color:var(--code-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas',monospace;font-size:0.9rem;direction:ltr;text-align:left}code{font-family:inherit;color:var(--accent-color)}.highlight-text{color:var(--yellow);font-weight:bold}ul{list-style:none;padding:0}li{position:relative;padding-right:1.5rem;margin-bottom:0.75rem}li::before{content:"▹";position:absolute;right:0;color:var(--accent-color)}.architecture-diagram{font-family:monospace;white-space:pre;color:var(--green);line-height:1.2;direction:ltr;text-align:left}.badge{display:inline-block;padding:0.25rem 0.5rem;border-radius:4px;font-size:0.75rem;font-weight:bold;background-color:rgba(56,189,248,0.1);color:var(--accent-color);margin-left:0.5rem}.alert{background-color:rgba(245,158,11,0.1);border-right:4px solid var(--yellow);padding:1rem;border-radius:4px;margin:1.5rem 0}.success{background-color:rgba(74,222,128,0.1);border-right:4px solid var(--green);padding:1rem;border-radius:4px;margin:1.5rem 0}footer{text-align:center;color:#64748b;margin-top:4rem;padding-top:1rem;border-top:1px dashed var(--border-color)}.subtitle{color:#94a3b8;font-size:1.1rem}</style></head><body><div class="container"><header><h1>مستند فنی استقرار React بر بستر Nginx</h1><p class="subtitle">استانداردسازی معماری SPA، پیکربندی Reverse Proxy و رفع خطاهای 404/502</p></header><main><section id="architecture"><h2>۱. چالش‌های معماری SPA و نقش Nginx</h2><p>در اپلیکیشن‌های تک‌صفحه‌ای (SPA) مانند React، تمامی مسیرها (Routes) مجازی هستند و فایل فیزیکی متناظر ندارند. وب‌سرورهای کلاسیک در مواجهه با آدرس‌هایی نظیر <code>/login</code> یا <code>/orders</code> به دلیل عدم یافتن فایل، خطای <strong>404</strong> بازمی‌گردانند.</p><h3>راهکار معماری (The Solution Blueprint)</h3><ul class="architecture-diagram">Request Flow:
Client (Browser)
  │
  ├── URL: /login ───> Nginx Check: File exists? NO ──> Fallback: index.html (200 OK)
  │
  └── URL: /api/* ───> Nginx Check: Pattern Match ──> Proxy Pass: Backend Service (Django)</ul><div class="success"><strong>هدف نهایی:</strong> تبدیل Nginx به یک دروازه‌بان هوشمند که ترافیک استاتیک را به React و ترافیک دیتای JSON را به سرویس‌های Backend هدایت می‌کند.</div></section><section id="nginx-config"><h2>۲. پیکربندی استاندارد (nginx.conf)</h2><p>فایل پیکربندی زیر به گونه‌ای تنظیم شده است که مشکل "صفحه سفید" در رفرش و مشکل "Bad Gateway" در API را به طور کامل مرتفع می‌سازد.</p><pre><code>server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;
    <span style="color:#64748b"># =========================================</span>
    <span style="color:#64748b"># 1. SPA Routing Logic (Fixes 404)</span>
    <span style="color:#64748b"># =========================================</span>
    location / {
        <span style="color:#94a3b8">try_files $uri $uri/ /index.html;</span> <span style="color:#64748b"># <--- Vital Command</span>
    }
    <span style="color:#64748b"># =========================================</span>
    <span style="color:#64748b"># 2. API Reverse Proxy (Fixes 502)</span>
    <span style="color:#64748b"># =========================================</span>
    location /api/ {
        <span style="color:#64748b"># Use Docker Service Name, NOT localhost</span>
        <span style="color:#facc15">proxy_pass http://backend_api:9010;</span>
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}</code></pre><div class="alert"><strong>نکته کلیدی:</strong> در دستور <code>proxy_pass</code> حتماً باید از نام سرویس تعریف شده در <code>docker-compose.yml</code> استفاده شود، نه 127.0.0.1.</div></section><section id="dockerfile"><h2>۳. استراتژی Dockerfile چندمرحله‌ای</h2><p>برای بهینه‌سازی حجم و امنیت، فرآیند بیلد در دو مرحله (Stage) جداگانه انجام می‌شود.</p><pre><code><span style="color:#64748b"># Stage 1: Build React App</span>
FROM node:18-alpine as build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

<span style="color:#64748b"># Stage 2: Serve via Nginx</span>
FROM nginx:alpine
<span style="color:#64748b"># Copy build output to Nginx root</span>
COPY --from=build /app/dist /usr/share/nginx/html
<span style="color:#64748b"># Override default config</span>
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]</code></pre></section><section id="troubleshooting"><h2>۴. راهنمای عیب‌یابی (Troubleshooting)</h2><p>لیست خطاهای رایج و راهکارهای قطعی برای محیط عملیاتی:</p><ul><li><strong>خطای 404 در صفحات داخلی:</strong> دستور <code>try_files</code> در کانفیگ Nginx وجود ندارد یا به درستی تنظیم نشده است.</li><li><strong>خطای 502 Bad Gateway:</strong> نام سرویس در <code>proxy_pass</code> اشتباه است یا کانتینر بک‌‌اند در حال اجرا نیست (Crash کرده است).</li><li><strong>خطای Connection Refused:</strong> در فایل <code>apiClient.js</code> به جای آدرس نسبی، از <code>localhost</code> استفاده شده است که در محیط کانتینری نامعتبر است.</li></ul></section></main><footer><p>تهیه شده برای تیم فنی ShivaTek | مستندات زیرساخت</p></footer></div></body></html>