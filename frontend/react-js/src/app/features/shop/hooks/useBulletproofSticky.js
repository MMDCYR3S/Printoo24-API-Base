// src/app/features/shop/hooks/useBulletproofSticky.js
import { useEffect, useRef, useState } from 'react';

/**
 * useBulletproofSticky
 * ─────────────────────────────────────────────────────────────────────────────
 * یک hook پنج‌لایه برای تضمین رفتار sticky حتی زمانی که CSS position:sticky
 * به دلیل ancestorهای دارای overflow (یا transform/filter) شکست می‌خورد.
 *
 * لایه‌ها:
 *   1. CSS sticky اولیه — اگر کار کرد، هیچ چیز اضافه‌ای لازم نیست.
 *   2. Ancestor Sanitizer (تا <html>) — تمام ancestorها حتی <body> و <html>
 *      را بررسی می‌کند. هرکدام که overflow غیر visible دارد، آن را به clip/visible
 *      تبدیل می‌کند. (clip جلوی scroll افقی را می‌گیرد ولی scroll container نمی‌سازد)
 *   3. تشخیص هوشمند scroll container واقعی — به‌جای اینکه روی window scroll
 *      listen کنیم، نزدیک‌ترین scrollable ancestor را پیدا می‌کنیم و روی آن listen می‌کنیم.
 *   4. JS Fixed Fallback — اگر CSS sticky کار نکرد، با scroll listener، element را
 *      position:fixed می‌کند با width و left گرفته‌شده از wrapper (الگوی Stickybits).
 *   5. ResizeObserver — اگر محتوای داخلی تغییر کرد (مثلاً AdminOrderPanel باز شد)،
 *      ابعاد را دوباره می‌گیریم.
 *
 * @param {Object}   options
 * @param {number}   [options.top=96]    فاصله از بالای viewport به پیکسل
 * @param {boolean}  [options.debug=false]  لاگ دیباگ در console
 * @returns {{ wrapperRef, stickyRef, isStuck }}
 */
