<script lang="ts">
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";

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
		{#if isExtracting}
			<div class="mb-4 flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary ring-8 ring-primary/5">
				<Loader2Icon class="size-6 animate-spin" />
			</div>
		{/if}

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
			<span class="rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				Dominant Colors
			</span>
			<span class="rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				Color Histogram
			</span>
			<span class="rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				Color Moments
			</span>
			<span class="rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				GLCM & LBP Texture
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
					<span>Extracting Features...</span>
				{:else}
					<span>Extract Visual Descriptors</span>
				{/if}
			</Button>
		</div>
	</div>
</Card.Root>
