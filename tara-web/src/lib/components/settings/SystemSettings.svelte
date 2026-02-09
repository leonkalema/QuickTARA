<script lang="ts">
	import { onMount } from 'svelte';
	import { Save, Database, Shield, Globe, Bell } from '@lucide/svelte';
	import { notifications } from '$lib/stores/notifications';
	import ThreatCatalogManager from './ThreatCatalogManager.svelte';

	let settings = {
		database: {
			backup_frequency: 'daily',
			retention_days: 30,
			auto_cleanup: true
		},
		security: {
			session_timeout: 480,
			password_policy: 'strong',
			two_factor_required: false,
			login_attempts: 5
		},
		system: {
			timezone: 'UTC',
			date_format: 'YYYY-MM-DD',
			language: 'en',
			theme: 'auto'
		},
		notifications: {
			email_enabled: true,
			risk_alerts: true,
			system_updates: true,
			weekly_reports: false
		}
	};

	let loading = false;
	let hasChanges = false;

	onMount(() => {
		loadSettings();
	});

	async function loadSettings() {
		loading = true;
		try {
			// Mock loading - replace with actual API call
			await new Promise(resolve => setTimeout(resolve, 500));
		} catch (error) {
			notifications.show('Failed to load system settings', 'error');
		} finally {
			loading = false;
		}
	}

	async function saveSettings() {
		loading = true;
		try {
			// Mock save - replace with actual API call
			await new Promise(resolve => setTimeout(resolve, 1000));
			notifications.show('System settings saved successfully', 'success');
			hasChanges = false;
		} catch (error) {
			notifications.show('Failed to save system settings', 'error');
		} finally {
			loading = false;
		}
	}

	function markChanged() {
		hasChanges = true;
	}
</script>

