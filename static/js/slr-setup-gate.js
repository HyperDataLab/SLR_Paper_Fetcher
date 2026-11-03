(() => {
  const isSettingsPage = window.location.pathname === '/settings';

  async function verifySetup() {
    try {
      const response = await fetch('/api/slr/config', { cache: 'no-store' });
      const config = await response.json();
      if (response.ok && !config.has_api_key && !isSettingsPage) {
        window.location.replace('/settings?setup=required');
        return;
      }
    } catch (error) {
      console.warn('Could not verify SLR setup state.', error);
    }
    document.body?.setAttribute('data-slr-setup-checked', 'true');
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', verifySetup, { once: true });
  } else {
    verifySetup();
  }
})();
