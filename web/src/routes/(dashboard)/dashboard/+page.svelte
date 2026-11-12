<script lang="ts">
	import SectionCards from "#lib/components/section-cards.svelte";
	import ChartAreaInteractive from "#lib/components/chart-area-interactive.svelte";
	import DataTable from "#lib/components/data-table.svelte";
	import { cbirMockImages } from "#lib/components/cbir-mock-data.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import PhotoPlusIcon from "@tabler/icons-svelte/icons/photo-plus";
	import RefreshDotIcon from "@tabler/icons-svelte/icons/refresh-dot";
	import SlidersIcon from "@tabler/icons-svelte/icons/adjustments";
</script>

<svelte:head>
	<title>Perceptra - Dashboard</title>
</svelte:head>

<div class="flex flex-1 flex-col">
	<div class="@container/main flex flex-1 flex-col gap-2">
		<!-- Top Welcome & Quick Actions Bar -->
		<div class="flex flex-col gap-2 px-4 pt-5 sm:flex-row sm:items-center sm:justify-between lg:px-6">
			<div>
				<h1 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
					Retrieval Intelligence & Index Overview
				</h1>
				<p class="text-xs text-muted-foreground sm:text-sm">
					Monitor descriptor indexing, query vector distributions, and relevance feedback convergence across GHIM-10K.
				</p>
			</div>

			<div class="flex items-center gap-2 pt-2 sm:pt-0">
				<Button variant="outline" size="sm" class="h-8 gap-1.5 text-xs">
					<RefreshDotIcon class="size-3.5" />
					<span>Sync Shards</span>
				</Button>
				<Button size="sm" href="/search" class="h-8 gap-1.5 text-xs shadow-xs">
					<PhotoPlusIcon class="size-3.5" />
					<span>New Visual Query</span>
				</Button>
			</div>
		</div>

		<!-- Dashboard Core Analytics & Controls -->
		<div class="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
			<!-- Section 1: KPI Cards -->
			<SectionCards />

			<!-- Section 2: Interactive Query Traffic & Descriptor Distribution Chart -->
			<div class="px-4 lg:px-6">
				<ChartAreaInteractive />
			</div>

			<!-- Section 3: GHIM-10K Image Gallery & Feature Descriptor Data Table -->
			<DataTable data={cbirMockImages} />
		</div>
	</div>
</div>
