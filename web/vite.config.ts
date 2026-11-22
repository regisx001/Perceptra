import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';
import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';
import { paraglideVitePlugin } from '@inlang/paraglide-js';

const configDir = dirname(fileURLToPath(import.meta.url));
const rootDir = resolve(configDir, '..');

export default defineConfig(({ mode }) => {
	// Load environment variables for the active mode unified from project root
	const env = {
		...loadEnv(mode, rootDir, ''),
		...process.env
	};

	// 7000 for development, 5555 for production (overridable via VITE_PROXY_TARGET / VITE_API_PORT / DEV_PORT / PORT)
	const defaultPort = mode === 'production' ? '5555' : '7000';
	const targetPort = env.VITE_API_PORT || (mode === 'development' ? env.DEV_PORT : env.PORT) || env.PORT || defaultPort;
	const proxyTarget = env.VITE_PROXY_TARGET || env.PROXY_TARGET || `http://127.0.0.1:${targetPort}`;

	return {
		// Unify .env location to the project root directory
		envDir: rootDir,
		plugins: [
			tailwindcss(),
			paraglideVitePlugin({
				project: './project.inlang',
				outdir: './src/lib/paraglide'
			}),
			sveltekit({
				compilerOptions: {
					// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
					runes: ({ filename }) =>
						filename.split(/[/\\]/).includes('node_modules') ? undefined : true
				},

				// adapter-auto only supports some environments, see https://svelte.dev/docs/kit/adapter-auto for a list.
				// If your environment is not supported, or you settled on a specific environment, switch out the adapter.
				// See https://svelte.dev/docs/kit/adapters for more information about adapters.
				adapter: adapter({
					fallback: 'index.html',
					strict: false
				}),
				prerender: {
					handleMissingId: 'ignore',
					handleHttpError: 'ignore',
					handleUnseenRoutes: 'ignore'
				}
			})
		],
		server: {
			proxy: {
				'/api': {
					target: proxyTarget,
					changeOrigin: true
				},
				'/uploads': {
					target: proxyTarget,
					changeOrigin: true
				}
			}
		},
		preview: {
			proxy: {
				'/api': {
					target: proxyTarget,
					changeOrigin: true
				},
				'/uploads': {
					target: proxyTarget,
					changeOrigin: true
				}
			}
		}
	};
});
