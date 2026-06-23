// src/app/features/shop/components/OrderWizard.jsx
import React, { useState, useMemo } from 'react';
import { CheckCircle2, AlertCircle } from 'lucide-react';

// ─── Types (JSDoc برای خوانایی) ───────────────────────────────────────────────
/**
 * @typedef {'show'|'hide'|'enable'|'disable'} ConditionAction
 * @typedef {'equals'|'not_equals'|'contains'|'not_contains'|'greater_than'|'less_than'} ConditionOperator
 *
 * @typedef {Object} Condition
 * @property {number}             id
 * @property {number}             trigger_field_id
 * @property {ConditionOperator}  operator
 * @property {number|null}        trigger_choice_id
 * @property {string|null}        trigger_value_text
 * @property {ConditionAction}    action
 *
 * @typedef {Object} Choice
 * @property {number} id
 * @property {string} title
 * @property {number} [order]
 *
 * @typedef {Object} Field
 * @property {number}     id
 * @property {string}     title
 * @property {string}     description
 * @property {string}     field_type   // dropdown | single_select | multi_select | text | textarea | number
 * @property {boolean}    is_required
 * @property {boolean}    is_active
 * @property {number}     [order]
 * @property {Choice[]}   choices
 * @property {Condition[]} conditions
 */

// ─── Condition Engine ─────────────────────────────────────────────────────────

/**
 * یک شرط رو نسبت به مقدار فعلی trigger_field ارزیابی می‌کنه.
 *
 * @param {Condition}   condition
 * @param {any}         triggerValue   مقدار فعلی فیلد trigger شده
 * @returns {boolean}
 */
const evaluateCondition = (condition, triggerValue) => {
  const { operator, trigger_choice_id, trigger_value_text } = condition;

  // مقدار مرجع برای مقایسه (اول choice_id، بعد value_text)
  const reference =
    trigger_choice_id !== null && trigger_choice_id !== undefined
      ? trigger_choice_id
      : trigger_value_text;

  if (reference === null || reference === undefined) return false;

  // نرمال‌سازی مقادیر برای مقایسه
  const normalize = (v) => (v !== null && v !== undefined ? String(v) : '');

  const refStr = normalize(reference);

  // برای multi_select مقدار آرایه‌ایه
  const isMulti = Array.isArray(triggerValue);
  const valueStr = isMulti ? triggerValue.map(normalize) : normalize(triggerValue);

  switch (operator) {
    case 'equals':
      return isMulti
        ? valueStr.includes(refStr)
        : valueStr === refStr;

    case 'not_equals':
      return isMulti
        ? !valueStr.includes(refStr)
        : valueStr !== refStr;

    case 'contains':
      return isMulti
        ? valueStr.includes(refStr)
        : valueStr.includes(refStr);

    case 'not_contains':
      return isMulti
        ? !valueStr.includes(refStr)
        : !valueStr.includes(refStr);

    case 'greater_than': {
      const num = parseFloat(triggerValue);
      const refNum = parseFloat(reference);
      return !isNaN(num) && !isNaN(refNum) && num > refNum;
    }

    case 'less_than': {
      const num = parseFloat(triggerValue);
      const refNum = parseFloat(reference);
      return !isNaN(num) && !isNaN(refNum) && num < refNum;
    }

    default:
      return false;
  }
};

/**
 * وضعیت نهایی یک فیلد رو با توجه به همه شرط‌هاش محاسبه می‌کنه.
 *
 * منطق اولویت‌بندی:
 *  - شرط‌ها به ترتیب id (زمان ثبت) پردازش می‌شن
 *  - آخرین شرط match‌شده غالبه (last-wins)
 *  - visibility و interactivity مستقل از هم ردیابی میشن
 *
 * @param {Field}             field
 * @param {Record<number,any>} selectedOptions   مقادیر فعلی همه فیلدها
 * @returns {{ visible: boolean, enabled: boolean }}
 */
