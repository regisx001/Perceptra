<script lang="ts">
	import type { DashboardTableFeatures } from "./data-table-features.js";
	import type { Schema } from "./schemas.js";
	import type { Row } from "@tanstack/svelte-table";

	let { row }: { row: Row<DashboardTableFeatures, Schema> } = $props();

	// Similarity score percentage format
	const scorePct = $derived((row.original.similarityScore * 100).toFixed(1));
</script>

<div class="flex items-center justify-end gap-1.5 font-mono text-xs">
	<span class="font-medium text-foreground">{scorePct}%</span>
</div>
