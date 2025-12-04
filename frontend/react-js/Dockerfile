# frontend/Dockerfile

FROM node:22-bookworm

WORKDIR /app

COPY package.json package-lock.json ./

# === این خط را اضافه کنید ===
RUN npm config set registry https://mirror-npm.runflare.com/
# ============================

RUN npm install

COPY . .

# پورت پیش فرض وایت
EXPOSE 5173

# نکته طلایی: اضافه کردن --host برای اینکه از بیرون کانتینر دیده بشه
CMD ["npm", "run", "dev", "--", "--host"]
