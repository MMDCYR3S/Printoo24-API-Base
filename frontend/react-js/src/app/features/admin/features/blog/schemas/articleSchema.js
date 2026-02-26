// src/app/features/admin/articles/schemas/articleSchema.js
import * as yup from 'yup';

export const articleSchema = yup.object().shape({
  title: yup.string()
    .required('وارد کردن عنوان مقاله الزامی است')
    .min(3, 'عنوان باید حداقل ۳ کاراکتر باشد')
    .max(150, 'عنوان نمی‌تواند بیشتر از ۱۵۰ کاراکتر باشد'),
  
  category: yup.string()
    .required('انتخاب دسته‌بندی الزامی است'),
  
  status: yup.string()
    .oneOf(['draft', 'published', 'archived'])
    .default('draft'),
  
  summary: yup.string()
    .nullable()
    .max(300, 'خلاصه مقاله نباید بیشتر از ۳۰۰ کاراکتر باشد'),
  
  read_time: yup.number()
    .transform((value) => (Number.isNaN(value) ? null : value))
    .nullable()
    .min(1, 'زمان مطالعه باید حداقل ۱ دقیقه باشد'),
});