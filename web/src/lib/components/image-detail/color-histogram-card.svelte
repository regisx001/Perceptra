<script lang="ts">
	import { scaleLinear } from "d3-scale";
	import { curveMonotoneX } from "d3-shape";
	import { LineChart } from "layerchart";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Chart from "#lib/components/ui/chart/index.js";
	import * as m from "#lib/paraglide/messages.js";
	import type { ColorHistogramFeature } from "#lib/images.js";

	let { data }: { data?: ColorHistogramFeature } = $props();

	const chartConfig = {
		hue: { label: "Hue", color: "#3b82f6" },
		saturation: { label: "Saturation", color: "#ef4444" },
		value: { label: "Value", color: "#10b981" },
	} satisfies Chart.ChartConfig;

	// Interactive channel visibility states
	let showHue = $state(true);
	let showSaturation = $state(true);
	let showValue = $state(true);

	let isAllActive = $derived(showHue && showSaturation && showValue);

	function showAll() {
		showHue = true;
		showSaturation = true;
		showValue = true;
	}

	function isolateChannel(key: "hue" | "saturation" | "value") {
		showHue = key === "hue";
		showSaturation = key === "saturation";
		showValue = key === "value";
	}

	function toggleChannel(key: "hue" | "saturation" | "value") {
		if (key === "hue") showHue = !showHue;
		if (key === "saturation") showSaturation = !showSaturation;
		if (key === "value") showValue = !showValue;

		// Prevent disabling all 3: if all are false, restore the clicked one
		if (!showHue && !showSaturation && !showValue) {
			if (key === "hue") showHue = true;
			if (key === "saturation") showSaturation = true;
			if (key === "value") showValue = true;
		}
	}

	let activeSeries = $derived.by(() => {
		const list = [];
		if (showHue) {
			list.push({
				key: "hue",
				label: "Hue",
				color: chartConfig.hue.color,
			});
		}
		if (showSaturation) {
			list.push({
				key: "saturation",
				label: "Saturation",
				color: chartConfig.saturation.color,
			});
		}
		if (showValue) {
			list.push({
				key: "value",
				label: "Value",
				color: chartConfig.value.color,
			});
		}
		return list;
	});

	// Extract full-resolution channel curves (256 bins each), with backward-compatible interpolation for legacy datasets
	let chartData = $derived.by(() => {
		const h = data?.channels?.h || [];
		const s = data?.channels?.s || [];
		const v = data?.channels?.v || [];
		if (h.length === 0 && s.length === 0 && v.length === 0) return [];

		const N = Math.max(h.length, s.length, v.length);
		if (N === 0) return [];

		// Direct 1:1 mapping when channels have equal resolution (e.g. 256 points)
		if (h.length === N && s.length === N && v.length === N) {
			return Array.from({ length: N }, (_, i) => ({
				bin: i + 1,
				hue: +(h[i] * 100).toFixed(3),
				saturation: +(s[i] * 100).toFixed(3),
				value: +(v[i] * 100).toFixed(3),
			}));
		}

		// Backward-compatibility: interpolate across N if legacy bins have varying channel lengths (e.g. 16/8/8)
		return Array.from({ length: N }, (_, t) => {
			const hVal = h[t] !== undefined ? +(h[t] * 100).toFixed(3) : 0;

			const sPos = s.length > 1 ? t * ((s.length - 1) / (N - 1)) : 0;
			const sIdx = Math.floor(sPos);
			const sFrac = sPos - sIdx;
			const s0 = s[sIdx] || 0;
			const s1 = s[Math.min(sIdx + 1, s.length - 1)] || s0;
			const sVal = +((s0 * (1 - sFrac) + s1 * sFrac) * 100).toFixed(3);

			const vPos = v.length > 1 ? t * ((v.length - 1) / (N - 1)) : 0;
			const vIdx = Math.floor(vPos);
			const vFrac = vPos - vIdx;
			const v0 = v[vIdx] || 0;
			const v1 = v[Math.min(vIdx + 1, v.length - 1)] || v0;
			const vVal = +((v0 * (1 - vFrac) + v1 * vFrac) * 100).toFixed(3);

			return {
				bin: t + 1,
				hue: hVal,
				saturation: sVal,
				value: vVal,
			};
		});
	});

	let peakHue = $derived.by(() => {
		const h = data?.channels?.h || [];
		return h.length > 0 ? (Math.max(...h) * 100).toFixed(2) : "0.00";
	});

	let peakSaturation = $derived.by(() => {
		const s = data?.channels?.s || [];
		return s.length > 0 ? (Math.max(...s) * 100).toFixed(2) : "0.00";
	});

	let peakValue = $derived.by(() => {
		const v = data?.channels?.v || [];
		return v.length > 0 ? (Math.max(...v) * 100).toFixed(2) : "0.00";
	});
</script>

