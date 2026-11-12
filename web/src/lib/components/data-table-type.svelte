<script lang="ts">
	import { Badge } from "#lib/components/ui/badge/index.js";
	import type { DashboardTableFeatures } from "./data-table-features.js";
	import type { Schema } from "./schemas.js";
	import type { Row } from "@tanstack/svelte-table";

	let { row }: { row: Row<DashboardTableFeatures, Schema> } = $props();
</script>

<div class="w-32">
	<Badge variant="outline" class="px-2 py-0.5 text-xs font-normal">
		{row.original.category}
	</Badge>
</div>
