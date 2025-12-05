import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';

const PasswordInput = ({ register, name, error, placeholder = "********" }) => {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="relative">
      <input
        type={showPassword ? "text" : "password"}
        placeholder={placeholder}
        className={`input input-bordered w-full pl-10 ${error ? 'input-error' : ''}`}
        {...register(name)}
      />
      
      {/* دکمه تغییر وضعیت نمایش (چپ‌چین شده برای زبان فارسی) */}
      <button
        type="button"
        className="absolute left-3 top-1/2 -translate-y-1/2 text-base-content/60 hover:text-primary transition-colors"
        onClick={() => setShowPassword(!showPassword)}
      >
        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
      </button>

      {/* نمایش پیام خطا */}
      {error && (
        <span className="text-error text-xs mt-1 block text-right">
          {error.message}
        </span>
      )}
    </div>
  );
};

export default PasswordInput;