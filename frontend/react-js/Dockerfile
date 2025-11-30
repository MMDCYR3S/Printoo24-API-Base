# frontend/Dockerfile

FROM node:22-bookworm

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install -y

COPY . .

# پورت پیش فرض وایت
EXPOSE 5173

# نکته طلایی: اضافه کردن --host برای اینکه از بیرون کانتینر دیده بشه
CMD ["npm", "run", "dev", "--", "--host"]
