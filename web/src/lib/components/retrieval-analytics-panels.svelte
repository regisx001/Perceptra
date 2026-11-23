<script lang="ts">
	import { onMount } from "svelte";
	import { AreaChart } from "layerchart";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Chart from "#lib/components/ui/chart/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Progress } from "#lib/components/ui/progress/index.js";
	import { analyticsClient, type AnalyticsFeedback, type AnalyticsPerformance } from "#lib/analytics.js";
	import ActivityIcon from "@tabler/icons-svelte/icons/activity";
	import CheckCircleIcon from "@tabler/icons-svelte/icons/circle-check";
	import ClockIcon from "@tabler/icons-svelte/icons/clock";

	let feedbackStats = $state<AnalyticsFeedback | null>(null);
	let performanceStats = $state<AnalyticsPerformance | null>(null);
	let isLoading = $state(true);

	onMount(async () => {
		try {
			const [fb, perf] = await Promise.all([
				analyticsClient.getFeedback(),
				analyticsClient.getPerformance(),
			]);
			feedbackStats = fb;
			performanceStats = perf;
		} catch (e) {
			console.error("Failed to load deep analytics:", e);
		} finally {
			isLoading = false;
		}
	});

	// Normalize feature weights for visualization
	const featureWeightEntries = $derived.by(() => {
		if (!feedbackStats?.feature_weight_evolution) return [];
		return Object.entries(feedbackStats.feature_weight_evolution);
	});

	// Sequential Latency Trendline data across recent iterations
	const latencyTrendData = $derived.by(() => {
		const raw = performanceStats?.recent_latencies;
		if (!raw || raw.length === 0) {
			return [
				{ index: 1, step: "#1", label: "Iter #1", latency: 0, candidates: 0 },
				{ index: 2, step: "#2", label: "Iter #2", latency: 0, candidates: 0 },
				{ index: 3, step: "#3", label: "Iter #3", latency: 0, candidates: 0 },
				{ index: 4, step: "#4", label: "Iter #4", latency: 0, candidates: 0 },
			];
		}
		// Sort chronologically (oldest to newest) for sequential progression
		return [...raw]
			.reverse()
			.map((item, idx) => ({
				index: idx + 1,
				step: `#${idx + 1}`,
				label: `Iter #${item.iteration_number}`,
				latency: Math.round(item.execution_time_ms ?? 0),
				candidates: item.candidates ?? 0,
			}));
	});

	const chartConfig = {
		latency: { label: "Latency (ms)", color: "var(--primary)" },
	} satisfies Chart.ChartConfig;
</script>

