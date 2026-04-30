import { readFileSync } from 'node:fs';
import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

const sslCertfile: string | undefined = process.env.QUICKTARA_SSL_CERTFILE;
const sslKeyfile:  string | undefined = process.env.QUICKTARA_SSL_KEYFILE;

const httpsConfig: false | { cert: Buffer; key: Buffer } =
	sslCertfile && sslKeyfile
		? { cert: readFileSync(sslCertfile), key: readFileSync(sslKeyfile) }
		: false;

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	preview: {
		allowedHosts: true,
		https: httpsConfig
	},
	server: {
		https: httpsConfig
	},
	test: {
		globals: true,
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'client',
					environment: 'browser',
					browser: {
						enabled: true,
						provider: 'playwright',
						instances: [{ browser: 'chromium' }]
					},
					include: ['src/**/*.svelte.{test,spec}.{js,ts}', 'src/**/components/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/lib/server/**'],
					setupFiles: ['./vitest-setup-client.ts']
				}
			},
			{
				extends: './vite.config.ts',
				test: {
					name: 'server',
					environment: 'jsdom',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}', 'src/**/components/**/*.{test,spec}.{js,ts}'],
					setupFiles: ['./vitest-setup-server.ts']
				}
			}
		]
	}
});
