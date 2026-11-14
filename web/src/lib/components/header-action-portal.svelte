<script lang="ts">
	import { useHeaderPortal } from "#lib/header-portal.svelte.js";
	import type { Snippet } from "svelte";

	let { children }: { children?: Snippet } = $props();
	const portal = useHeaderPortal();

	$effect(() => {
		if (portal) {
			portal.content = children ?? null;
		}
		return () => {
			if (portal) {
				portal.content = null;
			}
		};
	});
</script>