const resolveFieldState = (field, selectedOptions) => {
  // اگه شرطی نداره، همیشه نمایش داده و فعاله
  if (!field.conditions || field.conditions.length === 0) {
    return { visible: true, enabled: true };
  }

  // وضعیت پیش‌فرض — بدون هیچ شرطی همه چیز نمایان و فعاله
  let visible = true;
  let enabled = true;

  // شرط‌ها رو به ترتیب id پردازش کن تا last-wins رعایت بشه
  const sorted = [...field.conditions].sort((a, b) => a.id - b.id);

  for (const condition of sorted) {
    const triggerValue = selectedOptions[condition.trigger_field_id];
    const matched = evaluateCondition(condition, triggerValue);

    if (!matched) continue;

    switch (condition.action) {
      case 'show':    visible = true;  break;
      case 'hide':    visible = false; break;
      case 'enable':  enabled = true;  break;
      case 'disable': enabled = false; break;
      default: break;
    }
  }

  return { visible, enabled };
};

// ─── Sub-components ───────────────────────────────────────────────────────────

/** دکمه‌ی انتخاب که در single و multi_select مشترکه */
const ChoiceButton = ({ choice, isSelected, onClick, disabled }) => (
  <button
    type="button"
    onClick={onClick}
    disabled={disabled}
    className={`
      relative flex flex-col items-center justify-center text-center p-4 rounded-2xl border-2
      transition-all duration-300 overflow-hidden group
      ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
      ${isSelected && !disabled
        ? 'border-primary bg-primary/5 shadow-sm'
        : !disabled
          ? 'border-slate-100 bg-white hover:border-slate-300 hover:bg-slate-50'
          : 'border-slate-100 bg-slate-50'
      }
    `}
  >
    {/* تیک انتخاب */}
    <div
      className={`
        absolute top-2.5 right-2.5 transition-all duration-300
        ${isSelected && !disabled ? 'opacity-100 scale-100' : 'opacity-0 scale-50'}
      `}
    >
      <CheckCircle2 size={18} className="text-primary" fill="currentColor" stroke="white" />
    </div>

    <span
      className={`
        text-xs md:text-sm font-bold z-10 transition-colors mt-1
        ${isSelected && !disabled
          ? 'text-primary'
          : 'text-slate-600 group-hover:text-slate-900'
        }
      `}
    >
      {choice.title}
    </span>
  </button>
);

/** Single select / dropdown */
const SingleSelectField = ({ field, selectedOptions, handleOptionSelect, disabled }) => {
  const currentValue = selectedOptions[field.id];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {field.choices
        ?.slice()
        .sort((a, b) => (a.order || 0) - (b.order || 0))
        .map((choice) => (
          <ChoiceButton
            key={choice.id}
            choice={choice}
            isSelected={String(currentValue) === String(choice.id)}
            disabled={disabled}
            onClick={() => !disabled && handleOptionSelect(field.id, choice.id)}
          />
        ))}
    </div>
  );
};

/**
 * Multi select — local state نگه می‌داره تا re-render پدر state آرایه رو ری‌ست نکنه.
 * وقتی disabled بشه انتخاب‌های قبلی حفظ میشن ولی تغییرپذیر نیستن.
 */
const MultiSelectField = ({ field, selectedOptions, handleOptionSelect, disabled }) => {
  const [selected, setSelected] = useState(() => {
    const val = selectedOptions[field.id];
    return Array.isArray(val) ? val.map(String) : [];
  });

  const toggle = (choiceId) => {
    if (disabled) return;
    const strId = String(choiceId);
    const next = selected.includes(strId)
      ? selected.filter((v) => v !== strId)
      : [...selected, strId];
    setSelected(next);
    handleOptionSelect(field.id, next);
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      {field.choices
        ?.slice()
        .sort((a, b) => (a.order || 0) - (b.order || 0))
        .map((choice) => (
          <ChoiceButton
            key={choice.id}
            choice={choice}
            isSelected={selected.includes(String(choice.id))}
            disabled={disabled}
            onClick={() => toggle(choice.id)}
          />
        ))}
    </div>
  );
};

/** Input متنی / عددی / textarea با پشتیبانی از disabled */
const InputField = ({ field, selectedOptions, handleOptionSelect, disabled }) => {
  const value = selectedOptions[field.id] ?? '';
  const baseClass = `
    w-full px-4 py-3 rounded-2xl border-2 text-sm text-slate-800 placeholder-slate-400
    outline-none transition-all duration-300
    ${disabled
      ? 'border-slate-100 bg-slate-100 text-slate-400 cursor-not-allowed'
      : 'border-slate-100 bg-slate-50 focus:border-primary focus:bg-white'
    }
  `;

  if (field.field_type === 'textarea') {
    return (
      <textarea
        value={value}
        onChange={(e) => !disabled && handleOptionSelect(field.id, e.target.value)}
        placeholder={field.description || ''}
        rows={4}
        disabled={disabled}
        className={`${baseClass} resize-none`}
      />
    );
  }

  return (
    <input
      type={field.field_type === 'number' ? 'number' : 'text'}
      value={value}
      onChange={(e) => !disabled && handleOptionSelect(field.id, e.target.value)}
      placeholder={field.description || (field.field_type === 'number' ? '0' : '')}
      disabled={disabled}
      className={baseClass}
    />
  );
};

