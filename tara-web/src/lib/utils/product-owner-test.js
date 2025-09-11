// Quick test to verify PRODUCT_OWNER permissions
import { UserRole } from '../types/roles.js';

// Mock user store with PRODUCT_OWNER role
const mockUser = {
  roles: [UserRole.PRODUCT_OWNER],
  organizations: [{ role: UserRole.PRODUCT_OWNER }]
};

// Mock the user store
const userStore = {
  subscribe: (callback) => {
    callback(mockUser);
    return () => {};
  }
};

// Import and test permissions
import { canPerformTARA, isReadOnly, isProductOwner } from './permissions.js';

// Override the user store import
global.user = userStore;

console.log('Testing PRODUCT_OWNER permissions:');
console.log('canPerformTARA():', canPerformTARA());
console.log('isReadOnly():', isReadOnly());
console.log('isProductOwner():', isProductOwner());
console.log('canManageRisk (should be false):', canPerformTARA() && !isReadOnly());