<div class="system-settings">
	<div class="header">
		<h2>System Configuration</h2>
		<button 
			class="btn-primary" 
			on:click={saveSettings} 
			disabled={!hasChanges || loading}
		>
			<Save class="w-4 h-4" />
			{loading ? 'Saving...' : 'Save Changes'}
		</button>
	</div>

	<div class="settings-sections">
		<!-- Database Settings -->
		<div class="settings-section">
			<div class="section-header">
				<Database class="w-4 h-4" style="color: var(--color-accent-primary);" />
				<h3>Database & Backup</h3>
			</div>

			<div class="settings-grid">
				<div class="setting-item">
					<label for="backup_frequency">Backup Frequency</label>
					<select 
						id="backup_frequency" 
						bind:value={settings.database.backup_frequency}
						on:change={markChanged}
					>
						<option value="hourly">Hourly</option>
						<option value="daily">Daily</option>
						<option value="weekly">Weekly</option>
					</select>
				</div>

				<div class="setting-item">
					<label for="retention_days">Retention Period (days)</label>
					<input 
						id="retention_days"
						type="number" 
						min="1" 
						max="365"
						bind:value={settings.database.retention_days}
						on:input={markChanged}
					/>
				</div>

				<div class="setting-item checkbox-item">
					<input 
						id="auto_cleanup"
						type="checkbox" 
						bind:checked={settings.database.auto_cleanup}
						on:change={markChanged}
					/>
					<label for="auto_cleanup">Enable automatic cleanup</label>
				</div>
			</div>
		</div>

		<!-- Security Settings -->
		<div class="settings-section">
			<div class="section-header">
				<Shield class="w-4 h-4" style="color: var(--color-status-accepted-text, #10b981);" />
				<h3>Security & Authentication</h3>
			</div>

			<div class="settings-grid">
				<div class="setting-item">
					<label for="session_timeout">Session Timeout (minutes)</label>
					<input 
						id="session_timeout"
						type="number" 
						min="15" 
						max="1440"
						bind:value={settings.security.session_timeout}
						on:input={markChanged}
					/>
				</div>

				<div class="setting-item">
					<label for="password_policy">Password Policy</label>
					<select 
						id="password_policy" 
						bind:value={settings.security.password_policy}
						on:change={markChanged}
					>
						<option value="basic">Basic (8+ characters)</option>
						<option value="strong">Strong (12+ chars, mixed case, numbers)</option>
						<option value="complex">Complex (16+ chars, symbols required)</option>
					</select>
				</div>

				<div class="setting-item">
					<label for="login_attempts">Max Login Attempts</label>
					<input 
						id="login_attempts"
						type="number" 
						min="3" 
						max="10"
						bind:value={settings.security.login_attempts}
						on:input={markChanged}
					/>
				</div>

				<div class="setting-item checkbox-item">
					<input 
						id="two_factor_required"
						type="checkbox" 
						bind:checked={settings.security.two_factor_required}
						on:change={markChanged}
					/>
					<label for="two_factor_required">Require two-factor authentication</label>
				</div>
			</div>
		</div>

		<!-- System Settings -->
		<div class="settings-section">
			<div class="section-header">
				<Globe class="w-4 h-4" style="color: var(--color-accent-primary);" />
				<h3>System Preferences</h3>
			</div>

			<div class="settings-grid">
				<div class="setting-item">
					<label for="timezone">Default Timezone</label>
					<select 
						id="timezone" 
						bind:value={settings.system.timezone}
						on:change={markChanged}
					>
						<option value="UTC">UTC</option>
						<option value="America/New_York">Eastern Time</option>
						<option value="America/Chicago">Central Time</option>
						<option value="America/Denver">Mountain Time</option>
						<option value="America/Los_Angeles">Pacific Time</option>
						<option value="Europe/London">London</option>
						<option value="Europe/Paris">Paris</option>
					</select>
				</div>

				<div class="setting-item">
					<label for="date_format">Date Format</label>
					<select 
						id="date_format" 
						bind:value={settings.system.date_format}
						on:change={markChanged}
					>
						<option value="YYYY-MM-DD">YYYY-MM-DD</option>
						<option value="MM/DD/YYYY">MM/DD/YYYY</option>
						<option value="DD/MM/YYYY">DD/MM/YYYY</option>
					</select>
				</div>

				<div class="setting-item">
					<label for="language">Default Language</label>
					<select 
						id="language" 
						bind:value={settings.system.language}
						on:change={markChanged}
					>
						<option value="en">English</option>
						<option value="es">Spanish</option>
						<option value="fr">French</option>
						<option value="de">German</option>
					</select>
				</div>

				<div class="setting-item">
					<label for="theme">Default Theme</label>
					<select 
						id="theme" 
						bind:value={settings.system.theme}
						on:change={markChanged}
					>
						<option value="auto">Auto (System)</option>
						<option value="light">Light</option>
						<option value="dark">Dark</option>
					</select>
				</div>
			</div>
		</div>

		<!-- Notification Settings -->
		<div class="settings-section">
			<div class="section-header">
				<Bell class="w-4 h-4" style="color: var(--color-status-draft-text, #f59e0b);" />
				<h3>Notifications</h3>
			</div>

			<div class="settings-grid">
				<div class="setting-item checkbox-item">
					<input 
						id="email_enabled"
						type="checkbox" 
						bind:checked={settings.notifications.email_enabled}
						on:change={markChanged}
					/>
					<label for="email_enabled">Enable email notifications</label>
				</div>

				<div class="setting-item checkbox-item">
					<input 
						id="risk_alerts"
						type="checkbox" 
						bind:checked={settings.notifications.risk_alerts}
						on:change={markChanged}
					/>
					<label for="risk_alerts">High risk alerts</label>
				</div>

				<div class="setting-item checkbox-item">
					<input 
						id="system_updates"
						type="checkbox" 
						bind:checked={settings.notifications.system_updates}
						on:change={markChanged}
					/>
					<label for="system_updates">System update notifications</label>
				</div>

				<div class="setting-item checkbox-item">
					<input 
						id="weekly_reports"
						type="checkbox" 
						bind:checked={settings.notifications.weekly_reports}
						on:change={markChanged}
					/>
					<label for="weekly_reports">Weekly summary reports</label>
				</div>
			</div>
		</div>

		<!-- Threat Catalog -->
		<ThreatCatalogManager />
	</div>
</div>

<style>
	.system-settings {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.header {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.header h2 {
		margin: 0;
		font-size: 0.8125rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.settings-sections {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.settings-section {
		background: var(--color-bg-surface);
		border: 1px solid var(--color-border-default);
		border-radius: 8px;
		padding: 1.5rem;
	}

	.section-header {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}

	.section-header h3 {
		margin: 0;
		font-size: 0.75rem;
		font-weight: 600;
		color: var(--color-text-primary);
	}

	.settings-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1rem;
	}

	.setting-item {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.checkbox-item {
		flex-direction: row;
		align-items: center;
		gap: 0.75rem;
	}

	.checkbox-item input[type="checkbox"] {
		width: auto;
		margin: 0;
	}

	label {
		font-weight: 500;
		color: var(--color-text-secondary);
		font-size: 0.6875rem;
	}

	.checkbox-item label {
		margin: 0;
	}

	input, select {
		padding: 0.625rem 0.75rem;
		border: 1px solid var(--color-border-default);
		border-radius: 6px;
		font-size: 0.75rem;
		background: var(--color-bg-inset);
		color: var(--color-text-primary);
	}

	input:focus, select:focus {
		outline: none;
		border-color: var(--color-accent-primary);
		box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-accent-primary) 20%, transparent);
	}

	input[type="checkbox"] {
		width: 1rem;
		height: 1rem;
		padding: 0;
	}

	.btn-primary {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		background: var(--color-accent-primary);
		color: var(--color-text-inverse);
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-weight: 500;
		font-size: 0.75rem;
		transition: all 0.2s;
	}

	.btn-primary:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.btn-primary:not(:disabled):hover {
		filter: brightness(1.1);
	}
</style>
