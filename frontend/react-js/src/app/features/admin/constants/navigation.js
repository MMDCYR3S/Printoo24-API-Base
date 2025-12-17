// src/app/features/admin/constants/navigation.js
import { 
  LayoutDashboard, ShoppingCart, Box, Users, 
  MessageSquare, Settings, Layers, Hash, FilePlus, List
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
      { title: 'مدیریت سایزها', path: '/admin/products/sizes', icon: Hash }, // ویژگی‌ها
      { title: 'مدیریت تیراژها', path: '/admin/products/quantities', icon: Hash },
    ]
  },
  {
    title: 'دسته‌بندی‌ها',
    icon: Layers,
    children: [
      { title: 'مدیریت دسته‌ها', path: '/admin/categories', icon: List },
      { title: 'زیر‌دسته‌ها', path: '/admin/categories/sub', icon: Layers }, // اگه جداست
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
    title: 'مشتریان',
    icon: Users,
    children: [
      { title: 'لیست کاربران', path: '/admin/users', icon: List },
      // دیتیل معمولاً روت دینامیک هست و توی منو نمیاد (admin/users/:id)
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
    ]
  },
];