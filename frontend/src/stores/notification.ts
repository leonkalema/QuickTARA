import { writable } from 'svelte/store';

type NotificationType = 'success' | 'error' | 'info' | 'warning';

interface Notification {
  id: string;
  message: string;
  type: NotificationType;
  timeout: number;
}

export const notifications = writable<Notification[]>([]);

export function showNotification(
  message: string, 
  type: NotificationType = 'info', 
  timeout: number = 5000
) {
  const id = Math.random().toString(36).substring(2, 9);
  
  notifications.update(n => [
    ...n,
    { id, message, type, timeout }
  ]);
  
  if (timeout > 0) {
    setTimeout(() => {
      dismissNotification(id);
    }, timeout);
  }
  
  return id;
}

export function dismissNotification(id: string) {
  notifications.update(n => n.filter(notification => notification.id !== id));
}
