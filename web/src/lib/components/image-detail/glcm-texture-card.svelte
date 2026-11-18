<script lang="ts">
	import * as Card from "#lib/components/ui/card/index.js";
	import type { GlcmFeature, GlcmMetricSet } from "#lib/images.js";

	let { data }: { data?: GlcmFeature } = $props();

	type AngleKey = "summary" | "0" | "45" | "90" | "135";
	let selectedAngle = $state<AngleKey>("summary");

	let currentMetrics = $derived.by<GlcmMetricSet | undefined>(() => {
		if (!data) return undefined;
		if (selectedAngle === "summary") return data.summary;
		return data.by_angle?.[selectedAngle] || data.summary;
	});

	const metricDefinitions = [
		{
			id: "contrast",
			name: "Contrast",
			desc: "Measures local gray-level variation and edges",
			format: (v: number) => v.toFixed(2),
		},
		{
			id: "correlation",
			name: "Correlation",
			desc: "Linear dependency of gray levels in neighboring pixels",
			format: (v: number) => v.toFixed(3),
		},
		{
			id: "energy",
			name: "Energy (ASM)",
			desc: "Measures texture uniformity and repetition",
			format: (v: number) => v.toFixed(4),
		},
		{
			id: "homogeneity",
			name: "Homogeneity",
			desc: "Closeness of distribution to diagonal (smoothness)",
			format: (v: number) => v.toFixed(3),
		},
	];
</script>

<Card.Root class="border border-border/80 shadow-xs">
	<Card.Header class="pb-3">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
			<div>
				<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
					GLCM Texture Analysis
				</Card.Title>
				<Card.Description class="text-xs text-muted-foreground">
					Gray-Level Co-occurrence Matrix (32 levels, distance $d=1$)
				</Card.Description>
			</div>

			<!-- Angle Selector -->
			<div class="flex items-center p-0.5 rounded-lg border border-border bg-muted/40 w-fit">
				<button
					type="button"
					class="px-2.5 py-1 text-2xs font-medium rounded-md transition-all cursor-pointer {selectedAngle === 'summary'
						? 'bg-card text-foreground font-semibold shadow-2xs border border-border/60'
						: 'text-muted-foreground hover:text-foreground'}"
					onclick={() => (selectedAngle = "summary")}
				>
					Averaged
				</button>
				<button
					type="button"
					class="px-2.5 py-1 text-2xs font-medium rounded-md transition-all cursor-pointer {selectedAngle === '0'
						? 'bg-card text-foreground font-semibold shadow-2xs border border-border/60'
						: 'text-muted-foreground hover:text-foreground'}"
					onclick={() => (selectedAngle = "0")}
				>
					0°
				</button>
				<button
					type="button"
					class="px-2.5 py-1 text-2xs font-medium rounded-md transition-all cursor-pointer {selectedAngle === '45'
						? 'bg-card text-foreground font-semibold shadow-2xs border border-border/60'
						: 'text-muted-foreground hover:text-foreground'}"
					onclick={() => (selectedAngle = "45")}
				>
					45°
				</button>
				<button
					type="button"
					class="px-2.5 py-1 text-2xs font-medium rounded-md transition-all cursor-pointer {selectedAngle === '90'
						? 'bg-card text-foreground font-semibold shadow-2xs border border-border/60'
						: 'text-muted-foreground hover:text-foreground'}"
					onclick={() => (selectedAngle = "90")}
				>
					90°
				</button>
				<button
					type="button"
					class="px-2.5 py-1 text-2xs font-medium rounded-md transition-all cursor-pointer {selectedAngle === '135'
						? 'bg-card text-foreground font-semibold shadow-2xs border border-border/60'
						: 'text-muted-foreground hover:text-foreground'}"
					onclick={() => (selectedAngle = "135")}
				>
					135°
				</button>
			</div>
		</div>
	</Card.Header>

	<Card.Content>
		{#if !data || !currentMetrics}
			<div class="text-xs text-muted-foreground py-6 text-center">
				No GLCM texture metrics extracted.
			</div>
		{:else}
			<div class="grid grid-cols-2 md:grid-cols-4 gap-2.5">
				{#each metricDefinitions as m}
					{@const val = currentMetrics[m.id as keyof GlcmMetricSet]}
					<div class="p-3 rounded-lg border border-border/80 bg-card hover:bg-muted/30 transition-colors flex flex-col justify-between">
						<div>
							<div class="text-2xs font-medium uppercase tracking-wider text-muted-foreground">
								{m.name}
							</div>
							<div class="text-lg font-bold font-mono text-foreground mt-0.5">
								{val !== undefined ? m.format(val) : "—"}
							</div>
						</div>
						<div class="text-[10px] text-muted-foreground/80 mt-2 leading-tight">
							{m.desc}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</Card.Content>
</Card.Root>
