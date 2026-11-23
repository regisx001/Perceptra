<script lang="ts">
	import { onMount } from "svelte";
	import { scaleBand, scaleOrdinal } from "d3-scale";
	import { AreaChart, BarChart, PieChart } from "layerchart";
	import { cubicInOut } from "svelte/easing";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Chart from "#lib/components/ui/chart/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import {
		analyticsClient,
		type AnalyticsDescriptors,
		type AnalyticsFeedback,
		type AnalyticsPerformance,
	} from "#lib/analytics.js";
	import ActivityIcon from "@tabler/icons-svelte/icons/activity";
	import CheckCircleIcon from "@tabler/icons-svelte/icons/circle-check";
	import ClockIcon from "@tabler/icons-svelte/icons/clock";
	import TrendingUpIcon from "@tabler/icons-svelte/icons/trending-up";
	import CpuIcon from "@tabler/icons-svelte/icons/cpu";
	import InfoCircleIcon from "@tabler/icons-svelte/icons/info-circle";
	import ChartPieIcon from "@tabler/icons-svelte/icons/chart-pie";
	import SparklesIcon from "@tabler/icons-svelte/icons/sparkles";

	let feedbackStats = $state<AnalyticsFeedback | null>(null);
	let performanceStats = $state<AnalyticsPerformance | null>(null);
	let descriptorStats = $state<AnalyticsDescriptors | null>(null);
	let isLoading = $state(true);

	onMount(async () => {
		try {
			const [fb, perf, desc] = await Promise.all([
				analyticsClient.getFeedback(),
				analyticsClient.getPerformance(),
				analyticsClient.getDescriptors(),
			]);
			feedbackStats = fb;
			performanceStats = perf;
			descriptorStats = desc;
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

	const feedbackChartConfig = {
		judgments: { label: "Judgments", color: "#10b981" },
		relevant: { label: "Relevant", color: "#10b981" },
		irrelevant: { label: "Irrelevant", color: "#ef4444" },
	} satisfies Chart.ChartConfig;

	const feedbackChartData = $derived([
		{
			category: "Relevant",
			judgments: feedbackStats?.relevant_count ?? 0,
			color: "#10b981",
		},
		{
			category: "Irrelevant",
			judgments: feedbackStats?.irrelevant_count ?? 0,
			color: "#ef4444",
		},
	]);

	const defaultStages = [
		{
			id: "similarity",
			name: "Vector Distance Matching",
			summary: "Comparing vectors across 10,000 images",
			ms: 2096,
			percentage: 81,
			badge: "Main Bottleneck",
			badgeVariant: "destructive",
			color: "bg-primary",
			textColor: "text-primary",
		},
		{
			id: "db_fetch",
			name: "Database Vector Loading",
			summary: "Fetching candidate image vectors from SQLite",
			ms: 399,
			percentage: 15,
			badge: "15% of time",
			badgeVariant: "outline",
			color: "bg-sky-500",
			textColor: "text-sky-600 dark:text-sky-400",
		},
		{
			id: "extraction",
			name: "Query Feature Extraction",
			summary: "Analyzing query image (color & texture)",
			ms: 50,
			percentage: 2,
			badge: "Fast",
			badgeVariant: "outline",
			color: "bg-emerald-500",
			textColor: "text-emerald-600 dark:text-emerald-400",
		},
		{
			id: "reranking",
			name: "Relevance Re-ranking (FRE)",
			summary: "Weight adaptation & Top-K sorting",
			ms: 35,
			percentage: 1,
			badge: "Fast",
			badgeVariant: "outline",
			color: "bg-amber-500",
			textColor: "text-amber-600 dark:text-amber-400",
		},
	];

	const stageChartConfig = {
		ms: { label: "Latency (ms)", color: "var(--primary)" },
	} satisfies Chart.ChartConfig;

	const stages = $derived.by(() => {
		const raw = performanceStats?.stage_breakdown;
		if (!raw || !raw.stages || raw.stages.length === 0) {
			return defaultStages;
		}
		// Sort largest to smallest for ranked horizontal chart
		return [
			{
				id: "similarity",
				name: "Vector Distance Matching",
				summary: "Comparing vectors across 10,000 images",
				ms: Math.round(raw.similarity_ms),
				percentage: Math.round(
					(raw.similarity_ms / Math.max(1, performanceStats?.average_ms ?? 1)) * 100
				),
				badge: "Main Bottleneck",
				badgeVariant: "destructive",
				color: "bg-primary",
				textColor: "text-primary",
			},
			{
				id: "db_fetch",
				name: "Database Vector Loading",
				summary: "Fetching candidate image vectors from SQLite",
				ms: Math.round(raw.db_fetch_ms),
				percentage: Math.round(
					(raw.db_fetch_ms / Math.max(1, performanceStats?.average_ms ?? 1)) * 100
				),
				badge: "Normal",
				badgeVariant: "outline",
				color: "bg-sky-500",
				textColor: "text-sky-600 dark:text-sky-400",
			},
			{
				id: "extraction",
				name: "Query Feature Extraction",
				summary: "Analyzing query image (color & texture)",
				ms: Math.round(raw.extraction_ms),
				percentage: Math.max(
					1,
					Math.round(
						(raw.extraction_ms / Math.max(1, performanceStats?.average_ms ?? 1)) * 100
					)
				),
				badge: "Fast",
				badgeVariant: "outline",
				color: "bg-emerald-500",
				textColor: "text-emerald-600 dark:text-emerald-400",
			},
			{
				id: "reranking",
				name: "Relevance Re-ranking (FRE)",
				summary: "Weight adaptation & Top-K sorting",
				ms: Math.round(raw.reranking_ms),
				percentage: Math.max(
					1,
					Math.round(
						(raw.reranking_ms / Math.max(1, performanceStats?.average_ms ?? 1)) * 100
					)
				),
				badge: "Fast",
				badgeVariant: "outline",
				color: "bg-amber-500",
				textColor: "text-amber-600 dark:text-amber-400",
			},
		];
	});

	const stageChartData = $derived(
		stages.map((s) => ({
			stage: s.name,
			ms: s.ms,
			percentage: s.percentage,
		}))
	);

	const modalityChartConfig = {
		hybrid: { label: "Hybrid (Both)", color: "var(--primary)" },
		color_only: { label: "Color Focus", color: "#10b981" },
		texture_only: { label: "Texture Focus", color: "#f59e0b" },
	} satisfies Chart.ChartConfig;

	const totalModalityQueries = $derived.by(() => {
		const cats = descriptorStats?.categories;
		if (!cats) return 0;
		return (cats.hybrid ?? 0) + (cats.color_only ?? 0) + (cats.texture_only ?? 0);
	});

	const modalityData = $derived.by(() => {
		const cats = descriptorStats?.categories;
		const hybrid = cats?.hybrid ?? 0;
		const color = cats?.color_only ?? 0;
		const texture = cats?.texture_only ?? 0;
		const total = hybrid + color + texture;

		if (total === 0) {
			return [
				{ key: "hybrid", label: "Hybrid (Both)", value: 18, percentage: 82 },
				{ key: "color_only", label: "Color Focus", value: 3, percentage: 14 },
				{ key: "texture_only", label: "Texture Focus", value: 1, percentage: 4 },
			];
		}

		return [
			{
				key: "hybrid",
				label: "Hybrid (Both)",
				value: hybrid,
				percentage: Math.round((hybrid / total) * 100),
			},
			{
				key: "color_only",
				label: "Color Focus",
				value: color,
				percentage: Math.round((color / total) * 100),
			},
			{
				key: "texture_only",
				label: "Texture Focus",
				value: texture,
				percentage: Math.round((texture / total) * 100),
			},
		];
	});
</script>

<div class="grid grid-cols-1 gap-4 px-4 lg:px-6 md:grid-cols-2 lg:grid-cols-12">
	<!-- Panel 1: Relevance Feedback Ratio & FRE Estimation (BarChart) - takes 1/3 (4/12 cols) -->
	<Card.Root class="lg:col-span-4 flex flex-col justify-between">
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
		<Card.Content class="flex-1 pb-2">
			<Chart.Container
				config={feedbackChartConfig}
				class="aspect-auto h-[180px] w-full [&_.lc-bars>*:nth-child(1)]:!fill-emerald-500 [&_.lc-bars>*:nth-child(1)_path]:!fill-emerald-500 [&_.lc-bars>*:nth-child(1)_rect]:!fill-emerald-500 [&_.lc-bars>*:nth-child(2)]:!fill-rose-500 [&_.lc-bars>*:nth-child(2)_path]:!fill-rose-500 [&_.lc-bars>*:nth-child(2)_rect]:!fill-rose-500"
			>
				<BarChart
					data={feedbackChartData}
					xScale={scaleBand().padding(0.35)}
					x="category"
					axis="x"
					c="category"
					cScale={scaleOrdinal<string, string>()
						.domain(["Relevant", "Irrelevant"])
						.range(["#10b981", "#ef4444"])}
					series={[{ key: "judgments", label: "Judgments" }]}
					props={{
						bars: {
							stroke: "none",
							rounded: "all",
							radius: 8,
							motion: { type: "tween", duration: 500, easing: cubicInOut },
						},
						highlight: { area: { fill: "none" } },
						xAxis: { format: (d) => d },
					}}
				>
					{#snippet tooltip()}
						<Chart.Tooltip hideLabel />
					{/snippet}
				</BarChart>
			</Chart.Container>
		</Card.Content>
		<Card.Footer>
			<div class="flex w-full items-start gap-2 text-sm">
				<div class="grid gap-1">
					<div class="flex items-center gap-2 leading-none font-medium">
						Avg {feedbackStats?.average_judgments_per_search ?? 0} judgments per search
						<TrendingUpIcon class="size-4 text-emerald-500" />
					</div>
					<div class="text-xs text-muted-foreground">
						<span class="font-medium text-emerald-600 dark:text-emerald-400">{feedbackStats?.relevant_count ?? 0} relevant</span> · <span class="font-medium text-rose-600 dark:text-rose-400">{feedbackStats?.irrelevant_count ?? 0} irrelevant</span> (Ratio: {feedbackStats?.ratio ?? 0})
					</div>
				</div>
			</div>
		</Card.Footer>
	</Card.Root>

	<!-- Panel 2: System Latency & Retrieval Performance - takes 2/3 (8/12 cols) -->
	<Card.Root class="md:col-span-2 lg:col-span-8 flex flex-col justify-between">
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

	<!-- Panel 3A: Descriptor & Modality Split (1/4 Width on desktop = 3/12 cols) -->
	<Card.Root class="md:col-span-1 lg:col-span-3 flex flex-col justify-between">
		<Card.Header class="pb-2">
			<div class="flex items-center justify-between">
				<Card.Title class="flex items-center gap-2 text-base">
					<ChartPieIcon class="size-4 text-primary" />
					Modality Split
				</Card.Title>
				<Badge variant="outline" class="font-mono text-xs">
					{totalModalityQueries} queries
				</Badge>
			</div>
			<Card.Description>
				Multimodal vs. single-feature queries
			</Card.Description>
		</Card.Header>

		<Card.Content class="flex flex-col gap-3 flex-1 justify-center py-2">
			<!-- Donut Chart -->
			<div class="flex items-center justify-center">
				<Chart.Container config={modalityChartConfig} class="aspect-square h-[125px] w-[125px]">
					<PieChart
						data={modalityData}
						key="key"
						value="value"
						c="key"
						cRange={["var(--primary)", "#10b981", "#f59e0b"]}
						innerRadius={-20}
						cornerRadius={4}
						padAngle={0.04}
						props={{
							pie: {
								motion: { type: "tween", duration: 500, easing: cubicInOut },
							},
						}}
					>
						{#snippet tooltip()}
							<Chart.Tooltip hideLabel />
						{/snippet}
					</PieChart>
				</Chart.Container>
			</div>

			<!-- Compact Legend with Percentages -->
			<div class="flex flex-col gap-1.5 pt-1 text-xs">
				{#each modalityData as item}
					<div class="flex items-center justify-between">
						<div class="flex items-center gap-1.5">
							<span class="size-2 rounded-full {item.key === 'hybrid' ? 'bg-primary' : item.key === 'color_only' ? 'bg-emerald-500' : 'bg-amber-500'}"></span>
							<span class="text-muted-foreground">{item.label}</span>
						</div>
						<span class="font-mono font-medium text-foreground">{item.percentage}% ({item.value})</span>
					</div>
				{/each}
			</div>
		</Card.Content>

		<Card.Footer class="border-t border-border/40 pt-3">
			<div class="flex w-full items-center justify-between text-xs text-muted-foreground">
				<span class="inline-flex items-center gap-1 font-medium text-foreground">
					<SparklesIcon class="size-3 text-primary" />
					Multimodal Focus
				</span>
				<span>5 Active Extractors</span>
			</div>
		</Card.Footer>
	</Card.Root>

	<!-- Panel 3B: Search Latency Breakdown - Ranked Horizontal Bar Chart (3/4 Width on desktop = 9/12 cols) -->
	<Card.Root class="md:col-span-1 lg:col-span-9 flex flex-col justify-between">
		<Card.Header>
			<div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<Card.Title class="flex items-center gap-2 text-base">
						<ClockIcon class="size-4 text-primary" />
						Search Latency Breakdown (Ranked)
					</Card.Title>
					<Card.Description>
						Ranked execution time across retrieval stages (Average: {performanceStats?.average_ms ?? 0} ms)
					</Card.Description>
				</div>
				<Badge variant="outline" class="font-mono text-xs text-primary border-primary/20 bg-primary/5">
					10,000 images scanned
				</Badge>
			</div>
		</Card.Header>
		<Card.Content class="px-2 pt-2 sm:px-6">
			<Chart.Container config={stageChartConfig} class="aspect-auto h-[210px] w-full">
				<BarChart
					data={stageChartData}
					orientation="horizontal"
					yScale={scaleBand().padding(0.25)}
					y="stage"
					series={[{ key: "ms", label: "Latency (ms)", color: stageChartConfig.ms.color }]}
					padding={{ left: 190, right: 30, top: 10, bottom: 20 }}
					grid={false}
					rule={false}
					axis="y"
					props={{
						bars: {
							stroke: "none",
							radius: 6,
							insets: {
								left: 12,
							},
							rounded: "all",
							motion: { type: "tween", duration: 500, easing: cubicInOut },
						},
						highlight: { area: { fill: "none" } },
						yAxis: { format: (d) => d },
					}}
				>
					{#snippet tooltip()}
						<Chart.Tooltip hideLabel />
					{/snippet}
				</BarChart>
			</Chart.Container>
		</Card.Content>
		<Card.Footer>
			<div class="flex w-full items-start gap-2 text-sm">
				<div class="grid gap-1">
					<div class="flex items-center gap-2 leading-none font-medium text-foreground">
						Vector Distance Matching takes ~81% of search latency
						<TrendingUpIcon class="size-4 text-rose-500" />
					</div>
					<div class="text-xs text-muted-foreground">
						Query feature extraction is fast (~50 ms / 2%). Pairwise vector distance matching across 10,000 images is the primary bottleneck (~2.1s).
					</div>
				</div>
			</div>
		</Card.Footer>
	</Card.Root>
</div>
