<script lang="ts">
	import { scaleBand } from "d3-scale";
	import { BarChart, Highlight } from "layerchart";
	import { cubicInOut } from "svelte/easing";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Chart from "#lib/components/ui/chart/index.js";
	import * as m from "#lib/paraglide/messages.js";
	import type { LbpHistogramFeature } from "#lib/images.js";

	let { data }: { data?: LbpHistogramFeature } = $props();

	let bins = $derived(data?.bins || []);
	let labels = $derived(data?.labels || []);

	const chartConfig = {
		views: { label: "Patterns", color: "" },
		frequency: { label: "Frequency", color: "var(--chart-1)" },
		cumulative: { label: "Cumulative", color: "var(--chart-2)" },
	} satisfies Chart.ChartConfig;

	let activeChart = $state<"frequency" | "cumulative">("frequency");

	let maxBinVal = $derived.by(() => {
		if (bins.length === 0) return 0;
		return Math.max(...bins);
	});

	let dominantIndex = $derived.by(() => {
		if (bins.length === 0) return 0;
		return bins.indexOf(maxBinVal);
	});

	let peakPercentage = $derived((maxBinVal * 100).toFixed(2));

	let chartData = $derived.by(() => {
		if (bins.length === 0) return [];

		let runningSum = 0;
		return bins.map((val, i) => {
			const freqPct = +(val * 100).toFixed(3);
			runningSum += val;
			const cumPct = +(Math.min(runningSum, 1.0) * 100).toFixed(2);
			return {
				bin: i,
				label: labels[i] || `${i}`,
				frequency: freqPct,
				cumulative: cumPct,
			};
		});
	});

	const activeSeries = $derived([
		{
			key: activeChart,
			label: chartConfig[activeChart].label,
			color: chartConfig[activeChart].color,
		},
	]);
</script>

<Card.Root class="border border-border/80 shadow-xs">
	<Card.Header class="flex flex-col items-stretch space-y-0 border-b p-0 sm:flex-row">
		<div class="flex flex-1 flex-col justify-center gap-1 px-4 py-3 sm:px-6 sm:py-4">
			<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
				{m.image_detail_lbp_title()} ({bins.length || 256} Bins)
			</Card.Title>
			<Card.Description class="text-xs text-muted-foreground">
				{m.image_detail_lbp_desc()}
			</Card.Description>
		</div>

		<div class="flex">
			<button
				type="button"
				data-active={activeChart === "frequency"}
				class="relative z-30 flex flex-1 flex-col justify-center gap-1 border-t px-4 py-2.5 text-start even:border-s data-[active=true]:bg-muted/50 sm:border-s sm:border-t-0 sm:px-6 sm:py-3 transition-colors cursor-pointer"
				onclick={() => (activeChart = "frequency")}
			>
				<span class="text-xs text-muted-foreground font-medium">
					Peak Frequency
				</span>
				<span class="text-lg leading-none font-bold sm:text-2xl font-mono">
					{peakPercentage}%
				</span>
			</button>

			<button
				type="button"
				data-active={activeChart === "cumulative"}
				class="relative z-30 flex flex-1 flex-col justify-center gap-1 border-t px-4 py-2.5 text-start even:border-s data-[active=true]:bg-muted/50 sm:border-s sm:border-t-0 sm:px-6 sm:py-3 transition-colors cursor-pointer"
				onclick={() => (activeChart = "cumulative")}
			>
				<span class="text-xs text-muted-foreground font-medium">
					Dominant Pattern
				</span>
				<span class="text-lg leading-none font-bold sm:text-2xl font-mono">
					#{dominantIndex}
				</span>
			</button>
		</div>
	</Card.Header>

	<Card.Content class="px-2 sm:p-5 pt-4">
		{#if !data || bins.length === 0}
			<div class="text-xs text-muted-foreground py-8 text-center">
				No LBP histogram data available.
			</div>
		{:else}
			<Chart.Container config={chartConfig} class="aspect-auto h-[240px] sm:h-[260px] w-full">
				<BarChart
					data={chartData}
					x="bin"
					xScale={scaleBand().padding(0.08)}
					axis="x"
					series={activeSeries}
					props={{
						bars: {
							stroke: "none",
							rounded: "none",
							motion: { type: "tween", duration: 500, easing: cubicInOut },
						},
						highlight: { area: { fill: "none" } },
						xAxis: {
							ticks: [0, 32, 64, 96, 128, 160, 192, 224, 255].filter((b) => b < chartData.length),
							format: (d: number) => `#${d}`,
						},
					}}
				>
					{#snippet belowMarks()}
						<Highlight area={{ class: "fill-muted" }} />
					{/snippet}
					{#snippet tooltip()}
						<Chart.Tooltip
							labelFormatter={(v: number) => `LBP Pattern #${v}`}
						/>
					{/snippet}
				</BarChart>
			</Chart.Container>
		{/if}
	</Card.Content>

	{#if chartData.length > 0}
		<Card.Footer class="border-t border-border/60 bg-muted/20 px-4 sm:px-6 py-2.5">
			<div class="flex w-full items-center justify-between text-xs text-muted-foreground font-mono flex-wrap gap-2">
				<div>
					Dominant: <strong class="text-foreground font-semibold">Pattern #{dominantIndex}</strong> ({peakPercentage}%)
				</div>
				<div>
					Active Mode: <strong class="text-foreground font-semibold capitalize">{activeChart}</strong>
				</div>
				<div class="hidden sm:block ml-auto">
					Resolution: <strong class="text-foreground font-semibold">{bins.length} bins</strong> &bull; Vector: <strong class="text-foreground font-semibold">{data?.vector?.length ?? bins.length}-D</strong> (L1)
				</div>
			</div>
		</Card.Footer>
	{/if}
</Card.Root>
