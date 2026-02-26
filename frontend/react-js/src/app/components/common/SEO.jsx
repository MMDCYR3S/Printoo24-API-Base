import { Helmet } from 'react-helmet-async';

const SEO = ({ 
  title, 
  description, 
  keywords, 
  ogImage, 
  ogUrl, 
  type = 'website',
  author = 'Printoo24'
}) => {
  // عنوان سایت را به صورت پیش‌فرض اضافه می‌کنیم
  const siteTitle = title ? `${title} | پرینتو۲۴` : 'پرینتو۲۴ | خدمات چاپ آنلاین';
  
  return (
    <Helmet>
      {/* تگ‌های پایه */}
      <title>{siteTitle}</title>
      <meta name="description" content={description || 'خدمات چاپ آنلاین با بهترین کیفیت در پرینتو۲۴'} />
      {keywords && <meta name="keywords" content={keywords} />}
      <meta name="author" content={author} />

      {/* تگ‌های Open Graph برای شبکه‌های اجتماعی */}
      <meta property="og:title" content={siteTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:type" content={type} />
      {ogUrl && <meta property="og:url" content={ogUrl} />}
      {ogImage && <meta property="og:image" content={ogImage} />}
      <meta property="og:site_name" content="Printoo24" />

      {/* تگ‌های توییتر */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={siteTitle} />
      <meta name="twitter:description" content={description} />
      {ogImage && <meta name="twitter:image" content={ogImage} />}
    </Helmet>
  );
};

export default SEO;