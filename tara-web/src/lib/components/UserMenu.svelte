<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import { authStore, type User } from '$lib/stores/auth';
	import { authApi } from '$lib/api/auth';

	const dispatch = createEventDispatcher<{
		logout: void;
	}>();

	export let user: User;
	
	let showDropdown = false;
	let isLoggingOut = false;

	function toggleDropdown() {
		showDropdown = !showDropdown;
	}

	function closeDropdown() {
		showDropdown = false;
	}

	async function handleLogout() {
		isLoggingOut = true;
		
		try {
			// Get current auth state
			const currentAuth = authStore;
			let refreshToken = '';
			
			const unsubscribe = currentAuth.subscribe(auth => {
				refreshToken = auth.refreshToken || '';
			});
			unsubscribe();

			// Call logout API if we have a refresh token (don't await - fire and forget)
			if (refreshToken) {
				authApi.logout(refreshToken).catch(() => {});
			}
		} catch (error) {
			// Ignore API errors
		}

		// Clear auth store immediately
		authStore.logout();
		
		// Close dropdown and reset state
		isLoggingOut = false;
		closeDropdown();
		
		// Dispatch logout event and redirect
		dispatch('logout');
	}

	// Close dropdown when clicking outside
	function handleClickOutside(event: MouseEvent) {
		const target = event.target as Element;
		if (!target.closest('.user-menu')) {
			closeDropdown();
		}
	}
</script>

<svelte:window on:click={handleClickOutside} />

<div class="user-menu">
	<button class="user-button" on:click={toggleDropdown} disabled={isLoggingOut}>
		<div class="user-avatar">
			{user.first_name.charAt(0)}{user.last_name.charAt(0)}
		</div>
		<div class="user-info">
			<span class="user-name">{user.first_name} {user.last_name}</span>
			<span class="user-email">{user.email}</span>
		</div>
		<svg class="dropdown-arrow" class:rotated={showDropdown} viewBox="0 0 20 20" fill="currentColor">
			<path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
		</svg>
	</button>

	{#if showDropdown}
		<div class="dropdown-menu">
			<div class="dropdown-header">
				<div class="user-details">
					<p class="user-full-name">{user.first_name} {user.last_name}</p>
					<p class="user-username">@{user.username}</p>
					<div class="user-status">
						<span class="status-badge" class:active={user.status === 'ACTIVE'} class:pending={user.status === 'PENDING'}>
							{user.status}
						</span>
						{#if user.is_verified}
							<span class="verified-badge">✓ Verified</span>
						{/if}
					</div>
				</div>
			</div>
			
			<div class="dropdown-divider"></div>
			
			<div class="dropdown-actions">
				<button class="dropdown-item" on:click={closeDropdown}>
					<svg class="item-icon" viewBox="0 0 20 20" fill="currentColor">
						<path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-6-3a2 2 0 11-4 0 2 2 0 014 0zm-2 4a5 5 0 00-4.546 2.916A5.986 5.986 0 0010 16a5.986 5.986 0 004.546-2.084A5 5 0 0010 11z" clip-rule="evenodd" />
					</svg>
					Profile Settings
				</button>
				
				<button class="dropdown-item logout-item" on:click={handleLogout} disabled={isLoggingOut}>
					{#if isLoggingOut}
						<span class="logout-spinner"></span>
						Signing out...
					{:else}
						<svg class="item-icon" viewBox="0 0 20 20" fill="currentColor">
							<path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd" />
						</svg>
						Sign Out
					{/if}
				</button>
			</div>
		</div>
	{/if}
</div>

<style>
	.user-menu {
		position: relative;
		display: inline-block;
	}

	.user-button {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.5rem;
		background: white;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
		min-width: 200px;
	}

	.user-button:hover {
		background: #f9fafb;
		border-color: #d1d5db;
	}

	.user-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.user-avatar {
		width: 2.5rem;
		height: 2.5rem;
		background: #3b82f6;
		color: white;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 600;
		font-size: 0.875rem;
		text-transform: uppercase;
	}

	.user-info {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		min-width: 0;
	}

	.user-name {
		font-weight: 500;
		color: #1f2937;
		font-size: 0.875rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		width: 100%;
	}

	.user-email {
		color: #6b7280;
		font-size: 0.75rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		width: 100%;
	}

	.dropdown-arrow {
		width: 1.25rem;
		height: 1.25rem;
		color: #6b7280;
		transition: transform 0.2s;
		flex-shrink: 0;
	}

	.dropdown-arrow.rotated {
		transform: rotate(180deg);
	}

	.dropdown-menu {
		position: absolute;
		top: 100%;
		right: 0;
		margin-top: 0.5rem;
		background: white;
		border: 1px solid #e5e7eb;
		border-radius: 8px;
		box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
		min-width: 280px;
		z-index: 50;
		animation: dropdownSlide 0.2s ease-out;
	}

	@keyframes dropdownSlide {
		from {
			opacity: 0;
			transform: translateY(-10px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.dropdown-header {
		padding: 1rem;
	}

	.user-details {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.user-full-name {
		margin: 0;
		font-weight: 600;
		color: #1f2937;
		font-size: 1rem;
	}

	.user-username {
		margin: 0;
		color: #6b7280;
		font-size: 0.875rem;
	}

	.user-status {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.5rem;
	}

	.status-badge {
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
		font-size: 0.75rem;
		font-weight: 500;
		text-transform: uppercase;
	}

	.status-badge.active {
		background: #d1fae5;
		color: #065f46;
	}

	.status-badge.pending {
		background: #fef3c7;
		color: #92400e;
	}

	.verified-badge {
		color: #059669;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.dropdown-divider {
		height: 1px;
		background: #e5e7eb;
		margin: 0;
	}

	.dropdown-actions {
		padding: 0.5rem;
	}

	.dropdown-item {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.75rem;
		background: none;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.875rem;
		color: #374151;
		transition: background-color 0.2s;
		text-align: left;
	}

	.dropdown-item:hover {
		background: #f3f4f6;
	}

	.dropdown-item:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.logout-item {
		color: #dc2626;
	}

	.logout-item:hover {
		background: #fef2f2;
	}

	.item-icon {
		width: 1.25rem;
		height: 1.25rem;
		flex-shrink: 0;
	}

	.logout-spinner {
		width: 1.25rem;
		height: 1.25rem;
		border: 2px solid transparent;
		border-top: 2px solid currentColor;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		flex-shrink: 0;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
