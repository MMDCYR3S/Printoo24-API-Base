<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی سرویس‌های Shop</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی سرویس‌های Shop</h1>
            <p class="subtitle">بررسی جامع سرویس‌ها و منطق تجاری مربوط به اپلیکیشن فروشگاه در پروژه Printoo24</p>
        </header>
        <main>
            <section id="overview">
                <h2>۱. مرور کلی</h2>
                <p>
                    سرویس‌های اپلیکیشن <code>shop</code> مسئول اجرای منطق تجاری مربوط به عملیات فروشگاه در پروژه Printoo24 هستند. این سرویس‌ها شامل عملیات نمایش لیست و جزئیات محصولات، فیلتر کردن محصولات و محاسبه قیمت نهایی بر اساس ویژگی‌های انتخابی می‌شوند.
                </p>
                <div class="note-info">
                    <h4>ویژگی‌های کلیدی سرویس‌ها</h4>
                    <ul>
                        <li><strong>تقسیم‌بندی منطقی:</strong> هر سرویس مسئولیت خاصی را بر عهده دارد</li>
                        <li><strong>وابستگی کم:</strong> سرویس‌ها از طریق interfaceها با یکدیگر ارتباط دارند</li>
                        <li><strong>تست‌پذیری:</strong> ساختار مناسب برای نوشتن unit test</li>
                        <li><strong>قابلیت توسعه:</strong> امکان افزودن قابلیت‌های جدید بدون تغییر در ساختار کلی</li>
                    </ul>
                </div>
            </section>
            <section id="location">
                <h2>۲. مسیر فایل‌ها</h2>
                <p>
                    سرویس‌های اپلیکیشن shop در مسیر زیر قرار دارند:
                </p>
                <pre dir="ltr"><code>services/customer_site/apps/shop/services/</code></pre>
                <p>
                    این پوشه شامل سه سرویس اصلی برای مدیریت عملیات فروشگاه است.
                </p>
            </section>
            <section id="services">
                <h2>۳. بررسی سرویس‌ها</h2>
                <h3><code>ShopProductDetailService</code></h3>
                <p>
                    سرویس نمایش جزئیات محصول مسئول آماده‌سازی اطلاعات یک محصول برای نمایش در صفحه جزئیات است.
                </p>
                <pre dir="ltr"><code>class ShopProductDetailService:
    def get_product_detail_for_display(self, slug: str) -> Optional[Dict[str, Any]]:
        """دریافت و آماده‌سازی جزئیات یک محصول برای نمایش"""
    def _group_options_by_type(self, options: List[ProductOption]) -> Dict[str, List[ProductOption]]:
        """گروه‌بندی آپشن‌های محصول بر اساس نوع"""</code></pre>
                <h4>عملکرد اصلی</h4>
                <ol>
                    <li>دریافت جزئیات یک محصول از طریق ProductService</li>
                    <li>دریافت تمامی ویژگی‌های مرتبط با محصول (تیراژ، سایز، جنس، آپشن، تصاویر و پیوست‌ها)</li>
                    <li>گروه‌بندی آپشن‌ها بر اساس نوع آن‌ها</li>
                    <li>بازگشت دیکشنری حاوی تمام اطلاعات آماده برای نمایش</li>
                </ol>
                <h3><code>ShopProductListService</code></h3>
                <p>
                    سرویس نمایش لیست محصولات مسئول آماده‌سازی کوئری‌ست پایه برای نمایش لیست محصولات است.
                </p>    
                <pre dir="ltr"><code>class ShopProductListService:
    def get_base_queryset(self) -> QuerySet[Product]:
        """کوئری‌ست پایه و بهینه‌سازی شده برای لیست محصولات"""</code></pre>
                <h4>ویژگی‌های کلیدی</h4>
                <ul>
                    <li><strong>بهینه‌سازی:</strong> استفاده از کوئری‌ست بهینه برای کاهش تعداد درخواست‌های دیتابیس</li>
                    <li><strong>قابلیت فیلتر:</strong> آماده‌سازی کوئری‌ست برای استفاده در فیلترهای پیشرفته</li>
                    <li><strong>فقط محصولات فعال:</strong> تنها محصولات فعال را در نظر می‌گیرد</li>
                </ul>
                <h3><code>ProductPriceCalculator</code></h3>
                <p>
                    محاسبه‌گر قیمت محصولات مسئول محاسبه قیمت نهایی بر اساس ویژگی‌های انتخابی است.
                </p>
                <pre dir="ltr"><code>class ProductPriceCalculator:
    def __init__(
        self,
        product: Product,
        quantity: ProductQuantity,
        material: ProductMaterial,
        options: List[ProductOption],
        size: Optional[ProductSize] = None,
        custom_dimensions: Optional[Dict[str, Union[int, float]]] = None
    ):
        """مقداردهی اولیه محاسبه‌گر قیمت"""
        
    def calculate(self) -> Dict[str, Union[float, str]]:
        """الگوریتم اصلی محاسبه قیمت نهایی"""</code></pre>
                <h4>فرآیند محاسبه قیمت</h4>
                <ol>
                    <li>استخراج قیمت پایه از تیراژ انتخابی</li>
                    <li>محاسبه تأثیر قیمت بر اساس سایز (استاندارد یا دلخواه)</li>
                    <li>جمع‌آوری تأثیر قیمت جنس و آپشن‌ها</li>
                    <li>اعمال ضریب افزایش یا کاهش قیمت</li>
                    <li>محاسبه قیمت نهایی و بازگشت جزئیات کامل</li>
                </ol>
            </section>
            <section id="dependencies">
                <h2>۴. وابستگی‌ها و ارتباطات</h2>
                <p>
                    سرویس‌ها از طریق dependency injection با یکدیگر و با سایر بخش‌های سیستم ارتباط دارند:
                </p>
                <h3>نمودار وابستگی‌ها</h3>
                <pre dir="ltr"><code>ShopProductDetailService ────► ProductService
