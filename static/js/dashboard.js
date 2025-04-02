import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.6.0/firebase-app.js';
import { getMessaging, getToken, onMessage } from 'https://www.gstatic.com/firebasejs/11.6.0/firebase-messaging.js';

// ✅ Load Firebase config from `window` (set in `dashboard.html`)
const firebaseConfig = window.FIREBASE_CONFIG;
const vapidKey = window.FIREBASE_PUBLIC_KEY;

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// ✅ Request Notification Permission
async function requestNotificationPermission() {
    console.log("🔔 Requesting notification permission...");
    const permission = await Notification.requestPermission();
    
    if (permission === "granted") {
        console.log("✅ Notification permission granted.");
        getFCMToken(); // Get FCM Token
    } else {
        console.log("❌ Notification permission denied.");
    }
}

async function getFCMToken() {
    try {
        const registration = await navigator.serviceWorker.ready;
        const token = await getToken(messaging, { 
            vapidKey: vapidKey, 
            serviceWorkerRegistration: registration // 🔥 Force Firebase to use our SW
        });

        if (token) {
            console.log("✅ FCM Token:", token);
            saveTokenToDatabase(token);
        } else {
            console.log("❌ No FCM token received.");
        }
    } catch (error) {
        console.log("❌ Error getting FCM token:", error);
    }
}

// ✅ Store Token in Database
async function saveTokenToDatabase(token) {
    try {
        const response = await fetch("/notifications/store_fcm_token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ fcm_token: token })
        });

        if (response.ok) {
            console.log("✅ Token saved to database.");
        } else {
            console.log("❌ Failed to save token.");
        }
    } catch (error) {
        console.log("❌ Error saving token:", error);
    }
}

// ✅ Listen for Foreground Messages
onMessage(messaging, (payload) => {
    console.log("📩 New notification:", payload);
    alert(`📩 ${payload.notification.title}: ${payload.notification.body}`);
});

// Call permission request on page load
requestNotificationPermission();
