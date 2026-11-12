<script lang="ts">
	import type { DashboardTableFeatures } from "./data-table-features.js";
	import type { Schema } from "./schemas.js";
	import type { Row } from "@tanstack/svelte-table";
	import { Badge } from "#lib/components/ui/badge/index.js";

	let { row }: { row: Row<DashboardTableFeatures, Schema> } = $props();
</script>

<div class="flex items-center gap-1.5 text-xs text-muted-foreground font-mono">
	<span>{row.original.descriptorType}</span>
</div>
