<script lang="ts">
	import * as m from '#lib/paraglide/messages.js';
	import { getLocale, setLocale } from '#lib/paraglide/runtime.js';

	let currentLocale = $derived(getLocale());

	function toggleLocale() {
		const nextLocale = currentLocale === 'en' ? 'de' : 'en';
		setLocale(nextLocale);
	}
</script>

<main class="max-w-2xl mx-auto p-8 space-y-6">
	<header class="flex items-center justify-between">
		<h1 class="text-3xl font-bold tracking-tight">{m.app_title()}</h1>
		<button
			type="button"
			onclick={toggleLocale}
			class="px-3 py-1.5 text-sm font-medium border rounded-md shadow-sm hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
		>
			Locale: {currentLocale.toUpperCase()}
		</button>
	</header>

	<p class="text-neutral-600 dark:text-neutral-400">
		{m.description()}
	</p>

	<div class="p-4 rounded-lg bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 space-y-2">
		<h2 class="text-lg font-semibold">{m.welcome()}</h2>
		<p>{m.example_message({ username: 'Visitor' })}</p>
	</div>

	<div>
		<button
			type="button"
			class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
		>
			{m.search_button()}
		</button>
	</div>
</main>