ShopProductListService ──────► ProductService
ProductPriceCalculator (مستقل)</code></pre>
                <h3>استفاده در عمل</h3>
                <pre dir="ltr"><code># در views یا سایر بخش‌های برنامه
product_service = ProductService(ProductRepository())
product_detail_service = ShopProductDetailService(product_service)
product_list_service = ShopProductListService(product_service)

# برای محاسبه قیمت
price_calculator = ProductPriceCalculator(
    product=product,
    quantity=selected_quantity,
    material=selected_material,
    options=selected_options,
    size=selected_size  # یا custom_dimensions
)
price_details = price_calculator.calculate()</code></pre>
            </section>
            <section id="product-service">
                <h2>۵. ProductService</h2>
                <p>
                    سرویس مشترک برای دسترسی به داده‌های محصولات که توسط سرویس‌های shop استفاده می‌شود:
                </p>
                <pre dir="ltr"><code>class ProductService:
    def get_product_detail_by_slug(self, slug: str) -> Optional[Product]:
        """دریافت جزئیات محصول با استفاده از slug"""
        
    def get_all_active_products(self) -> QuerySet[Product]:
        """دریافت تمام محصولات فعال"""</code></pre>
                <p>
                    این سرویس از ProductRepository برای دسترسی به داده‌ها استفاده می‌کند.
                </p>
            </section>
            <section id="logging">
                <h2>۶. لاگ‌نویسی</h2>
                <p>
                    تمام سرویس‌ها از سیستم لاگ‌نویسی یکپارچه پروژه استفاده می‌کنند:
                </p>            
                <pre dir="ltr"><code># هر سرویس لاگ‌های خود را دارد
logger = logging.getLogger('shop.services.product_detail')
logger = logging.getLogger('shop.services.product_list')
logger = logging.getLogger('shop.services.price_calculator')</code></pre>
                <h3>سطح‌های لاگ‌نویسی</h3>
                <ul>
                    <li><strong>DEBUG:</strong> اطلاعات جزئی برای توسعه‌دهندگان</li>
                    <li><strong>INFO:</strong> اطلاعات کلی درباره عملیات‌ها</li>
                    <li><strong>WARNING:</strong> هشدارها و عملیات مشکوک</li>
                    <li><strong>ERROR:</strong> خطاها و استثناها</li>
                </ul>
            </section>
        </main>
        <footer>
            <p>مستند فنی تولید شده در تاریخ ۱۴۰۴/۰۸/۲۴</p>
        </footer>
    </div>
</body>
</html>