// src/app/features/admin/constants/navigation.js
import { 
  LayoutDashboard, ShoppingCart, Box, Users, 
  MessageSquare, Settings, Layers, Hash, FilePlus, List , Map , MapPin,
  BookOpen , Book , Video
} from 'lucide-react';

export const ADMIN_NAVIGATION = [
  {
    title: 'داشبورد',
    path: '/admin',
    icon: LayoutDashboard,
  },
  {
    title: 'محصولات',
    icon: Box,
    children: [
      { title: 'لیست محصولات', path: '/admin/products', icon: List },
      { title: 'ایجاد محصول جدید', path: '/admin/products/create', icon: FilePlus },
      // { title: 'مدیریت سایزها', path: '/admin/products/sizes', icon: Hash }, 
      // { title: 'مدیریت تیراژها', path: '/admin/products/quantities', icon: Hash },
    ]
  },
  {
    title: 'دسته‌بندی‌ها',
    icon: Layers,
    children: [
      { title: 'مدیریت دسته‌ها', path: '/admin/categories', icon: List },
      { title: 'زیر‌دسته‌ها', path: '/admin/categories/sub', icon: Layers },
    ]
  },
  {
    title: 'مناطق جغرافیایی',
    icon: Map, 
    children: [
      { title: 'مدیریت استان‌ها', path: '/admin/provinces', icon: Layers },
      { title: 'مدیریت شهرها', path: '/admin/cities', icon: MapPin },
    ]
  },
  {
    title: 'سفارشات',
    icon: ShoppingCart,
    children: [
      { title: 'لیست سفارشات', path: '/admin/orders', icon: List },
      { title: 'ثبت سفارش دستی', path: '/admin/orders/create', icon: FilePlus },
    ]
  },
    {
    title: 'بلاگ',
    icon: BookOpen, // آیکون بلاگ
    children: [
      { title: 'دسته‌بندی‌های بلاگ', path: '/admin/blog-categories', icon: Layers },
      { title: 'مقالات', path: '/admin/articles', icon: Book },
      { title: 'نوشتن مقاله جدید', path: '/admin/articles/new', icon: Book },
    ]
  },
    {
    title: 'آموزش ها',
    icon: Video , 
    children: [
      { title: 'آموزش ها', path: '/admin/Tutorials', icon: Book },
      { title: 'ایجاد آموزش جدید', path: '/admin/Tutorials/new', icon: Book },
    ]
  },
  {
    title: 'مشتریان',
    icon: Users,
    children: [
      { title: 'لیست کاربران', path: '/admin/users', icon: List },
    ]
  },
  {
    title: 'پیام‌ها',
    icon: MessageSquare,
    children: [
      { title: 'صندوق ورودی', path: '/admin/messages', icon: List },
    ]
  },
  {
    title: 'تنظیمات سایت',
    icon: Settings,
    children: [
      { title: 'اسلایدر صفحه اصلی', path: '/admin/settings/sliders', icon: Layers },
      { title: 'مودال‌های اطلاع‌رسانی', path: '/admin/settings/modals', icon: MessageSquare },
      { title: 'نوار هدر', path: '/admin/settings/media', icon: Settings }
    ]
  },
];