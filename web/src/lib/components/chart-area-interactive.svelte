<script lang="ts">
	import { onMount } from "svelte";
	import { scaleUtc } from "d3-scale";
	import { Area, AreaChart } from "layerchart";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Chart from "#lib/components/ui/chart/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { analyticsClient, type AnalyticsActivity } from "#lib/analytics.js";

	let activityData = $state<AnalyticsActivity | null>(null);
	let isLoading = $state(true);

	onMount(async () => {
		try {
			activityData = await analyticsClient.getActivity();
		} catch (e) {
			console.error("Failed to load search activity:", e);
		} finally {
			isLoading = false;
		}
	});

	// Transform timeline for LayerChart
	const formattedTimeline = $derived.by(() => {
		if (!activityData?.activity_timeline || activityData.activity_timeline.length === 0) {
			// Fallback with a few points if fresh database
			const now = new Date();
			return [
				{ date: new Date(now.getTime() - 86400000 * 3), searches: 0, iterations: 0 },
				{ date: new Date(now.getTime() - 86400000 * 2), searches: 0, iterations: 0 },
				{ date: new Date(now.getTime() - 86400000), searches: 0, iterations: 0 },
				{ date: now, searches: 0, iterations: 0 },
			];
		}
		return activityData.activity_timeline.map((item) => ({
			date: new Date(item.date),
			searches: item.searches,
			iterations: item.iterations,
		}));
	});

	const chartConfig = {
		searches: { label: "Visual Searches", color: "var(--primary)" },
		iterations: { label: "Refinement Iterations (FRE)", color: "hsl(var(--muted-foreground))" },
	} satisfies Chart.ChartConfig;
</script>

<Card.Root class="@container/card">
	<Card.Header class="flex flex-col items-start gap-4 @[767px]/card:flex-row @[767px]/card:items-center">
		<div>
			<Card.Title>Visual Search &amp; Refinement Volume</Card.Title>
			<Card.Description>
				Real-time search frequency and Feature Relevance Estimation iterations over time
			</Card.Description>
		</div>
		<Card.Action>
			<div class="flex items-center gap-2">
				{#if activityData?.scope_distribution}
					{#each Object.entries(activityData.scope_distribution) as [scope, count]}
						<Badge variant="outline" class="text-xs capitalize">
							{scope}: {count}
						</Badge>
					{/each}
				{/if}
			</div>
		</Card.Action>
	</Card.Header>
	<Card.Content class="px-2 pt-4 sm:px-6 sm:pt-6">
		<Chart.Container config={chartConfig} class="aspect-auto h-[260px] w-full">
			<AreaChart
				legend
				data={formattedTimeline}
				x="date"
				xScale={scaleUtc()}
				series={[
					{
						key: "searches",
						label: "Initial Searches",
						color: chartConfig.searches.color,
					},
					{
						key: "iterations",
						label: "Total Iterations (FRE)",
						color: chartConfig.iterations.color,
					},
				]}
				seriesLayout="stack"
				props={{
					xAxis: {
						format: (v) => {
							return new Date(v).toLocaleDateString("en-US", {
								month: "short",
								day: "numeric",
							});
						},
					},
					yAxis: {
						format: (v) => `${v} q`,
					},
				}}
			>
				{#snippet tooltip()}
					<Chart.Tooltip
						labelFormatter={(v) => {
							return new Date(v).toLocaleDateString("en-US", {
								month: "short",
								day: "numeric",
								year: "numeric",
							});
						}}
					/>
				{/snippet}
			</AreaChart>
		</Chart.Container>
	</Card.Content>
</Card.Root>
