/* Local-only form behavior. No submitted data leaves this recreation. */
(() => {
  document.addEventListener('submit', event => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    if (!form.reportValidity()) return;
    const wrapper = form.closest('.w-form') || form.parentElement;
    let notice = wrapper.querySelector('[data-preview-notice]');
    if (!notice) {
      notice = document.createElement('div');
      notice.dataset.previewNotice = '';
      notice.className = 'preview-form-notice';
      notice.setAttribute('role', 'status');
      notice.setAttribute('tabindex', '-1');
      wrapper.appendChild(notice);
    }
    notice.textContent = 'Preview only — your message has not been sent.';
    notice.focus();
  }, true);
  // Keep page content available if a network-dependent animation fails to initialize.
  window.addEventListener('load', () => {
    if (!window.Webflow) document.documentElement.classList.add('replica-static-fallback');
  });
})();
