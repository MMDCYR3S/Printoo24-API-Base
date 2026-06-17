const fs = require('fs');
const path = require('path');

// تنظیمات
const ROOT_DIR = './src'; // مسیر اسکن (شروع از src)
const OUTPUT_FILE = 'persian_report.txt';
const EXCLUDE_DIRS = ['node_modules', 'dist', 'build', '.git'];
const EXCLUDE_FEATURE_DIR = path.join('app', 'features', 'admin'); // پوشه ادمین برای اسکیپ شدن

// رجکس برای تشخیص حروف فارسی
const persianRegex = /[\u0600-\u06FF]/;

// تابع بررسی یک خط کد که آیا فارسی خارج از کامنت دارد یا خیر
function hasPersianOutsideComments(line) {
    // پیدا کردن شروع کامنت‌ها
    const jsxCommentStart = line.indexOf('{/*');
    const jsCommentStart = line.indexOf('//');

    let limit = line.length;
    if (jsxCommentStart !== -1) limit = Math.min(limit, jsxCommentStart);
    if (jsCommentStart !== -1) limit = Math.min(limit, jsCommentStart);

    // بخشی از کد که قبل از کامنت است
    const codePart = line.substring(0, limit);

    return persianRegex.test(codePart);
}

// تابع اسکن فایل
function scanFile(filePath, results) {
    const ext = path.extname(filePath).toLowerCase();
    const validExtensions = ['.js', '.jsx', '.ts', '.tsx', '.json', '.html', '.vue'];

    if (!validExtensions.includes(ext)) return;

    try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const lines = content.split('\n');

        lines.forEach((line, index) => {
            if (hasPersianOutsideComments(line)) {
                results.push({
                    file: filePath.replace(/\\/g, '/'),
                    lineNum: index + 1,
                    content: line.trim()
                });
            }
        });
    } catch (error) {
        console.error(`Error reading file ${filePath}:`, error.message);
    }
}

// تابع پیمایش پوشه‌ها به صورت بازگشتی
function walkDir(dir, results) {
    let files;
    try {
        files = fs.readdirSync(dir, { withFileTypes: true });
    } catch (error) {
        return;
    }

    for (const file of files) {
        const fullPath = path.join(dir, file.name);
        const relativePath = fullPath.replace(/\\/g, '/').replace('./', '');

        // بررسی پوشه‌های مستثنی
        if (EXCLUDE_DIRS.includes(file.name)) continue;
        if (relativePath.includes(EXCLUDE_FEATURE_DIR.replace(/\\/g, '/'))) continue;

        if (file.isDirectory()) {
            walkDir(fullPath, results);
        } else {
            scanFile(fullPath, results);
        }
    }
}

// تابع ساخت گزارش
function generateReport(results) {
    if (results.length === 0) {
        fs.writeFileSync(OUTPUT_FILE, 'هیچ متن فارسی‌ای خارج از کامنت‌ها و پوشه ادمین یافت نشد!', 'utf-8');
        console.log('✅ هیچ متنی برای ترجمه یافت نشد!');
        return;
    }

    let output = '📋 گزارش کلمات و جملات فارسی برای ترجمه:\n';
    output += '==========================================\n\n';

    // گروه‌بندی بر اساس فایل
    const grouped = {};
    results.forEach(r => {
        if (!grouped[r.file]) grouped[r.file] = [];
        grouped[r.file].push(r);
    });

    for (const file in grouped) {
        output += `📁 فایل: ${file}\n`;
        output += '------------------------------------------\n';
        grouped[file].forEach(r => {
            output += `[خط ${r.lineNum}] ${r.content}\n`;
        });
        output += '\n';
    }

    fs.writeFileSync(OUTPUT_FILE, output, 'utf-8');
    console.log(`✅ گزارش با موفقیت ساخته شد! تعداد ${results.length} مورد پیدا شد.`);
    console.log(`📄 فایل خروجی: ${OUTPUT_FILE}`);
}

// شروع اسکریپت
console.log('⏳ در حال بررسی فایل‌ها...');
const results = [];
walkDir(ROOT_DIR, results);
generateReport(results);