export const useBulletproofSticky = ({ top = 96, debug = false } = {}) => {
  const wrapperRef = useRef(null);
  const stickyRef = useRef(null);
  const [isStuck, setIsStuck] = useState(false);

  const originalStylesRef = useRef([]);

  useEffect(() => {
    const wrapper = wrapperRef.current;
    const sticky = stickyRef.current;
    if (!wrapper || !sticky) return;

    // ─────────────────────────────────────────────────────────────────────
    // لایه ۲: Ancestor Sanitizer — این بار تا <html> (شامل body و html)
    // ─────────────────────────────────────────────────────────────────────
    const overflowRegex = /^(hidden|auto|scroll)$/;
    // عناصر قابل قبول برای sanitize: هر ancestor + body + html
    const collectAncestors = () => {
      const list = [];
      let node = wrapper.parentElement;
      while (node) {
        list.push(node);
        node = node.parentElement;
      }
      // اطمینان از حضور body و html
      if (document.body && !list.includes(document.body)) list.push(document.body);
      if (document.documentElement && !list.includes(document.documentElement))
        list.push(document.documentElement);
      return list;
    };

    const sanitizeAncestors = () => {
      originalStylesRef.current = [];
      const ancestors = collectAncestors();
      ancestors.forEach((node, depth) => {
        const computed = window.getComputedStyle(node);
        const ox = computed.overflowX;
        const oy = computed.overflowY;
        const o = computed.overflow;
        const tag =
          node.tagName.toLowerCase() +
          (node.id ? '#' + node.id : '') +
          (node.className && typeof node.className === 'string'
            ? '.' + node.className.split(' ').filter(Boolean).join('.')
            : '');

        const offenderX = overflowRegex.test(ox);
        const offenderY = overflowRegex.test(oy);
        const offenderO = overflowRegex.test(o);
        const offender = offenderX || offenderY || offenderO;

        if (offender) {
          if (debug) {
            console.warn(
              `[useBulletproofSticky] Ancestor #${depth} <${tag}> has overflow (x:${ox} y:${oy} o:${o}) — sanitizing to clip/visible`
            );
          }
          originalStylesRef.current.push({
            node,
            overflowX: node.style.overflowX,
            overflowY: node.style.overflowY,
            overflow: node.style.overflow,
          });
          // clip جلوی horizontal scroll را می‌گیرد ولی sticky را نمی‌شکند
          // visible برای overflow-y اجازه می‌دهد عنصر بچسبد
          node.style.overflowX = 'clip';
          node.style.overflowY = 'visible';
          node.style.overflow = 'visible';
        } else if (debug && depth < 8) {
          console.log(
            `[useBulletproofSticky] Ancestor #${depth} <${tag}> OK (x:${ox} y:${oy})`
          );
        }
      });
    };

    sanitizeAncestors();

    // ─────────────────────────────────────────────────────────────────────
    // لایه ۳: تشخیص scroll container واقعی (نزدیک‌ترین scrollable ancestor)
    // بعد از sanitize، ممکن است هنوز یک scrollable ancestor وجود داشته باشد
    // (مثلاً اگر کاربر خودش یک overflow:auto دلخواه گذاشته باشد).
    // در غیر این صورت، scroll container واقعی = window (document.scrollingElement).
    // ─────────────────────────────────────────────────────────────────────
    const findScrollContainer = () => {
      let node = wrapper.parentElement;
      while (node && node !== document.body) {
        const cs = window.getComputedStyle(node);
        const oy = cs.overflowY;
        if (oy === 'auto' || oy === 'scroll') {
          return node;
        }
        node = node.parentElement;
      }
      // fallback: window (viewport scroll)
      return null;
    };

    const scrollContainer = findScrollContainer();
    const scrollTarget = scrollContainer || window;
      if (debug) {
        console.log(
          `[useBulletproofSticky] Scroll container detected:`,
          scrollContainer ? scrollContainer.tagName + (scrollContainer.id ? '#' + scrollContainer.id : '') : 'window (viewport)'
        );
      }

    // ─────────────────────────────────────────────────────────────────────
    // لایه ۴: JS Fixed Fallback (الگوی Stickybits)
    // ─────────────────────────────────────────────────────────────────────
    let jsMode = false;
    let savedWidth = 0;
    let savedLeft = 0;

    const captureDimensions = () => {
      const rect = wrapper.getBoundingClientRect();
      savedWidth = wrapper.clientWidth;
      savedLeft = rect.left;
    };

    const applyFixed = () => {
      sticky.style.position = 'fixed';
      sticky.style.top = `${top}px`;
      sticky.style.width = `${savedWidth}px`;
      sticky.style.left = `${savedLeft}px`;
      sticky.style.zIndex = '30';
      // حفظ layout: وقتی فرزند fixed می‌شود، ارتفاع wrapper به 0 می‌رسد.
      wrapper.style.minHeight = `${sticky.scrollHeight}px`;
      setIsStuck(true);
    };

    const revertFixed = () => {
      sticky.style.position = '';
      sticky.style.top = '';
      sticky.style.width = '';
      sticky.style.left = '';
      sticky.style.zIndex = '';
      wrapper.style.minHeight = '';
      setIsStuck(false);
    };

    const onScroll = () => {
      const wrapperRect = wrapper.getBoundingClientRect();
      const shouldBeStuck = wrapperRect.top < top;

      if (!shouldBeStuck) {
        if (jsMode) {
          revertFixed();
          jsMode = false;
        }
        return;
      }

      // حالا باید sticky باشد. چک کنیم CSS sticky کار کرده یا نه.
      const stickyRect = sticky.getBoundingClientRect();
      const cssStickyWorking = Math.abs(stickyRect.top - top) < 2;

      if (cssStickyWorking) {
        if (jsMode) {
          revertFixed();
          jsMode = false;
          if (debug)
            console.log('[useBulletproofSticky] CSS sticky is working — JS fallback disabled');
        }
        return;
      }

      // CSS sticky شکست خورده → فعال‌سازی JS mode
      if (!jsMode) {
        captureDimensions();
        jsMode = true;
        if (debug)
          console.log(
            '[useBulletproofSticky] CSS sticky failed — enabling JS fixed fallback',
            { width: savedWidth, left: savedLeft }
          );
      }
      applyFixed();
    };

    const onResize = () => {
      if (jsMode) {
        captureDimensions();
        applyFixed();
      } else {
        // بعد از resize، sanitize دوباره چون ممکن است ancestor جدیدی اضافه شده باشد
        sanitizeAncestors();
        onScroll();
      }
    };

    // اجرای اولیه
    onScroll();

    // listeners — هم روی scroll container واقعی و هم روی window (پشتیبان)
    scrollTarget.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onResize);

    // ─────────────────────────────────────────────────────────────────────
    // لایه ۵: ResizeObserver
    // ─────────────────────────────────────────────────────────────────────
    const ro = new ResizeObserver(() => {
      if (jsMode) {
        captureDimensions();
        applyFixed();
      } else {
        onScroll();
      }
    });
    ro.observe(sticky);
    ro.observe(wrapper);

    // cleanup
    return () => {
      scrollTarget.removeEventListener('scroll', onScroll);
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onResize);
      ro.disconnect();
      // restore ancestors
      for (const item of originalStylesRef.current) {
        item.node.style.overflowX = item.overflowX;
        item.node.style.overflowY = item.overflowY;
        item.node.style.overflow = item.overflow;
      }
      revertFixed();
    };
  }, [top, debug]);

  return { wrapperRef, stickyRef, isStuck };
};

export default useBulletproofSticky;
