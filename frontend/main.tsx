import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Development-only: demo preview without real authentication
async function init() {
  try {
    const env = (typeof import.meta !== 'undefined' && (import.meta as any).env) || {};
    // Allow enabling demo with localStorage or URL param ?demo=true
    const urlParams = typeof window !== 'undefined' ? new URLSearchParams(window.location.search) : null;
    if (urlParams && urlParams.get('demo') === 'true') {
      try { localStorage.setItem('demo', 'true'); } catch (e) { /* ignore */ }
    }
    const demoFlag = typeof window !== 'undefined' ? localStorage.getItem('demo') : null;

    if (demoFlag === 'true') {
      // Put a fake token and user in localStorage so the app thinks we're logged in
      // This is strictly for local development and demo purposes only.
      const fakeToken = 'demo-token';
      localStorage.setItem('token', fakeToken);
      const fakeUser = {
        id: '00000000-0000-0000-0000-000000000000',
        studentId: 'demo-001',
        name: 'Demo Student',
        email: 'demo@student.local',
        gpa: 3.5,
        semester: 2,
      };
      localStorage.setItem('user', JSON.stringify(fakeUser));

      // Import and install mocks BEFORE rendering so components don't race and trigger network requests
      try {
        const mod = await import('./mocks/devMock');
        mod.installDevMocks();
      } catch (e) {
        // ignore if import fails in some environments
      }
    }
  } catch (e) {
    // ignore in environments where localStorage isn't available
  }

  ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

// Start the app
init();