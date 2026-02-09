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
		gap: 0.5rem;
		padding: 0.375rem 0.5rem;
		background: transparent;
		border: 1px solid var(--color-border-default);
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.15s;
		min-width: 160px;
	}

	.user-button:hover {
		background: var(--color-bg-surface-hover);
		border-color: var(--color-border-default);
	}

	.user-button:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.user-avatar {
		width: 1.75rem;
		height: 1.75rem;
		background: var(--color-accent-primary);
		color: var(--color-text-inverse);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 600;
		font-size: 0.6875rem;
		text-transform: uppercase;
		flex-shrink: 0;
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
		color: var(--color-text-primary);
		font-size: 0.8125rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		width: 100%;
		line-height: 1.2;
	}

	.user-email {
		color: var(--color-text-tertiary);
		font-size: 0.6875rem;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		width: 100%;
		line-height: 1.2;
	}

	.dropdown-arrow {
		width: 1rem;
		height: 1rem;
		color: var(--color-text-tertiary);
		transition: transform 0.15s;
		flex-shrink: 0;
	}

	.dropdown-arrow.rotated {
		transform: rotate(180deg);
	}

	.dropdown-menu {
		position: absolute;
		top: 100%;
		right: 0;
		margin-top: 0.375rem;
		background: var(--color-bg-elevated);
		border: 1px solid var(--color-border-default);
		border-radius: 8px;
		box-shadow: var(--shadow-lg);
		min-width: 260px;
		z-index: 50;
		animation: dropdownSlide 0.15s ease-out;
	}

	@keyframes dropdownSlide {
		from { opacity: 0; transform: translateY(-6px); }
		to { opacity: 1; transform: translateY(0); }
	}

	.dropdown-header {
		padding: 0.75rem;
	}

	.user-details {
		display: flex;
		flex-direction: column;
		gap: 0.125rem;
	}

	.user-full-name {
		margin: 0;
		font-weight: 600;
		color: var(--color-text-primary);
		font-size: 0.875rem;
	}

	.user-username {
		margin: 0;
		color: var(--color-text-secondary);
		font-size: 0.8125rem;
	}

	.user-status {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.375rem;
	}

	.status-badge {
		padding: 0.125rem 0.375rem;
		border-radius: 4px;
		font-size: 0.6875rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.025em;
	}

	.status-badge.active {
		background: var(--color-success-bg);
		color: var(--color-success);
	}

	.status-badge.pending {
		background: var(--color-warning-bg);
		color: var(--color-warning);
	}

	.verified-badge {
		color: var(--color-success);
		font-size: 0.6875rem;
		font-weight: 500;
	}

	.dropdown-divider {
		height: 1px;
		background: var(--color-border-subtle);
		margin: 0;
	}

	.dropdown-actions {
		padding: 0.375rem;
	}

	.dropdown-item {
		width: 100%;
		display: flex;
		align-items: center;
		gap: 0.625rem;
		padding: 0.5rem 0.625rem;
		background: none;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.8125rem;
		color: var(--color-text-secondary);
		transition: all 0.15s;
		text-align: left;
	}

	.dropdown-item:hover {
		background: var(--color-bg-surface-hover);
		color: var(--color-text-primary);
	}

	.dropdown-item:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.logout-item {
		color: var(--color-error);
	}

	.logout-item:hover {
		background: var(--color-error-bg);
		color: var(--color-error);
	}

	.item-icon {
		width: 1.125rem;
		height: 1.125rem;
		flex-shrink: 0;
	}

	.logout-spinner {
		width: 1.125rem;
		height: 1.125rem;
		border: 2px solid transparent;
		border-top: 2px solid currentColor;
		border-radius: 50%;
		animation: spin 1s linear infinite;
		flex-shrink: 0;
	}

	@keyframes spin {
		to { transform: rotate(360deg); }
	}
</style>
