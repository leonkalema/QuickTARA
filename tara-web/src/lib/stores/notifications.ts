import { writable } from 'svelte/store';

export interface Notification {
	id: string;
	message: string;
	type: 'success' | 'error' | 'warning' | 'info';
	duration?: number;
}

function createNotificationStore() {
	const { subscribe, update } = writable<Notification[]>([]);

	return {
		subscribe,
		show: (message: string, type: Notification['type'] = 'info', duration = 5000) => {
			const id = Math.random().toString(36).substr(2, 9);
			const notification: Notification = { id, message, type, duration };

			update(notifications => [...notifications, notification]);

			// Auto-remove after duration
			if (duration > 0) {
				setTimeout(() => {
					update(notifications => notifications.filter(n => n.id !== id));
				}, duration);
			}

			return id;
		},
		remove: (id: string) => {
			update(notifications => notifications.filter(n => n.id !== id));
		},
		clear: () => {
			update(() => []);
		}
	};
}

export const notifications = createNotificationStore();
