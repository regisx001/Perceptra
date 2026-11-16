<script lang="ts">
	import { useHeaderPortal } from "#lib/header-portal.svelte.js";
	import type { Snippet } from "svelte";

	let {
		children,
		breadcrumb
	}: {
		children?: Snippet;
		breadcrumb?: Snippet;
	} = $props();

	const portal = useHeaderPortal();

	$effect(() => {
		if (portal) {
			portal.content = children ?? null;
			portal.breadcrumb = breadcrumb ?? null;
		}
		return () => {
			if (portal) {
				portal.content = null;
				portal.breadcrumb = null;
			}
		};
	});
</script>
