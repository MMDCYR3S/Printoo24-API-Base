# frontend/Dockerfile

FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# پورت پیش فرض وایت
EXPOSE 5173

# نکته طلایی: اضافه کردن --host برای اینکه از بیرون کانتینر دیده بشه
CMD ["npm", "run", "dev", "--", "--host"]
