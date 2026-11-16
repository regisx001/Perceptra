<script lang="ts">
	import * as Card from "#lib/components/ui/card/index.js";
	import BarChart3Icon from "@lucide/svelte/icons/bar-chart-3";
	import type { ColorHistogramFeature } from "#lib/images.js";

	let { data }: { data?: ColorHistogramFeature } = $props();

	type Channel = "h" | "s" | "v";
	let activeChannel = $state<Channel>("h");

	let currentBins = $derived.by(() => {
		if (!data?.channels) return [];
		return data.channels[activeChannel] || [];
	});

	let maxBinVal = $derived.by(() => {
		if (currentBins.length === 0) return 1.0;
		const max = Math.max(...currentBins);
		return max > 0 ? max : 1.0;
	});

	function getBarColor(channel: Channel, index: number, total: number): string {
		if (channel === "h") {
			// True hue angle in degrees: 0..360
			const hue = Math.round((index / total) * 360);
			return `hsl(${hue}, 85%, 55%)`;
		} else if (channel === "s") {
			// Saturation spectrum
			const pct = Math.round((index / total) * 100);
			return `hsl(210, ${pct}%, 55%)`;
		} else {
			// Value / brightness spectrum
			const light = Math.round(20 + (index / total) * 70);
			return `hsl(0, 0%, ${light}%)`;
		}
	}
</script>

<Card.Root class="border border-border/80 shadow-xs">
	<Card.Header class="pb-3">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
			<div class="flex items-center gap-2">
				<div class="p-1.5 rounded-md bg-primary/10 text-primary">
					<BarChart3Icon class="size-4" />
				</div>
				<div>
					<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
						HSV Color Histogram
					</Card.Title>
					<Card.Description class="text-xs text-muted-foreground">
						32-D concatenated L1-normalized frequency distribution
					</Card.Description>
				</div>
			</div>

			<!-- Channel Toggle Pills -->
			<div class="flex items-center p-0.5 rounded-lg border border-border bg-muted/40 w-fit">
				<button
					type="button"
					class="px-2.5 py-1 text-2xs font-medium rounded-md transition-all cursor-pointer {activeChannel === 'h'
						? 'bg-card text-foreground font-semibold shadow-2xs border border-border/60'
						: 'text-muted-foreground hover:text-foreground'}"
					onclick={() => (activeChannel = "h")}
				>
					Hue (16)
				</button>
				<button
					type="button"
					class="px-2.5 py-1 text-2xs font-medium rounded-md transition-all cursor-pointer {activeChannel === 's'
						? 'bg-card text-foreground font-semibold shadow-2xs border border-border/60'
						: 'text-muted-foreground hover:text-foreground'}"
					onclick={() => (activeChannel = "s")}
				>
					Saturation (8)
				</button>
				<button
					type="button"
					class="px-2.5 py-1 text-2xs font-medium rounded-md transition-all cursor-pointer {activeChannel === 'v'
						? 'bg-card text-foreground font-semibold shadow-2xs border border-border/60'
						: 'text-muted-foreground hover:text-foreground'}"
					onclick={() => (activeChannel = "v")}
				>
					Value (8)
				</button>
			</div>
		</div>
	</Card.Header>

	<Card.Content class="space-y-3">
		{#if !data || !data.channels || currentBins.length === 0}
			<div class="text-xs text-muted-foreground py-6 text-center">
				No color histogram data available.
			</div>
		{:else}
			<!-- Pure SVG Histogram Bar Chart -->
			<div class="w-full bg-muted/20 border border-border/60 rounded-lg p-3">
				<svg
					viewBox="0 0 400 130"
					class="w-full h-32 overflow-visible select-none"
					preserveAspectRatio="none"
				>
					<!-- Grid lines -->
					<line x1="0" y1="100" x2="400" y2="100" stroke="currentColor" stroke-opacity="0.2" stroke-width="1" />
					<line x1="0" y1="50" x2="400" y2="50" stroke="currentColor" stroke-opacity="0.1" stroke-dasharray="2,2" stroke-width="1" />
					<line x1="0" y1="0" x2="400" y2="0" stroke="currentColor" stroke-opacity="0.1" stroke-dasharray="2,2" stroke-width="1" />

					<!-- Bars -->
					{#each currentBins as val, i}
						{@const barCount = currentBins.length}
						{@const slotW = 400 / barCount}
						{@const pad = slotW * 0.15}
						{@const barW = Math.max(2, slotW - pad * 2)}
						{@const barH = Math.max(2, (val / maxBinVal) * 98)}
						{@const barX = i * slotW + pad}
						{@const barY = 100 - barH}
						{@const fill = getBarColor(activeChannel, i, barCount)}

						<g class="transition-all duration-150 group">
							<rect
								x={barX}
								y={barY}
								width={barW}
								height={barH}
								rx="2"
								fill={fill}
								class="opacity-90 hover:opacity-100 cursor-pointer"
							>
								<title>Bin #{i + 1}: {(val * 100).toFixed(2)}% ({val.toFixed(4)})</title>
							</rect>
							<!-- Bin Label -->
							<text
								x={barX + barW / 2}
								y="118"
								text-anchor="middle"
								font-size="9"
								class="fill-muted-foreground font-mono select-none"
							>
								{i + 1}
							</text>
						</g>
					{/each}
				</svg>
			</div>

			<!-- Quick Channel Metrics -->
			<div class="flex items-center justify-between text-2xs text-muted-foreground px-1">
				<span>
					Peak: <strong class="text-foreground font-mono">{(maxBinVal * 100).toFixed(1)}%</strong>
				</span>
				<span>
					Bins: <strong class="text-foreground font-mono">{currentBins.length}</strong>
				</span>
				<span>
					Channel Sum: <strong class="text-foreground font-mono">{currentBins.reduce((a, b) => a + b, 0).toFixed(2)}</strong> (L1)
				</span>
			</div>
		{/if}
	</Card.Content>
</Card.Root>
