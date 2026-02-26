import * as yup from 'yup';

export const blogCategorySchema = yup.object().shape({
  name: yup.string()
    .required('وارد کردن نام دسته‌بندی الزامی است')
    .min(2, 'نام دسته باید حداقل ۲ کاراکتر باشد'),
  is_active: yup.boolean().default(true),
});