<script lang="ts">
	import SectionCards from "#lib/components/section-cards.svelte";
	import ChartAreaInteractive from "#lib/components/chart-area-interactive.svelte";
	import RetrievalAnalyticsPanels from "#lib/components/retrieval-analytics-panels.svelte";
	import RetrievalHistoryTable from "#lib/components/retrieval-history-table.svelte";
	import DataTable from "#lib/components/data-table.svelte";
	import { cbirMockImages } from "#lib/components/cbir-mock-data.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import PhotoPlusIcon from "@tabler/icons-svelte/icons/photo-plus";
	import RefreshDotIcon from "@tabler/icons-svelte/icons/refresh-dot";
	import * as m from "#lib/paraglide/messages.js";
</script>

<svelte:head>
	<title>Perceptra - Retrieval Analytics &amp; History</title>
</svelte:head>

<div class="flex flex-1 flex-col">
	<div class="@container/main flex flex-1 flex-col gap-2">
		<!-- Top Welcome & Quick Actions Bar -->
		<div class="flex flex-col gap-2 px-4 pt-5 sm:flex-row sm:items-center sm:justify-between lg:px-6">
			<div>
				<h1 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">
					Retrieval Analytics &amp; Search History
				</h1>
				<p class="text-xs text-muted-foreground sm:text-sm">
					Real-time visual search telemetry, Feature Relevance Estimation (FRE Group 13) tracking, and history logs
				</p>
			</div>

			<div class="flex items-center gap-2 pt-2 sm:pt-0">
				<Button size="sm" href="/dashboard/query" class="h-8 gap-1.5 text-xs shadow-xs">
					<PhotoPlusIcon class="size-3.5" />
					<span>{m.nav_new_visual_query()}</span>
				</Button>
			</div>
		</div>

		<!-- Dashboard Core Analytics & Controls -->
		<div class="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
			<!-- Section 1: KPI Overview Cards (Real data from SQLite /api/v1/analytics/overview) -->
			<SectionCards />

			<!-- Section 2: Interactive Query Traffic & Search Activity Timeline -->
			<div class="px-4 lg:px-6">
				<ChartAreaInteractive />
			</div>

			<!-- Section 3: Deep Analytics (Feedback ratio, Descriptors, Latency) -->
			<RetrievalAnalyticsPanels />

			<!-- Section 4: Persistent Search History Table with Iteration Inspection -->
			<RetrievalHistoryTable />
		</div>
	</div>
</div>
