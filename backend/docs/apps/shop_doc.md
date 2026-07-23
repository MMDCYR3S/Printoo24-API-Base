<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مستند فنی اپلیکیشن Shop</title>
    <style>:root{--bg-color:#1a1b26;--fg-color:#c0caf5;--card-bg:#24283b;--border-color:#414868;--accent-color:#7aa2f7;--highlight-bg:#bb9af7;--highlight-fg:#1a1b26;--green:#9ece6a;--yellow:#e0af68;--red:#f7768e;}@font-face{font-family:'Vazirmatn';src:url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');font-weight:100 900;font-display:swap;}body{background-color:var(--bg-color);color:var(--fg-color);font-family:'Vazirmatn',-apple-system,BlinkMacSystemFont,"Segoe UI","Roboto","Helvetica Neue",Arial,sans-serif;line-height:1.8;margin:0;padding:0;font-size:16px;}.container{max-width:900px;margin:2rem auto;padding:1rem 2rem;background-color:var(--bg-color);}h1,h2,h3{color:var(--accent-color);font-weight:600;border-bottom:1px solid var(--border-color);padding-bottom:0.5rem;}h1{font-size:2.5rem;text-align:center;border-bottom:none;margin-bottom:0;}.subtitle{text-align:center;color:#a9b1d6;margin-top:0.5rem;font-size:1.1rem;}h2{font-size:2rem;margin-top:3rem;}h3{font-size:1.5rem;color:var(--green);border-bottom-style:dashed;margin-top:2.5rem;}a{color:var(--accent-color);text-decoration:none;transition:color 0.2s ease-in-out;}a:hover{color:var(--highlight-bg);}.key-concept{background-color:rgba(187,154,247,0.1);color:var(--highlight-bg);padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.95em;}pre{background-color:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;padding:1rem;overflow-x:auto;font-family:'Fira Code','Consolas','Monaco',monospace;font-size:0.9rem;line-height:1.6;}code{font-family:inherit;}ul{list-style-type:none;padding-right:20px;}li{position:relative;padding-right:25px;margin-bottom:0.75rem;}li::before{content:'✓';position:absolute;right:0;color:var(--green);font-weight:bold;}.note{background-color:rgba(247,118,142,0.1);border-right:4px solid var(--red);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}.note-info{background-color:rgba(122,162,247,0.1);border-right:4px solid var(--accent-color);padding:1rem 1.5rem;margin:2rem 0;border-radius:4px;}footer{text-align:center;margin-top:4rem;padding-top:2rem;border-top:1px solid var(--border-color);color:#a9b1d6;}</style>
</head>
<body>
    <div class="container">
        <header>
            <h1>مستند فنی اپلیکیشن Shop</h1>
            <p class="subtitle">بررسی ساختار، اجزا و نحوه کارکرد اپلیکیشن فروشگاه در پروژه Printoo24</p>
        </header>
        <main>
            <section id="overview">
                <h2>۱. مرور کلی</h2>
                <p>
                    اپلیکیشن <code>shop</code> مسئول مدیریت عملیات مربوط به فروشگاه در پروژه Printoo24 است. این اپلیکیشن شامل نمایش لیست محصولات، جزئیات محصولات، فیلتر کردن محصولات و محاسبه قیمت نهایی بر اساس ویژگی‌های انتخابی است.
                </p>
                <div class="note-info">
                    <h4>ویژگی‌های کلیدی اپلیکیشن</h4>
                    <ul>
                        <li><strong>نمایش محصولات:</strong> لیست و جزئیات محصولات با قابلیت فیلتر</li>
                        <li><strong>فیلتر پیشرفته:</strong> فیلتر کردن محصولات بر اساس ویژگی‌های مختلف</li>
                        <li><strong>محاسبه قیمت:</strong> محاسبه قیمت نهایی بر اساس ویژگی‌های انتخابی</li>
                        <li><strong>مدیریت ویژگی‌ها:</strong> مدیریت سایز، جنس، آپشن و سایر ویژگی‌های محصولات</li>
                    </ul>
                </div>
            </section>
            <section id="structure">
                <h2>۲. ساختار پوشه‌بندی</h2>
                <p>
                    اپلیکیشن <code>shop</code> دارای ساختار سلسله‌مراتبی و منظمی است که هر بخش مسئولیت خاصی را بر عهده دارد:
                </p>
                <pre dir="ltr"><code>.
├── migrations
│   └── __init__.py
├── services
│   ├── __init__.py
│   ├── product_detail_service.py
│   ├── product_list_service.py
│   └── product_price_cal_service.py
├── __init__.py
├── admin.py
├── apps.py
└── filters.py</code></pre>
                <h3>بررسی هر پوشه و فایل</h3>
                <h4><code>migrations</code></h4>
                <p>
                    این پوشه شامل فایل‌های مربوط به تغییرات ساختار پایگاه داده برای اپلیکیشن است. در حال حاضر تنها فایل <code>__init__.py</code> وجود دارد که نشان‌دهنده عدم اعمال هیچ تغییری در ساختار پایگاه داده توسط این اپلیکیشن است.
                </p>
                <h4><code>services</code></h4>
                <p>
                    پوشه اصلی حاوی منطق تجاری اپلیکیشن است. هر فایل در این پوشه مسئول یک بخش خاص از عملیات فروشگاه است:
                </p>
                <ul>
                    <li><strong><code>product_detail_service.py</code>:</strong> مدیریت نمایش جزئیات یک محصول</li>
                    <li><strong><code>product_list_service.py</code>:</strong> مدیریت نمایش لیست محصولات</li>
                    <li><strong><code>product_price_cal_service.py</code>:</strong> محاسبه قیمت نهایی محصولات</li>
                </ul>
                <h4>فایل‌های ریشه اپلیکیشن</h4>
                <ul>
                    <li><strong><code>admin.py</code>:</strong> ثبت مدل‌های مرتبط با فروشگاه در پنل ادمین جنگو</li>
                    <li><strong><code>apps.py</code>:</strong> پیکربندی اپلیکیشن</li>
                    <li><strong><code>filters.py</code>:</strong> تعریف فیلترهای پیشرفته برای محصولات</li>
                    <li><strong><code>__init__.py</code>:</strong> تبدیل پوشه به پکیج پایتون</li>
                </ul>
            </section>
            <section id="services-details">
                <h2>۳. بررسی جزئیات سرویس‌ها</h2>
                <h3><code>product_detail_service.py</code></h3>
                <p>
                    کلاس <code>ShopProductDetailService</code> مسئول آماده‌سازی جزئیات یک محصول برای نمایش در صفحه جزئیات است:
                </p>
                <pre dir="ltr"><code>class ShopProductDetailService:
    def get_product_detail_for_display(self, slug: str) -> Optional[Dict[str, Any]]:
        """دریافت و آماده‌سازی جزئیات یک محصول برای نمایش"""
        
    def _group_options_by_type(self, options: List[ProductOption]) -> Dict[str, List[ProductOption]]:
        """گروه‌بندی آپشن‌های محصول بر اساس نوع"""</code></pre>
                <h3><code>product_list_service.py</code></h3>
                <p>
                    کلاس <code>ShopProductListService</code> مسئول آماده‌سازی کوئری‌ست پایه برای نمایش لیست محصولات:
                </p>    
                <pre dir="ltr"><code>class ShopProductListService:
    def get_base_queryset(self) -> QuerySet[Product]:
        """کوئری‌ست پایه و بهینه‌سازی شده برای لیست محصولات"""</code></pre>
                <h3><code>product_price_cal_service.py</code></h3>
                <p>
                    کلاس <code>ProductPriceCalculator</code> مسئول محاسبه قیمت نهایی یک محصول بر اساس ویژگی‌های انتخابی:
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
            </section>
            <section id="filters">
                <h2>۴. فیلترهای پیشرفته</h2>
                <h3><code>filters.py</code></h3>
                <p>
                    این فایل شامل کلاس <code>ProductFilter</code> است که فیلترهای پیشرفته برای محصولات را تعریف می‌کند:
                </p>
                <pre dir="ltr"><code>class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(
        field_name='category__slug',
        to_field_name='slug',
        queryset=ProductCategory.objects.all()
    )
    sizes = django_filters.ModelMultipleChoiceFilter(
        field_name='productsize__size__id',
        to_field_name='id',
        queryset=Size.objects.all()
    )
    # ... سایر فیلترها</code></pre>
                <p>
                    فیلترها امکان جستجو و فیلتر کردن محصولات بر اساس ویژگی‌های مختلف را فراهم می‌کنند.
                </p>
            </section>
            <section id="integration">
                <h2>۵. یکپارچه‌سازی با سایر بخش‌ها</h2>
                
                <h3>یکپارچه‌سازی با مدل‌های مشترک</h3>
                <p>
                    اپلیکیشن <code>shop</code> از مدل‌های تعریف شده در اپلیکیشن مشترک <code>core</code> استفاده می‌کند:
                </p>  
                <pre dir="ltr"><code>from core.models import (
    Product,
    ProductCategory,
    ProductMaterial,
    ProductImage,
    ProductSize,
    Size,
    Material,
    ProductQuantity,
    Quantity,
    ProductAttachment,
    Attachment,   
    ProductOption,
    Option,
    OptionValue,
)</code></pre>
                <h3>یکپارچه‌سازی با سرویس‌های مشترک</h3>
                <p>
                    از سرویس‌های مشترک برای دسترسی به داده‌های محصولات استفاده می‌شود:
                </p>
                <pre dir="ltr"><code>from core.common.product.product_services import ProductService</code></pre>
            </section>
        </main>
        <footer>
            <p>جهت اطلاعات بیشتر راجب سرویس‌ها، به <a href="../services/shop_services_doc.md">مستندات سرویس‌های اپلیکیشن shop</a> مراجعه کنید</p>
            <p>مستند فنی تولید شده در تاریخ ۱۴۰۴/۰۸/۲۴</p>
        </footer>
    </div>
</body>
</html>