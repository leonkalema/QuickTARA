import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

export interface ActiveOrganization {
	organization_id: string;
	name: string;
	description: string;
	role: string;
}

export interface ActiveOrgState {
	organization: ActiveOrganization | null;
	isLoading: boolean;
}

const initialState: ActiveOrgState = {
	organization: null,
	isLoading: false
};

function createActiveOrgStore() {
	const { subscribe, set, update } = writable<ActiveOrgState>(initialState);

	return {
		subscribe,

		// Set loading state
		setLoading: (loading: boolean) => {
			update(state => ({ ...state, isLoading: loading }));
		},

		// Set active organization
		setActive: (organization: ActiveOrganization) => {
			const newState: ActiveOrgState = {
				organization,
				isLoading: false
			};
			
			set(newState);
			
			// Store in localStorage if in browser
			if (browser) {
				localStorage.setItem('active_organization', JSON.stringify(organization));
			}
		},

		// Clear active organization
		clear: () => {
			set(initialState);
			
			// Clear localStorage if in browser
			if (browser) {
				localStorage.removeItem('active_organization');
			}
		},

		// Initialize from localStorage
		init: () => {
			if (!browser) return;
			
			const orgStr = localStorage.getItem('active_organization');
			
			if (orgStr) {
				try {
					const organization = JSON.parse(orgStr);
					set({
						organization,
						isLoading: false
					});
				} catch (error) {
					console.error('Error parsing stored organization data:', error);
					localStorage.removeItem('active_organization');
				}
			}
		},

		// Get current active organization
		getCurrent: (): ActiveOrganization | null => {
			const state = get(activeOrgStore);
			return state.organization;
		},

		// Check if organization is active
		isActive: (organizationId: string): boolean => {
			const state = get(activeOrgStore);
			return state.organization?.organization_id === organizationId;
		}
	};
}

export const activeOrgStore = createActiveOrgStore();

// Initialize store when module loads
if (browser) {
	setTimeout(() => {
		activeOrgStore.init();
	}, 100);
}
