import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, searchForWorkspaceRoot } from 'vite';

export default defineConfig({
	server: {
		fs: {
			allow: [
				// search up for workspace root
				searchForWorkspaceRoot(process.cwd()),
				// your custom rules
				'/move-sound.mp3',
			],
		},
	},
	plugins: [sveltekit()],
	optimizeDeps: {
		include: ['chart.js', 'chart.js/auto', 'socket.io-client']
	},
	build: {
		rollupOptions: {
			output: {
				manualChunks: (id) => {
					if (id.includes('chart.js')) {
						return 'chart';
					}
					if (id.includes('socket.io-client')) {
						return 'socketio';
					}
				}
			}
		}
	},
	ssr: {
		noExternal: ['chart.js', 'socket.io-client']
	},
	resolve: {
		alias: {
			'chart.js/auto': 'chart.js/auto'
		}
	}
})