<script lang="ts">
	import * as Card from "#lib/components/ui/card/index.js";
	import type { LbpHistogramFeature } from "#lib/images.js";

	let { data }: { data?: LbpHistogramFeature } = $props();

	let bins = $derived(data?.bins || []);
	let labels = $derived(data?.labels || ["0", "1", "2", "3", "4", "5", "6", "7", "8", "non-uniform"]);

	let maxBinVal = $derived.by(() => {
		if (bins.length === 0) return 1.0;
		const max = Math.max(...bins);
		return max > 0 ? max : 1.0;
	});
</script>

<Card.Root class="border border-border/80 shadow-xs">
	<Card.Header class="pb-3">
		<div class="flex items-center justify-between">
			<div>
				<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
					Local Binary Patterns (LBP)
				</Card.Title>
				<Card.Description class="text-xs text-muted-foreground">
					Uniform micro-texture pattern histogram ($P=8, R=1$, 10 bins)
				</Card.Description>
			</div>
			<span class="text-2xs font-mono px-2 py-0.5 rounded-full bg-muted text-muted-foreground border border-border/60">
				10-D Vector
			</span>
		</div>
	</Card.Header>

	<Card.Content class="space-y-3">
		{#if !data || bins.length === 0}
			<div class="text-xs text-muted-foreground py-6 text-center">
				No LBP histogram data available.
			</div>
		{:else}
			<div class="w-full bg-muted/20 border border-border/60 rounded-lg p-3">
				<svg
					viewBox="0 0 400 130"
					class="w-full h-32 overflow-visible select-none"
					preserveAspectRatio="none"
				>
					<!-- Grid lines -->
					<line x1="0" y1="100" x2="400" y2="100" stroke="currentColor" stroke-opacity="0.2" stroke-width="1" />
					<line x1="0" y1="50" x2="400" y2="50" stroke="currentColor" stroke-opacity="0.1" stroke-dasharray="2,2" stroke-width="1" />

					<!-- Bars -->
					{#each bins as val, i}
						{@const slotW = 400 / bins.length}
						{@const pad = slotW * 0.16}
						{@const barW = Math.max(3, slotW - pad * 2)}
						{@const barH = Math.max(2, (val / maxBinVal) * 98)}
						{@const barX = i * slotW + pad}
						{@const barY = 100 - barH}
						{@const isNonUniform = i === bins.length - 1}

						<g class="transition-all duration-150 group">
							<rect
								x={barX}
								y={barY}
								width={barW}
								height={barH}
								rx="2"
								class="{isNonUniform
									? 'fill-amber-500/80 hover:fill-amber-500'
									: 'fill-primary/80 hover:fill-primary'} transition-colors cursor-pointer"
							>
								<title>Pattern '{labels[i]}': {(val * 100).toFixed(2)}% ({val.toFixed(4)})</title>
							</rect>
							<!-- Label -->
							<text
								x={barX + barW / 2}
								y="118"
								text-anchor="middle"
								font-size="8.5"
								class="fill-muted-foreground font-mono select-none"
							>
								{isNonUniform ? "NU" : labels[i]}
							</text>
						</g>
					{/each}
				</svg>
			</div>

			<div class="flex items-center justify-between text-2xs text-muted-foreground px-1">
				<span>
					Dominant Pattern: <strong class="text-foreground font-mono">{labels[bins.indexOf(Math.max(...bins))]}</strong>
				</span>
				<span>
					Non-Uniform Ratio: <strong class="text-foreground font-mono">{(bins[bins.length - 1] * 100).toFixed(1)}%</strong>
				</span>
			</div>
		{/if}
	</Card.Content>
</Card.Root>
