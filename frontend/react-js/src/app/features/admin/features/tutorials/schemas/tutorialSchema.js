import * as yup from 'yup';

export const tutorialSchema = yup.object().shape({
  title: yup.string()
    .required('عنوان آموزش الزامی است')
    .min(3, 'عنوان باید حداقل ۳ کاراکتر باشد'),
  
  youtube_embed_url: yup.string()
    .required('لینک امبد یوتیوب الزامی است')
    // .url('فرمت لینک نامعتبر است (باید شامل http یا https باشد)')
    // .matches(/youtube\.com\/embed\//, 'لینک باید فرمت Embed یوتیوب باشد (مثال: https://www.youtube.com/embed/...)'),
 , 
  description: yup.string()
    .required('توضیحات کوتاه الزامی است'),

  is_active: yup.boolean().default(true),
});