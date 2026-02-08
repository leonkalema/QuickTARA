import { writable } from 'svelte/store';

export interface ProductEventsStore {
  readonly changedAt: number;
}

const initialState: ProductEventsStore = {
  changedAt: 0
};

const productEventsStore = writable<ProductEventsStore>(initialState);

export const notifyProductsChanged = (): void => {
  productEventsStore.set({ changedAt: Date.now() });
};

export const productEvents = {
  subscribe: productEventsStore.subscribe
};