<Card.Root class="border border-border/80 shadow-xs">
	<Card.Header class="pb-3">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
			<div>
				<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
					{m.image_detail_color_hist_title()} ({chartData.length || 256} Bins)
				</Card.Title>
				<Card.Description class="text-xs text-muted-foreground">
					{m.image_detail_color_hist_desc()}
				</Card.Description>
			</div>

			<!-- Interactive Channel Selection & Legend Controls -->
			<div class="flex items-center gap-1.5 flex-wrap">
				<!-- Show All Button -->
				<button
					type="button"
					class="px-2.5 py-1 rounded-md text-xs font-mono font-medium transition-all {isAllActive
						? 'bg-foreground text-background font-semibold shadow-xs'
						: 'bg-muted/60 text-muted-foreground hover:text-foreground'}"
					onclick={showAll}
					title="Show all 3 channels"
				>
					All (3)
				</button>

				<!-- Hue Chip: click label to toggle, click 'only' to isolate -->
				<div class="inline-flex items-center rounded-md border {showHue ? 'border-border bg-background shadow-xs' : 'border-transparent bg-muted/20'} text-xs font-mono overflow-hidden transition-all">
					<button
						type="button"
						class="inline-flex items-center gap-1.5 px-2.5 py-1 transition-all {showHue ? 'text-foreground font-medium' : 'text-muted-foreground/40 hover:text-muted-foreground'}"
						onclick={() => toggleChannel('hue')}
						title="Toggle Hue on/off"
					>
						<span class="size-2 rounded-full {showHue ? '' : 'opacity-30'}" style="background-color: {chartConfig.hue.color};"></span>
						<span class="{showHue ? '' : 'line-through'}">Hue</span>
					</button>
					<button
						type="button"
						class="px-1.5 py-1 text-[10px] text-muted-foreground/60 hover:text-foreground hover:bg-muted/50 border-l border-border/40 transition-colors"
						onclick={() => isolateChannel('hue')}
						title="Show only Hue (disable others)"
					>
						only
					</button>
				</div>

				<!-- Saturation Chip -->
				<div class="inline-flex items-center rounded-md border {showSaturation ? 'border-border bg-background shadow-xs' : 'border-transparent bg-muted/20'} text-xs font-mono overflow-hidden transition-all">
					<button
						type="button"
						class="inline-flex items-center gap-1.5 px-2.5 py-1 transition-all {showSaturation ? 'text-foreground font-medium' : 'text-muted-foreground/40 hover:text-muted-foreground'}"
						onclick={() => toggleChannel('saturation')}
						title="Toggle Saturation on/off"
					>
						<span class="size-2 rounded-full {showSaturation ? '' : 'opacity-30'}" style="background-color: {chartConfig.saturation.color};"></span>
						<span class="{showSaturation ? '' : 'line-through'}">Saturation</span>
					</button>
					<button
						type="button"
						class="px-1.5 py-1 text-[10px] text-muted-foreground/60 hover:text-foreground hover:bg-muted/50 border-l border-border/40 transition-colors"
						onclick={() => isolateChannel('saturation')}
						title="Show only Saturation (disable others)"
					>
						only
					</button>
				</div>

				<!-- Value Chip -->
				<div class="inline-flex items-center rounded-md border {showValue ? 'border-border bg-background shadow-xs' : 'border-transparent bg-muted/20'} text-xs font-mono overflow-hidden transition-all">
					<button
						type="button"
						class="inline-flex items-center gap-1.5 px-2.5 py-1 transition-all {showValue ? 'text-foreground font-medium' : 'text-muted-foreground/40 hover:text-muted-foreground'}"
						onclick={() => toggleChannel('value')}
						title="Toggle Value on/off"
					>
						<span class="size-2 rounded-full {showValue ? '' : 'opacity-30'}" style="background-color: {chartConfig.value.color};"></span>
						<span class="{showValue ? '' : 'line-through'}">Value</span>
					</button>
					<button
						type="button"
						class="px-1.5 py-1 text-[10px] text-muted-foreground/60 hover:text-foreground hover:bg-muted/50 border-l border-border/40 transition-colors"
						onclick={() => isolateChannel('value')}
						title="Show only Value (disable others)"
					>
						only
					</button>
				</div>
			</div>
		</div>
	</Card.Header>

	<Card.Content class="pt-1 pb-2">
		{#if !data || !data.channels || chartData.length === 0}
			<div class="text-xs text-muted-foreground py-6 text-center">
				No color histogram data available.
			</div>
		{:else}
			<Chart.Container config={chartConfig} class="h-44 sm:h-48 md:h-52 w-full aspect-auto">
				<LineChart
					data={chartData}
					x="bin"
					xScale={scaleLinear()}
					axis="x"
					series={activeSeries}
					props={{
						spline: { curve: curveMonotoneX, motion: "tween", strokeWidth: 2 },
						xAxis: {
							ticks: chartData.length > 64 ? [1, 32, 64, 96, 128, 160, 192, 224, 256] : undefined,
							format: (v: number) => `${Math.round(v)}`,
						},
						highlight: { points: { r: 3.5 } },
					}}
				>
					{#snippet tooltip()}
						<Chart.Tooltip labelFormatter={(v) => `Bin ${v} (of ${chartData.length})`} />
					{/snippet}
				</LineChart>
			</Chart.Container>
		{/if}
	</Card.Content>

	{#if chartData.length > 0}
		<Card.Footer class="border-t border-border/60 bg-muted/20 px-4 sm:px-6 py-2.5">
			<div class="flex w-full items-center justify-between text-xs text-muted-foreground font-mono flex-wrap gap-2">
				{#if showHue}
					<div>
						Peak Hue: <strong class="text-foreground font-semibold">{peakHue}%</strong>
					</div>
				{/if}
				{#if showSaturation}
					<div>
						Peak Saturation: <strong class="text-foreground font-semibold">{peakSaturation}%</strong>
					</div>
				{/if}
				{#if showValue}
					<div>
						Peak Value: <strong class="text-foreground font-semibold">{peakValue}%</strong>
					</div>
				{/if}
				<div class="hidden sm:block ml-auto">
					Resolution: <strong class="text-foreground font-semibold">{chartData.length} bins</strong> &bull; Vector: <strong class="text-foreground font-semibold">{data?.vector?.length ?? (chartData.length * 3)}-D</strong> (L1)
				</div>
			</div>
		</Card.Footer>
	{/if}
</Card.Root>
