<script lang="ts">
	import { progress } from "#lib/progress.svelte.js";
	import { navigating } from "$app/state";
	import { untrack } from "svelte";

	let isNavigating = $state(false);

	$effect(() => {
		const isNav = Boolean(navigating.to);
		if (isNav !== isNavigating) {
			isNavigating = isNav;
			untrack(() => {
				if (isNav) {
					progress.start();
				} else {
					progress.done();
				}
			});
		}
	});
</script>

{#if progress.visible}
	<aside
		aria-label="Loading progress"
		aria-live="polite"
		class="fixed inset-x-0 top-0 z-[9999] pointer-events-none h-1 w-full bg-transparent overflow-hidden"
	>
		<div
			class="h-full bg-linear-to-r from-primary/80 via-primary to-accent-foreground shadow-[0_0_12px_rgba(var(--primary),0.5)] transition-[width,opacity] duration-200 ease-out"
			style="width: {progress.current}%; opacity: {progress.visible ? 1 : 0};"
		></div>
	</aside>
{/if}