// ─── Field renderer ───────────────────────────────────────────────────────────

const FieldContent = ({ field, selectedOptions, handleOptionSelect, disabled }) => {
  switch (field.field_type) {
    case 'dropdown':
    case 'single_select':
      return (
        <SingleSelectField
          field={field}
          selectedOptions={selectedOptions}
          handleOptionSelect={handleOptionSelect}
          disabled={disabled}
        />
      );

    case 'multi_select':
      return (
        <MultiSelectField
          field={field}
          selectedOptions={selectedOptions}
          handleOptionSelect={handleOptionSelect}
          disabled={disabled}
        />
      );

    case 'text':
    case 'textarea':
    case 'number':
      return (
        <InputField
          field={field}
          selectedOptions={selectedOptions}
          handleOptionSelect={handleOptionSelect}
          disabled={disabled}
        />
      );

    default:
      return null;
  }
};

// ─── Main Component ───────────────────────────────────────────────────────────

const OrderWizard = ({ productData, state, setters }) => {
  // ── Guard ──────────────────────────────────────────────────────────────────
  if (!productData || !Array.isArray(productData.fields)) {
    return (
      <div className="w-full h-32 flex items-center justify-center bg-slate-50 rounded-3xl border border-slate-100">
        <span className="loading loading-dots loading-md text-slate-300" />
      </div>
    );
  }

  const selectedOptions  = state?.selectedOptions  || {};
  const handleOptionSelect = setters?.handleOptionSelect || (() => {});

  // ── Condition Engine ───────────────────────────────────────────────────────
  /**
   * برای هر فیلد وضعیت visible/enabled رو محاسبه می‌کنه.
   * useMemo تضمین می‌کنه فقط وقتی selectedOptions عوض میشه دوباره حساب بشه.
   */
  const fieldStates = useMemo(() => {
    const map = {};
    for (const field of productData.fields) {
      if (field.is_active) {
        map[field.id] = resolveFieldState(field, selectedOptions);
      }
    }
    return map;
  }, [productData.fields, selectedOptions]);

  // ── Fields to render ───────────────────────────────────────────────────────
  const fieldsToRender = productData.fields
    .filter((f) => f.is_active && fieldStates[f.id]?.visible)
    .sort((a, b) => (a.order || 0) - (b.order || 0));

  if (fieldsToRender.length === 0) return null;

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="space-y-6">
      {fieldsToRender.map((field) => {
        const { enabled } = fieldStates[field.id] || { enabled: true };

        return (
          <div
            key={field.id}
            className={`
              bg-white p-5 md:p-6 rounded-3xl border border-slate-100 shadow-sm
              transition-all duration-300 hover:shadow-md
              ${!enabled ? 'opacity-60' : ''}
            `}
          >
            {/* هدر فیلد */}
            <div className="flex items-center justify-between mb-4 border-b border-slate-50 pb-3">
              <div className="flex items-center gap-1.5">
                <div className="w-1.5 h-4 bg-primary rounded-full" />
                <h3 className="text-sm md:text-base font-extrabold text-slate-800">
                  {field.title}
                </h3>
                {field.is_required && (
                  <span className="text-rose-500 text-lg leading-none mt-1">*</span>
                )}
              </div>

              {/* نشانگر disabled */}
              {!enabled && (
                <div className="flex items-center gap-1 text-xs text-slate-400">
                  <AlertCircle size={13} />
                  <span>غیرفعال</span>
                </div>
              )}
            </div>

            {/* محتوای فیلد */}
            <FieldContent
              field={field}
              selectedOptions={selectedOptions}
              handleOptionSelect={handleOptionSelect}
              disabled={!enabled}
            />
          </div>
        );
      })}
    </div>
  );
};

export default OrderWizard;