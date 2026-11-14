<script lang="ts">
	import { progress } from "#lib/progress.svelte.js";
	import { navigating } from "$app/state";
	import { untrack } from "svelte";

	// Only pages that load significant datasets / descriptors should be eligible for the navigation progress bar
	const HEAVY_DATA_ROUTES = [
		"/dashboard/images",
		"/dashboard/categories",
		"/dashboard",
		"/search",
	];

	// Threshold (in ms) before showing the bar, so fast/cached transitions don't flash
	const SLOW_LOAD_THRESHOLD_MS = 250;

	let delayTimer: ReturnType<typeof setTimeout> | null = null;
	let isProgressActive = false;

	function isHeavyDataRoute(pathname: string): boolean {
		return HEAVY_DATA_ROUTES.some(
			(route) => pathname === route || pathname.startsWith(route + "/")
		);
	}

	$effect(() => {
		const to = navigating.to;
		const from = navigating.from;

		// Check if this is an actual route change to a data-heavy page
		const isHeavyNavigation = Boolean(
			to &&
			to.url.pathname !== from?.url.pathname &&
			isHeavyDataRoute(to.url.pathname)
		);

		untrack(() => {
			if (isHeavyNavigation) {
				// Only show progress bar if loading is relatively slow (exceeds threshold)
				if (!delayTimer && !isProgressActive) {
					delayTimer = setTimeout(() => {
						isProgressActive = true;
						progress.start();
						delayTimer = null;
					}, SLOW_LOAD_THRESHOLD_MS);
				}
			} else {
				// Cancel pending timer if navigation resolved quickly before threshold
				if (delayTimer) {
					clearTimeout(delayTimer);
					delayTimer = null;
				}
				// If the progress bar was actually started, finish it cleanly
				if (isProgressActive) {
					progress.done();
					isProgressActive = false;
				}
			}
		});

		return () => {
			if (delayTimer) {
				clearTimeout(delayTimer);
				delayTimer = null;
			}
		};
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
