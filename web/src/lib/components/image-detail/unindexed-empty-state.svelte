<script lang="ts">
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import SparklesIcon from "@lucide/svelte/icons/sparkles";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import EyeIcon from "@lucide/svelte/icons/eye";
	import BarChart3Icon from "@lucide/svelte/icons/bar-chart-3";
	import PaletteIcon from "@lucide/svelte/icons/palette";
	import GridIcon from "@lucide/svelte/icons/grid";

	let {
		isExtracting = false,
		onExtract
	}: {
		isExtracting?: boolean;
		onExtract: () => void;
	} = $props();
</script>

<Card.Root class="border-dashed border-2 bg-card/60 p-8 text-center backdrop-blur-sm">
	<div class="mx-auto flex max-w-lg flex-col items-center">
		<div class="mb-4 flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary ring-8 ring-primary/5">
			{#if isExtracting}
				<Loader2Icon class="size-7 animate-spin" />
			{:else}
				<SparklesIcon class="size-7" />
			{/if}
		</div>

		<h3 class="text-xl font-semibold tracking-tight text-foreground">
			{isExtracting ? "Extracting Visual Descriptors..." : "Visual Descriptors Not Indexed"}
		</h3>

		<p class="mt-2 text-sm text-muted-foreground leading-relaxed">
			{isExtracting
				? "Analyzing image channels, color distribution, co-occurrence matrices, and local binary patterns. This may take a moment."
				: "This image hasn't been processed for visual features yet. Extracting descriptors will compute color distribution, statistical moments, dominant palettes, GLCM texture, and uniform LBP patterns for similarity search."}
		</p>

		<!-- Feature badges preview -->
		<div class="mt-6 flex flex-wrap items-center justify-center gap-2">
			<span class="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				<PaletteIcon class="size-3 text-primary" /> Dominant Colors
			</span>
			<span class="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				<BarChart3Icon class="size-3 text-primary" /> Color Histogram
			</span>
			<span class="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				<EyeIcon class="size-3 text-primary" /> Color Moments
			</span>
			<span class="inline-flex items-center gap-1.5 rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				<GridIcon class="size-3 text-primary" /> GLCM & LBP
			</span>
		</div>

		<div class="mt-7">
			<Button
				variant="default"
				size="lg"
				disabled={isExtracting}
				onclick={onExtract}
				class="gap-2 shadow-sm"
			>
				{#if isExtracting}
					<Loader2Icon class="size-4 animate-spin" />
					Extracting Features...
				{:else}
					<SparklesIcon class="size-4" />
					Extract Visual Descriptors
				{/if}
			</Button>
		</div>
	</div>
</Card.Root>
