import { writable } from 'svelte/store';

export interface Notification {
  id: string;
  message: string;
  type: 'success' | 'info' | 'warning' | 'error';
  duration?: number;
}

function createNotificationStore() {
  const { subscribe, set, update } = writable<Notification[]>([]);

  return {
    subscribe,
    show: (message: string, type: 'success' | 'info' | 'warning' | 'error' = 'success', duration: number = 3000) => {
      const id = Math.random().toString(36).substr(2, 9);
      const notification: Notification = { id, message, type, duration };
      
      update(notifications => [...notifications, notification]);
      
      // Auto-remove after duration
      setTimeout(() => {
        update(notifications => notifications.filter(n => n.id !== id));
      }, duration);
      
      return id;
    },
    remove: (id: string) => {
      update(notifications => notifications.filter(n => n.id !== id));
    },
    clear: () => set([])
  };
}

export const notifications = createNotificationStore();