<div class="grid grid-cols-1 gap-4 px-4 lg:px-6 md:grid-cols-2 lg:grid-cols-3">
	<!-- Panel 1: Relevance Feedback Ratio & FRE Estimation -->
	<Card.Root>
		<Card.Header>
			<div class="flex items-center justify-between">
				<Card.Title class="flex items-center gap-2 text-base">
					<CheckCircleIcon class="size-4 text-emerald-500" />
					Relevance Judgment Behavior
				</Card.Title>
				<Badge variant="outline" class="text-xs">
					Ratio: {feedbackStats?.ratio ?? 0}
				</Badge>
			</div>
			<Card.Description>
				Relevant vs. Irrelevant user judgments recorded
			</Card.Description>
		</Card.Header>
		<Card.Content class="flex flex-col gap-4">
			<div class="flex items-center justify-between text-sm">
				<div class="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-medium">
					<span>Relevant</span>
					<Badge variant="outline" class="border-emerald-500/20 bg-emerald-500/10">
						{feedbackStats?.relevant_count ?? 0}
					</Badge>
				</div>
				<div class="flex items-center gap-1.5 text-rose-600 dark:text-rose-400 font-medium">
					<span>Irrelevant</span>
					<Badge variant="outline" class="border-rose-500/20 bg-rose-500/10">
						{feedbackStats?.irrelevant_count ?? 0}
					</Badge>
				</div>
			</div>

			<Progress
				value={
					(feedbackStats?.relevant_count ?? 0) + (feedbackStats?.irrelevant_count ?? 0) > 0
						? Math.round(
								((feedbackStats?.relevant_count ?? 0) /
									((feedbackStats?.relevant_count ?? 0) + (feedbackStats?.irrelevant_count ?? 0))) *
									100,
						  )
						: 50
				}
				class="h-2.5"
			/>

			<div class="rounded-lg border border-border/40 bg-muted/20 p-2.5 text-xs text-muted-foreground flex flex-col gap-1">
				<div class="font-medium text-foreground">
					Avg Feedback per Search: {feedbackStats?.average_judgments_per_search ?? 0} judgments
				</div>
				<div>Higher ratios accelerate positive feature clustering in FRE Group 13.</div>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Panel 2: System Latency & Retrieval Performance (takes 2 columns) -->
	<Card.Root class="md:col-span-2 lg:col-span-2">
		<Card.Header>
			<div class="flex items-center justify-between">
				<Card.Title class="flex items-center gap-2 text-base">
					<ClockIcon class="size-4 text-blue-500" />
					Retrieval Latency
				</Card.Title>
				<Badge variant="outline" class="text-xs text-blue-600 dark:text-blue-400">
					Avg: {performanceStats?.average_ms ?? 0} ms
				</Badge>
			</div>
			<Card.Description>
				Candidate distance calculation &amp; FRE re-ranking execution
			</Card.Description>
		</Card.Header>
		<Card.Content class="flex flex-col gap-3">
			<div class="grid grid-cols-3 gap-2 text-center text-xs">
				<div class="rounded-lg border border-border/50 bg-muted/30 p-2">
					<div class="text-[11px] text-muted-foreground">Min Latency</div>
					<div class="text-base font-bold tabular-nums text-foreground">
						{performanceStats?.min_ms ?? 0} <span class="text-xs font-normal">ms</span>
					</div>
				</div>
				<div class="rounded-lg border border-border/50 bg-muted/30 p-2">
					<div class="text-[11px] text-muted-foreground">Average</div>
					<div class="text-base font-bold tabular-nums text-foreground">
						{performanceStats?.average_ms ?? 0} <span class="text-xs font-normal">ms</span>
					</div>
				</div>
				<div class="rounded-lg border border-border/50 bg-muted/30 p-2">
					<div class="text-[11px] text-muted-foreground">Max Latency</div>
					<div class="text-base font-bold tabular-nums text-foreground">
						{performanceStats?.max_ms ?? 0} <span class="text-xs font-normal">ms</span>
					</div>
				</div>
			</div>

			<!-- Sequential Latency Trendline (Area Chart with Average Latency Reference Line) -->
			<div class="flex flex-col gap-1.5 pt-1">
				<div class="flex items-center justify-between text-xs">
					<span class="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
						Sequential Latency Trendline
					</span>
					<div class="flex items-center gap-2 text-[10px] text-muted-foreground">
						<span class="inline-flex items-center gap-1">
							<span class="size-2 rounded-full bg-primary"></span> Latency
						</span>
						<span class="inline-flex items-center gap-1 font-mono text-amber-500">
							<span class="inline-block w-3 border-t-2 border-dashed border-amber-500"></span> Avg ({performanceStats?.average_ms ?? 0}ms)
						</span>
					</div>
				</div>

				<div class="rounded-lg border border-border/50 bg-muted/20 p-2">
					<Chart.Container config={chartConfig} class="aspect-auto h-[140px] w-full">
						<AreaChart
							data={latencyTrendData}
							x="step"
							y="latency"
							series={[
								{
									key: "latency",
									label: "Latency (ms)",
									color: chartConfig.latency.color,
								},
							]}
							grid={true}
							rule={{
								y: performanceStats?.average_ms ?? 0,
								class: "stroke-amber-500 stroke-dashed [stroke-dasharray:4_4] opacity-80 stroke-[1.5]",
							}}
							props={{
								xAxis: {
									format: (v) => `${v}`,
								},
								yAxis: {
									format: (v) => `${v}ms`,
								},
							}}
						>
							{#snippet tooltip()}
								<Chart.Tooltip
									labelFormatter={(v) => {
										const item = latencyTrendData.find((d) => d.step === v);
										return item ? `${item.label} (${item.candidates} candidates)` : `${v}`;
									}}
								/>
							{/snippet}
						</AreaChart>
					</Chart.Container>
				</div>
			</div>
		</Card.Content>
	</Card.Root>
</div>
