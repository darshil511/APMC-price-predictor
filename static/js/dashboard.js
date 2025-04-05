import { messaging, onMessage, getToken } from './firebase-init.js';
const vapidKey = window.FIREBASE_PUBLIC_KEY;

// ✅ Request Notification Permission
async function requestNotificationPermission() {
    console.log("🔔 Requesting notification permission...");
    const permission = await Notification.requestPermission();
    
    if (permission === "granted") {
        console.log("✅ Notification permission granted.");
        // Fetch stored token from backend (or pass it via template context)
        fetch('/notifications/check_fcm_token')
        .then(response => response.json())
        .then(data => {
            if (!data.token) {
                console.log("No token found in DB. Fetching new FCM token...");
                getFCMToken(); // Call only if token doesn't exist
            } else {
                console.log("✅ FCM token already exists in DB. Skipping fetch.");
            }
        })
        .catch(err => {
            console.error("⚠️ Error checking token in DB:", err);
            // Fallback: try to get the token
            getFCMToken();
        });
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

if (window.IS_LOGGED_IN) {
    // Call permission request on page load
    requestNotificationPermission();
} else {
    console.log("🔒 User not logged in. Skipping notification permission.");
}

