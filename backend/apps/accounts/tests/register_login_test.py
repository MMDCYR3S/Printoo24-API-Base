from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class AccountAPITests(APITestCase):
    """
    تست‌های یکپارچه (Integration Tests) برای ماژول حساب کاربری (Accounts).
    این کلاس شامل تست‌های مربوط به ثبت‌نام (Register) و ورود (Login) می‌باشد.
    """

    def setUp(self):
        """
        تنظیمات اولیه و آماده‌سازی داده‌های مورد نیاز قبل از اجرای هر تست.
        در این بخش URLها و داده‌های نمونه‌ی کاربر تعریف می‌شوند.
        """
        # ===== تنظیم URLهای اندپوینت‌ها ===== #
        self.register_url = reverse('api:v1:accounts:register') 
        self.login_url = reverse('api:v1:accounts:login')

        # ===== داده‌های نمونه برای ثبت‌نام ===== #
        self.user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
            "password_2": "StrongPassword123!"
        }

    # ========================================== #
    #            TESTS FOR REGISTER              #
    # ========================================== #

    @patch('apps.accounts.services.verify_service.VerificationService.send_verification_code')
    def test_register_user_success(self, mock_send_email):
        """
        تست سناریوی موفقیت‌آمیز ثبت‌نام کاربر.
        
        انتظار می‌رود:
        1. پاسخ با کد وضعیت 201 (Created) بازگردانده شود.
        2. متد ارسال ایمیل تایید (Mock شده) دقیقاً یک بار با ایمیل کاربر صدا زده شود.
        3. رکورد کاربر در دیتابیس ایجاد شده باشد.
        4. توکن‌های احراز هویت (Access و Refresh) در پاسخ وجود داشته باشند.
        """
        # ===== ارسال درخواست ثبت‌نام ===== #
        response = self.client.post(self.register_url, self.user_data)
        
        # ===== بررسی کد وضعیت پاسخ ===== #
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # ===== بررسی فراخوانی سرویس ایمیل ===== #
        mock_send_email.assert_called_once_with(self.user_data['email'])
        
        # ===== بررسی ذخیره‌سازی در دیتابیس ===== #
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
        
        # ===== بررسی وجود توکن در خروجی ===== #
        # نکته: فرض بر این است که باگ مربوط به کلید دیکشنری در View اصلاح شده است.
        self.assertIn('token', response.data) 
        self.assertIn('access', response.data['token']) 

    def test_register_password_mismatch(self):
        """
        تست سناریوی عدم تطابق رمز عبور و تکرار آن.
        
        انتظار می‌رود:
        1. سیستم از ثبت‌نام جلوگیری کند.
        2. کد وضعیت 400 (Bad Request) بازگردانده شود.
        3. پیام خطای مربوط به فیلد password در پاسخ موجود باشد.
        """
        # ===== ایجاد داده با رمز عبور نامعتبر ===== #
        data = self.user_data.copy()
        data['password_2'] = "WrongPassword"
        
        # ===== ارسال درخواست ===== #
        response = self.client.post(self.register_url, data)
        
        # ===== اعتبارسنجی پاسخ خطا ===== #
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_duplicate_email(self):
        """
        تست جلوگیری از ثبت‌نام مجدد با ایمیل تکراری.
        
        انتظار می‌رود:
        1. اگر کاربری قبلاً با یک ایمیل ثبت‌نام کرده باشد، سیستم اجازه ثبت مجدد ندهد.
        2. کد وضعیت 400 بازگردانده شود.
        3. خطای مربوط به فیلد email دریافت شود.
        """
        # ===== پیش‌نیاز: ایجاد کاربر اولیه ===== #
        User.objects.create_user(
            username='existing', 
            email=self.user_data['email'], 
            password='Password123!'
        )
        
        # ===== تلاش برای ثبت‌نام مجدد با همان ایمیل ===== #
        response = self.client.post(self.register_url, self.user_data)
        
        # ===== اعتبارسنجی پاسخ خطا ===== #
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    # ========================================== #
    #              TESTS FOR LOGIN               #
    # ========================================== #

    def test_login_success(self):
        """
        تست سناریوی موفقیت‌آمیز ورود کاربر.
        
        انتظار می‌رود:
        1. با ارسال نام کاربری و رمز عبور صحیح، کد 200 دریافت شود.
        2. توکن‌های Access و Refresh در پاسخ بازگردانده شوند.
        """
        # ===== پیش‌نیاز: ایجاد کاربر در دیتابیس ===== #
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

        login_data = {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }
        
        # ===== ارسال درخواست ورود ===== #
        response = self.client.post(self.login_url, login_data)
        
        # ===== اعتبارسنجی پاسخ موفق ===== #
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """
        تست ورود با اطلاعات احراز هویت نامعتبر (رمز عبور اشتباه).
        
        انتظار می‌رود:
        1. سیستم اجازه ورود ندهد.
        2. کد وضعیت 400 (Bad Request) بازگردانده شود.
        """
        # ===== پیش‌نیاز: ایجاد کاربر ===== #
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )

        # ===== داده‌های ورود با پسورد غلط ===== #
        login_data = {
            "username": self.user_data['username'],
            "password": "WrongPassword!!!"
        }
        
        # ===== ارسال درخواست ===== #
        response = self.client.post(self.login_url, login_data)
        
        # ===== اعتبارسنجی خطا ===== #
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """
        تست جلوگیری از ورود کاربر غیرفعال (Inactive).
        
        انتظار می‌رود:
        1. حتی با رمز عبور صحیح، اگر is_active=False باشد، ورود انجام نشود.
        2. کد وضعیت 400 بازگردانده شود.
        3. پیام خطای مشخص مبنی بر غیرفعال بودن حساب دریافت شود.
        """
        # ===== ایجاد کاربر و غیرفعال کردن آن ===== #
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        user.is_active = False
        user.save()

        login_data = {
            "username": self.user_data['username'],
            "password": self.user_data['password']
        }
        
        # ===== ارسال درخواست ورود ===== #
        response = self.client.post(self.login_url, login_data)
        
        # ===== اعتبارسنجی خطا و پیام مربوطه ===== #
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "حساب کاربری غیرفعال است")
