<script lang="ts">
	import CircleCheckFilledIcon from "@tabler/icons-svelte/icons/circle-check-filled";
	import LoaderIcon from "@tabler/icons-svelte/icons/loader";
	import SparklesIcon from "@tabler/icons-svelte/icons/sparkles";
	import ClockIcon from "@tabler/icons-svelte/icons/clock";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import type { DashboardTableFeatures } from "./data-table-features.js";
	import type { Schema } from "./schemas.js";
	import type { Row } from "@tanstack/svelte-table";

	let { row }: { row: Row<DashboardTableFeatures, Schema> } = $props();
</script>

<Badge variant="outline" class="px-2 py-0.5 text-xs font-normal gap-1.5">
	{#if row.original.status === "Indexed"}
		<CircleCheckFilledIcon class="size-3 text-emerald-500 fill-emerald-500 dark:fill-emerald-400" />
		<span class="text-emerald-700 dark:text-emerald-300">Indexed</span>
	{:else if row.original.status === "Optimized"}
		<SparklesIcon class="size-3 text-blue-500" />
		<span class="text-blue-700 dark:text-blue-300">Feedback Calibrated</span>
	{:else if row.original.status === "Processing"}
		<LoaderIcon class="size-3 animate-spin text-amber-500" />
		<span class="text-amber-700 dark:text-amber-300">Extracting Descriptors</span>
	{:else}
		<ClockIcon class="size-3 text-muted-foreground" />
		<span>Pending</span>
	{/if}
</Badge>
