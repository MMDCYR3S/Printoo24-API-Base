# مستندات API استخراج و ایمپورت محصولات

## 📋 فهرست مطالب
1. [نمای کلی](#نمای-کلی)
2. [نکات مهم](#نکات-مهم)
3. [API Endpoints](#api-endpoints)
4. [مثال‌های کامل](#مثال‌های-کامل)
5. [راهنمای فرانت‌اند](#راهنمای-فرانت‌اند)

---

## 🎯 نمای کلی

این API به ادمین اجازه می‌دهد:
- ✅ استخراج همه یا بخشی از محصولات به Excel (همراه با عکس‌ها، فیلدها و فرمول‌ها)
- ✅ دانلود فایل نمونه برای ایمپورت
- ✅ ایمپورت کامل محصولات از Excel (محصولات، فیلدها، فرمول‌ها و عکس‌ها)
- ✅ مشاهده تاریخچه فایل‌های استخراج شده

**ساختار فایل Excel:**
- Sheet 1: اطلاعات اصلی محصولات
- Sheet 2: فیلدهای داینامیک
- Sheet 3: فرمول‌های قیمت‌گذاری
- Sheet 4: عکس‌ها (URL)
- Sheet 5: فایل‌های پیوست (URL)

---

## ⚠️ نکات مهم

### 1. **عکس‌ها و فایل‌های پیوست**
- ✅ در استخراج: **URL عکس‌ها و فایل‌های پیوست** در Sheet‌های جداگانه استخراج می‌شوند
- ✅ در ایمپورت: عکس‌ها از URL دانلود و به دیتابیس آپلود می‌شوند
- ⚠️ فایل‌های پیوست در این نسخه فقط URLشان ذخیره می‌شود (آپلود پیوست‌ها در نسخه بعدی)

### 2. **فیلدهای داینامیک و فرمول‌ها**
- ✅ در استخراج: شامل می‌شوند (در Sheet‌های جداگانه)
- ✅ در ایمپورت: **همچنین ایجاد می‌شوند** (در یک تراکنش یکپارچه)
- ✅ فرمول‌ها به صورت خودکار ID فیلدهای جدید را پیدا می‌کنند

### 3. **محصولات تکراری**
- در ایمپورت، بر اساس **نام محصول** چک می‌شود
- اگر `update_existing=false` باشد، محصول تکراری نادیده گرفته می‌شود
- اگر `update_existing=true` باشد، محصول به‌روزرسانی می‌شود

### 4. **یکپارچگی داده‌ها (Atomicity)**
- ✅ تمام عملیات ایمپورت در یک **تراکنش atomic** انجام می‌شود
- ✅ اگر هر کدام از مراحل fail شود، **همه چیز rollback می‌شود**
- ✅ هیچ داده ناقصی در دیتابیس ذخیره نمی‌شود

---

## 🔌 API Endpoints

### **Base URL:**
```
/api/v1/dashboard/products-export-import/
```

---

## 📤 1. استخراج محصولات (Export)

### **Endpoint:**
```http
POST /api/v1/dashboard/products-export-import/export/
```

### **Headers:**
```json
{
  "Authorization": "Bearer {token}",
  "Content-Type": "application/json"
}
```

### **Request Body:**
```json
{
  "product_ids": [1, 5, 12],
  "include_fields": true,
  "include_formulas": true
}
```

### **فیلدهای درخواست:**

| فیلد | نوع | اجباری | توضیحات |
|------|-----|--------|---------|
| `product_ids` | Array[Integer] | خیر | لیست ID محصولات (اگر خالی باشد، همه محصولات) |
| `include_fields` | Boolean | خیر | شامل کردن فیلدهای داینامیک (پیش‌فرض: true) |
| `include_formulas` | Boolean | خیر | شامل کردن فرمول‌ها (پیش‌فرض: true) |

### **Response موفق (200):**
```json
{
  "success": true,
  "message": "5 محصول با موفقیت استخراج شد.",
  "file_path": "exports/products/products_export_20260123_143022.xlsx",
  "file_name": "products_export_20260123_143022.xlsx",
  "product_count": 5,
  "download_url": "http://localhost:8000/api/v1/dashboard/products/download/products_export_20260123_143022.xlsx"
}
```

### **Response خطا (400/500):**
```json
{
  "success": false,
  "message": "خطا در استخراج: ..."
}
```

---

## 📥 2. دانلود فایل استخراج شده

### **Endpoint:**
```http
GET /api/v1/dashboard/products-export-import/download/{file_name}
```

### **مثال:**
```http
GET /api/v1/dashboard/products-export-import/download/products_export_20260123_143022.xlsx
```

### **Response:**
- فایل Excel با Content-Type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Header: `Content-Disposition: attachment; filename="products_export_20260123_143022.xlsx"`

---

## 📤 3. ایمپورت محصولات (Import)

### **Endpoint:**
```http
POST /api/v1/dashboard/products-export-import/import/
```

### **Headers:**
```json
{
  "Authorization": "Bearer {token}",
  "Content-Type": "multipart/form-data"
}
```

### **Request Body (Form Data):**
```
file: <فایل Excel>
update_existing: true
skip_errors: true
```

### **فیلدهای درخواست:**

| فیلد | نوع | اجباری | توضیحات |
|------|-----|--------|---------|
| `file` | File | بله | فایل Excel با فرمت .xlsx |
| `update_existing` | Boolean | خیر | به‌روزرسانی محصولات تکراری (پیش‌فرض: false) |
| `skip_errors` | Boolean | خیر | ادامه در صورت خطا (پیش‌فرض: true) |

### **Response موفق (200):**
```json
{
  "success": true,
  "message": "ایمپورت تکمیم شد: 10 موفق، 2 ناموفق.",
  "imported_count": 10,
  "failed_count": 2,
  "errors": [
    "سطر 5: نام محصول نمی‌تواند خالی باشد.",
    "سطر 12: خطا در ذخیره محصول: ..."
  ]
}
```

### **Response خطا (400/500):**
```json
{
  "success": false,
  "message": "خطا در ایمپورت: ...",
  "imported_count": 0,
  "failed_count": 0,
  "errors": ["..."]
}
```

---

## 📄 4. دانلود فایل نمونه (Template)

### **Endpoint:**
```http
GET /api/v1/dashboard/products-export-import/template/
```

### **Response:**
```json
{
  "success": true,
  "message": "فایل نمونه با موفقیت ایجاد شد.",
  "file_path": "templates/products/products_import_template_20260123_143022.xlsx",
  "file_name": "products_import_template_20260123_143022.xlsx",
  "download_url": "http://localhost:8000/api/v1/dashboard/products/download-template/products_import_template_20260123_143022.xlsx"
}
```

### **دانلود فایل نمونه:**
```http
GET /api/v1/dashboard/products-export-import/download-template/{file_name}
```

---

## 📊 5. تاریخچه استخراج‌ها

### **Endpoint:**
```http
GET /api/v1/dashboard/products-export-import/history/
```

### **Response:**
```json
{
  "success": true,
  "files": [
    {
      "file_name": "products_export_20260123_143022.xlsx",
      "file_path": "exports/products/products_export_20260123_143022.xlsx",
      "size": 15420,
      "created_at": "2026-01-23 14:30:22",
      "download_url": "http://localhost:8000/api/v1/dashboard/products/download/products_export_20260123_143022.xlsx"
    }
  ]
}
```

---

## 💡 مثال‌های کامل

### **مثال 1: استخراج همه محصولات**

```javascript
// Frontend Code (React/Vue/Plain JS)
async function exportAllProducts() {
  const response = await fetch('/api/v1/dashboard/products-export-import/export/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      product_ids: [],
      include_fields: true,
      include_formulas: true
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // دانلود فایل
    window.open(data.download_url, '_blank');
    console.log(`استخراج ${data.product_count} محصول`);
  } else {
    console.error('خطا:', data.message);
  }
}
```

### **مثال 2: استخراج محصولات انتخابی**

```javascript
async function exportSelectedProducts(productIds) {
  const response = await fetch('/api/v1/dashboard/products-export-import/export/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      product_ids: productIds,  // [1, 5, 12]
      include_fields: true,
      include_formulas: false
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    window.open(data.download_url, '_blank');
  }
}
```

### **مثال 3: دانلود فایل نمونه**

```javascript
async function downloadTemplate() {
  const response = await fetch('/api/v1/dashboard/products-export-import/template/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  if (data.success) {
    window.open(data.download_url, '_blank');
  }
}
```

### **مثال 4: ایمپورت محصولات**

```javascript
async function importProducts(file) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('update_existing', 'true');
  formData.append('skip_errors', 'true');
  
  const response = await fetch('/api/v1/dashboard/products-export-import/import/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
      // نکته: Content-Type را خودکار تنظیم نکنید، FormData خودش تنظیم می‌کند
    },
    body: formData
  });
  
  const data = await response.json();
  
  if (data.success) {
    alert(`ایمپورت موفق: ${data.imported_count} محصول\nخطاها: ${data.failed_count}`);
    if (data.errors.length > 0) {
      console.log('خطاها:', data.errors);
    }
  } else {
    alert('خطا در ایمپورت:', data.message);
  }
}

// استفاده از input file
document.getElementById('importFileInput').addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    importProducts(file);
  }
});
```

### **مثال 5: مشاهده تاریخچه**

```javascript
async function getExportHistory() {
  const response = await fetch('/api/v1/dashboard/products-export-import/history/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  if (data.success) {
    data.files.forEach(file => {
      console.log(`فایل: ${file.file_name}`);
      console.log(`تاریخ: ${file.created_at}`);
      console.log(`حجم: ${file.size} بایت`);
      console.log(`دانلود: ${file.download_url}`);
    });
  }
}
```

---

## 🛠️ راهنمای فرانت‌اند

### **1. ساختار UI پیشنهادی:**

```
┌─────────────────────────────────────────┐
│  مدیریت محصولات                          │
├─────────────────────────────────────────┤
│                                         │
│  [📤 استخراج به Excel]  [📥 ایمپورت از Excel]  │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  لیست محصولات                            │
│  ☑️ محصول 1    [✏️] [🗑️]                │
│  ☑️ محصول 2    [✏️] [🗑️]                │
│  ☑️ محصول 3    [✏️] [🗑️]                │
│                                         │
│  [استخراج موارد انتخابی]                  │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  تاریخچه استخراج‌ها                       │
│  📄 products_export_20260123.xlsx  [دانلود] [🗑️] │
│  📄 products_export_20260122.xlsx  [دانلود] [🗑️] │
│                                         │
└─────────────────────────────────────────┘
```

### **2. نکات پیاده‌سازی:**

#### **A. استخراج محصولات:**
```javascript
// 1. کاربر دکمه "استخراج همه" یا "استخراج موارد انتخابی" را می‌زند
// 2. درخواست POST به endpoint export ارسال می‌شود
// 3. در پاسخ، download_url دریافت می‌شود
// 4. فایل در tab جدید باز می‌شود (window.open)
// 5. پیام موفقیت به کاربر نمایش داده می‌شود
```

#### **B. ایمپورت محصولات:**
```javascript
// 1. کاربر دکمه "دانلود فایل نمونه" را می‌زند
// 2. فایل نمونه را باز می‌کند و پر می‌کند
// 3. فایل را آپلود می‌کند (input type="file")
// 4. درخواست POST با FormData ارسال می‌شود
// 5. در پاسخ، تعداد موفق و ناموفق نمایش داده می‌شود
// 6. در صورت وجود خطا، لیست خطاها به کاربر نشان داده می‌شود
```

#### **C. نمایش پیشرفت:**
```javascript
// برای عملیات بزرگ، از loading indicator استفاده کنید
async function importProducts(file) {
  showLoading('در حال ایمپورت...');
  
  try {
    const response = await fetch('/api/v1/dashboard/products-export-import/import/', {
      // ...
    });
    
    const data = await response.json();
    hideLoading();
    
    if (data.success) {
      showSuccess(`ایمپورت موفق: ${data.imported_count} محصول`);
    } else {
      showError(data.message);
    }
  } catch (error) {
    hideLoading();
    showError('خطا در ارتباط با سرور');
  }
}
```

### **3. مدیریت خطاها:**

```javascript
// خطاهای رایج:
// 1. خطا در اعتبارسنجی فایل
if (response.status === 400) {
  const data = await response.json();
  alert('خطا در فایل: ' + data.message);
}

// 2. خطا در سرور
if (response.status === 500) {
  alert('خطای سرور، لطفاً بعداً تلاش کنید');
}

// 3. خطا در دانلود فایل
if (response.status === 404) {
  alert('فایل یافت نشد، ممکن است منقضی شده باشد');
}
```

### **4. بهینه‌سازی:**

```javascript
// A. Debounce برای درخواست‌های متوالی
let exportTimeout;
function handleExport() {
  clearTimeout(exportTimeout);
  exportTimeout = setTimeout(() => {
    exportProducts();
  }, 500);
}

// B. Cancel Token برای cancel کردن درخواست
const controller = new AbortController();
fetch(url, { signal: controller.signal });

// برای cancel:
controller.abort();

// C. Progress bar برای فایل‌های بزرگ
const formData = new FormData();
formData.append('file', file);

const xhr = new XMLHttpRequest();
xhr.upload.addEventListener('progress', (e) => {
  if (e.lengthComputable) {
    const percent = (e.loaded / e.total) * 100;
    updateProgressBar(percent);
  }
});
```

---

## 🔒 احراز هویت

تمام endpoint‌ها نیاز به توکن JWT دارند:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📝 نکات تکمیلی

### **1. محدودیت‌ها:**
- حداکثر حجم فایل: 10MB (قابل تغییر در settings)
- حداکثر تعداد محصولات در یک استخراج: 1000 (برای جلوگیری از timeout)
- فرمت فایل: فقط .xlsx (فرمت .xls پشتیبانی نمی‌شود)

### **2. Performance:**
- برای محصولات زیاد (بیش از 100)، از Celery task استفاده کنید
- فایل‌های استخراج شده بعد از 24 ساعت به صورت خودکار حذف می‌شوند (قابل تنظیم)

### **3. امنیت:**
- فقط ادمین‌ها می‌توانند از این API استفاده کنند
- فایل‌های آپلود شده در یک دایرکتوری موقت ذخیره می‌شوند و بعد از پردازش حذف می‌شوند

---

## 🆘 پشتیبانی

در صورت بروز مشکل:
1. لاگ‌های سرور را بررسی کنید
2. فایل Excel را با Excel یا LibreOffice باز کنید (Google Sheets ممکن است فرمت را خراب کند)
3. از Validation Errorهای گزارش شده در ایمپورت استفاده کنید

---

## 📌 TODO (برای نسخه‌های آینده)

- [ ] استخراج و ایمپورت عکس‌ها و فایل‌های پیوست
- [ ] پشتیبانی از .xls (فرمت قدیمی Excel)
- [ ] ایمپورت فیلدهای داینامیک و فرمول‌ها
- [ ] استخراج دسته‌بندی‌ها به صورت جداگانه
- [ ] امکان استخراج partial (فقط فیلدهای انتخابی)
- [ ] پیش‌نمایش داده‌ها قبل از ایمپورت
- [ ] Rollback در صورت خطا در ایمپورت

---

**نسخه:** 1.0.0  
**تاریخ ایجاد:** 2026-01-23  
**آخرین به‌روزرسانی:** 2026-01-23