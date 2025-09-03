import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface Product {
  scope_id: string;
  name: string;
  description?: string;
  product_type?: string;
  created_at?: string;
  updated_at?: string;
}

// Create the store with initial value from localStorage if available
function createProductStore() {
  const initialValue: Product | null = browser 
    ? JSON.parse(localStorage.getItem('selectedProduct') || 'null')
    : null;

  const { subscribe, set, update } = writable<Product | null>(initialValue);

  return {
    subscribe,
    set: (product: Product | null) => {
      set(product);
      if (browser) {
        if (product) {
          localStorage.setItem('selectedProduct', JSON.stringify(product));
        } else {
          localStorage.removeItem('selectedProduct');
        }
      }
    },
    clear: () => {
      set(null);
      if (browser) {
        localStorage.removeItem('selectedProduct');
      }
    }
  };
}

export const selectedProduct = createProductStore();
