// src/app/hooks/useStickyFix.js
import { useLayoutEffect } from 'react';

/**
 * useStickyFix — Fix قطعی برای مشکل sticky با JavaScript
 * ─────────────────────────────────────────────────────────────────────────────
 *
 * 📖 منبع تحقیق:
 *   - Stack Overflow: "body { overflow-x: hidden; } breaks position: sticky"
 *     https://stackoverflow.com/questions/45530235
 *   - CSS-Tricks: "Dealing with overflow and position: sticky;"
 *     https://css-tricks.com/dealing-with-overflow-and-position-sticky/
 *   - Philip Walton (نویسنده Flexbox spec): "flex items ignore their parent
 *     container's height if it's set via the min-height property"
 *
 * 🎯 علت مشکل:
 *   وقتی <html> یا <body> مقدار overflow-x: hidden دارند، مرورگر طبق CSS Spec
 *   به‌طور خودکار overflow-y را از visible به auto تبدیل می‌کند. این یعنی
 *   <html> و <body> تبدیل به scroll container می‌شوند. sticky به نزدیک‌ترین
 *   scrollable ancestor می‌چسبد، پس به <body> می‌چسبد. ولی viewport scroll
 *   می‌کند، نه <body>. پس sticky هیچ‌وقت نمی‌چسبد!
 *
 * ✅ راه‌حل:
 *   با useLayoutEffect (که قبل از paint اجرا می‌شود)، تمام ancestorها از
 *   sticky element تا <html> را بررسی می‌کنیم. هرکدام که overflow غیر visible
 *   دارد، با !important به visible تبدیل می‌کنیم. JavaScript با !important
 *   همیشه CSS را override می‌کند (حتی اگر CSS خودش !important داشته باشد).
 *
 *   برای جلوگیری از horizontal scroll که overflow-x:hidden قرار بود بگیرد،
 *   از overflow-x: clip استفاده می‌کنیم که طبق CSS Spec scroll container
 *   نمی‌سازد.
 *
 * @param {Object} options
 * @param {React.RefObject} options.targetRef - ref روی sticky element
 * @param {boolean} [options.debug=false]
 */
export const useStickyFix = ({ targetRef, debug = false } = {}) => {
  useLayoutEffect(() => {
    if (!targetRef?.current) return;

    const target = targetRef.current;
    const fixedNodes = []; // برای restore در cleanup

    /**
     * اعمال یک style با !important از طریق setProperty.
     * این روش حتی از CSS با !important هم بالاتر است (inline style precedence).
     */
    const forceStyle = (el, prop, value) => {
      const original = el.style.getPropertyValue(prop);
      const originalPriority = el.style.getPropertyPriority(prop);
      fixedNodes.push({ el, prop, original, originalPriority });
      el.style.setProperty(prop, value, 'important');
    };

    /**
     * پیمایش تمام ancestorها از target تا <html> (شامل body و html).
     */
    const fixAncestors = () => {
      const overflowRegex = /^(hidden|auto|scroll|clip)$/;
      let node = target.parentElement;
      let depth = 0;

      while (node) {
        const cs = window.getComputedStyle(node);
        const ox = cs.overflowX;
        const oy = cs.overflowY;
        const o = cs.overflow;
        const transform = cs.transform;
        const filter = cs.filter;
        const willChange = cs.willChange;
        const contain = cs.contain;

        const tag =
          node.tagName.toLowerCase() +
          (node.id ? '#' + node.id : '') +
          (node.className && typeof node.className === 'string'
            ? '.' + node.className.split(' ').filter(Boolean).join('.')
            : '');

        // ۱. overflow مشکل‌دار → fix به clip/visible
        if (overflowRegex.test(ox) || overflowRegex.test(oy) || overflowRegex.test(o)) {
          if (debug) {
            console.warn(
              `[useStickyFix] #${depth} <${tag}> has overflow (x:${ox} y:${oy} o:${o}) — forcing clip/visible`
            );
          }
          // clip جلوی horizontal scroll را می‌گیرد ولی scroll container نمی‌سازد
          forceStyle(node, 'overflow-x', 'clip');
          forceStyle(node, 'overflow-y', 'visible');
          forceStyle(node, 'overflow', 'visible');
        } else if (debug && depth < 8) {
          console.log(`[useStickyFix] #${depth} <${tag}> overflow OK (x:${ox} y:${oy})`);
        }

        // ۲. transform/filter/will-change/contain هم containing block جدید
        //    برای sticky/fixed می‌سازند → باید reset شوند
        if (transform && transform !== 'none') {
          if (debug) {
            console.warn(`[useStickyFix] #${depth} <${tag}> has transform: ${transform} — resetting`);
          }
          forceStyle(node, 'transform', 'none');
        }
        if (filter && filter !== 'none') {
          if (debug) {
            console.warn(`[useStickyFix] #${depth} <${tag}> has filter: ${filter} — resetting`);
          }
          forceStyle(node, 'filter', 'none');
        }
        if (willChange && willChange !== 'auto') {
          if (debug) {
            console.warn(`[useStickyFix] #${depth} <${tag}> has will-change: ${willChange} — resetting`);
          }
          forceStyle(node, 'will-change', 'auto');
        }
        if (contain && contain !== 'none') {
          if (debug) {
            console.warn(`[useStickyFix] #${depth} <${tag}> has contain: ${contain} — resetting`);
          }
          forceStyle(node, 'contain', 'none');
        }

        node = node.parentElement;
        depth++;
      }

      // ۳. <html> و <body> را به‌طور خاص fix کنیم (بدون توجه به loop بالا)
      const html = document.documentElement;
      const body = document.body;
      const htmlCs = window.getComputedStyle(html);
      const bodyCs = window.getComputedStyle(body);

      if (overflowRegex.test(htmlCs.overflowX) || overflowRegex.test(htmlCs.overflowY)) {
        if (debug) console.warn('[useStickyFix] <html> has overflow — fixing');
        forceStyle(html, 'overflow-x', 'clip');
        forceStyle(html, 'overflow-y', 'visible');
        forceStyle(html, 'overflow', 'visible');
      }
      if (overflowRegex.test(bodyCs.overflowX) || overflowRegex.test(bodyCs.overflowY)) {
        if (debug) console.warn('[useStickyFix] <body> has overflow — fixing');
        forceStyle(body, 'overflow-x', 'clip');
        forceStyle(body, 'overflow-y', 'visible');
        forceStyle(body, 'overflow', 'visible');
      }
    };

    fixAncestors();

    // cleanup: restore تمام styleهای تغییر کرده
    return () => {
      for (const { el, prop, original, originalPriority } of fixedNodes) {
        if (original) {
          el.style.setProperty(prop, original, originalPriority || '');
        } else {
          el.style.removeProperty(prop);
        }
      }
    };
  }, [targetRef, debug]);
};

export default useStickyFix;
