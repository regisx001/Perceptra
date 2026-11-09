<script lang="ts">
	import * as m from '#lib/paraglide/messages.js';
	import { useLocale } from '#lib/i18n.svelte.js';
	import { Button } from '#lib/components/ui/button/index.js';
	import LogInIcon from '@lucide/svelte/icons/log-in';
	import UserPlusIcon from '@lucide/svelte/icons/user-plus';
	import GlobeIcon from '@lucide/svelte/icons/globe';

	const locale = useLocale();
</script>

<main class="max-w-2xl mx-auto p-8 space-y-6">
	<header class="flex items-center justify-between">
		<div class="flex items-center gap-3">
			<img
				src="/logo-black.png"
				alt="Studio Logo"
				class="h-10 w-auto object-contain dark:hidden"
			/>
			<img
				src="/logo-beige.png"
				alt="Studio Logo"
				class="hidden h-10 w-auto object-contain dark:block"
			/>
			<h1 class="text-2xl sm:text-3xl font-bold tracking-tight">{m.app_title()}</h1>
		</div>
		<div class="flex items-center gap-2">
			<button
				type="button"
				onclick={() => locale.toggle()}
				class="inline-flex h-8 items-center gap-1.5 px-3 text-xs font-medium border rounded-md shadow-xs hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors"
			>
				<GlobeIcon class="size-3.5" />
				<span>{locale.current.toUpperCase()}</span>
			</button>
			<Button variant="outline" size="sm" href="/login" class="gap-1.5">
				<LogInIcon class="size-3.5" />
				<span>{m.auth_sign_in_link()}</span>
			</Button>
			<Button size="sm" href="/register" class="gap-1.5">
				<UserPlusIcon class="size-3.5" />
				<span>{m.auth_sign_up_link()}</span>
			</Button>
		</div>
	</header>

	<p class="text-neutral-600 dark:text-neutral-400">
		{m.description()}
	</p>

	<div class="p-4 rounded-lg bg-neutral-50 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 space-y-2">
		<h2 class="text-lg font-semibold">{m.welcome()}</h2>
		<p>{m.example_message({ username: 'Visitor' })}</p>
	</div>

	<div class="flex items-center gap-3">
		<Button>
			{m.search_button()}
		</Button>
	</div>
</main>
