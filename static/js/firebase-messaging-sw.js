importScripts('https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.10.1/firebase-messaging.js');

// ✅ Only initialize Firebase if it's not already initialized
if (!firebase.apps.length) {
    firebase.initializeApp({
        apiKey: "{{ FIREBASE_CONFIG_apiKey }}",
        authDomain: "{{ FIREBASE_CONFIG_authDomain }}",
        projectId: "{{ FIREBASE_CONFIG_projectId }}",
        storageBucket: "{{ FIREBASE_CONFIG_storageBucket }}",
        messagingSenderId: "{{ FIREBASE_CONFIG_messagingSenderId }}",
        appId: "{{ FIREBASE_CONFIG_appId }}",
        measurementId: "{{ FIREBASE_CONFIG_measurementId }}"
    });
}

// Initialize Messaging
const messaging = firebase.messaging();

// Background Message Handler
messaging.onBackgroundMessage((payload) => {
    console.log("📩 Received background message: ", payload);

    const { title, body, url } = payload.data;

    self.registration.showNotification(title, {
        body: body,
        icon: "/static/icons/notification-icon.png",
        data: { url }
    });
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();

    const urlToOpen = event.notification.data.url;

    const clickResponsePromise = clients.matchAll({
        type: "window",
        includeUncontrolled: true
    }).then(windowClients => {
        for (let client of windowClients) {
            if (client.url === urlToOpen && 'focus' in client) {
                return client.focus();
            }
        }
        if (clients.openWindow) {
            return clients.openWindow(urlToOpen);
        }
    });

    event.waitUntil(clickResponsePromise);
});