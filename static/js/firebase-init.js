// static/js/firebase-init.js
import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.6.0/firebase-app.js';
import { getMessaging, getToken, deleteToken, onMessage } from 'https://www.gstatic.com/firebasejs/11.6.0/firebase-messaging.js';

const firebaseConfig = window.FIREBASE_CONFIG;
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

export { app, messaging, getToken, deleteToken, onMessage };