package org.kivy.evitaai;

import android.accessibilityservice.AccessibilityService;
import android.view.accessibility.AccessibilityEvent;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.provider.Settings;
import android.net.Uri;
import android.app.AppOpsManager;
import android.content.pm.ApplicationInfo;

public class MyAccessibilityService extends AccessibilityService {

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {
        if (event.getEventType() == AccessibilityEvent.TYPE_VIEW_CLICKED) {
            CharSequence content = event.getText().toString();

            if (content != null && content.toString().contains("http")) {
                // Verifica se as notificações estão habilitadas
                if (!areNotificationsEnabled()) {
                    openNotificationSettings();
                } else {
                    showNotification("Link detectado: " + content.toString());
                }
            }
        }
    }

    @Override
    public void onInterrupt() {
        // Nada a fazer
    }

    private void showNotification(String message) {
        NotificationManager notificationManager =
                (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

        String channelId = "evitaai_channel";
        String channelName = "EvitaAI Notificações";

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    channelId, channelName, NotificationManager.IMPORTANCE_HIGH);
            notificationManager.createNotificationChannel(channel);
        }

        Notification.Builder builder = new Notification.Builder(this)
                .setContentTitle("EvitaAI - Link detectado")
                .setContentText(message)
                .setSmallIcon(android.R.drawable.ic_dialog_info);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder.setChannelId(channelId);
        }

        notificationManager.notify(1, builder.build());
    }

    private boolean areNotificationsEnabled() {
        NotificationManager notificationManager =
                (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            return notificationManager.areNotificationsEnabled();
        }

        // Para versões mais antigas, assume que está ativado
        return true;
    }

    private void openNotificationSettings() {
        Intent intent = new Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS);
        intent.putExtra(Settings.EXTRA_APP_PACKAGE, getPackageName());
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
    }
}