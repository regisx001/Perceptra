<script lang="ts">
	import * as Card from "#lib/components/ui/card/index.js";
	import * as ToggleGroup from "#lib/components/ui/toggle-group/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as m from "#lib/paraglide/messages.js";
	import CopyIcon from "@lucide/svelte/icons/copy";
	import CheckIcon from "@lucide/svelte/icons/check";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import PaletteIcon from "@lucide/svelte/icons/palette";
	import SparklesIcon from "@lucide/svelte/icons/sparkles";
	import type { DescriptorsMap, DominantColorsFeature } from "#lib/images.js";

	let {
		descriptors = {},
		isExtracting = false,
		onExtractCluster
	}: {
		descriptors?: DescriptorsMap;
		isExtracting?: boolean;
		onExtractCluster?: (k: number) => Promise<void>;
	} = $props();

	let selectedK = $state<"5" | "10" | "20">("5");
	let copiedHex = $state<string | null>(null);
	let isLocalExtracting = $state(false);

	// Resolve the active dominant colors feature based on selected cluster count
	const activeData = $derived.by<DominantColorsFeature | undefined>(() => {
		if (selectedK === "5") {
			return descriptors.dominant_colors;
		}
		if (selectedK === "10") {
			return descriptors.dominant_colors_10;
		}
		if (selectedK === "20") {
			return descriptors.dominant_colors_20;
		}
		return undefined;
	});

	const clusters = $derived.by(() => {
		return activeData?.clusters || [];
	});

	const hasDataForSelectedK = $derived.by(() => {
		return Boolean(clusters.length > 0);
	});

	async function copyToClipboard(hex: string) {
		try {
			await navigator.clipboard.writeText(hex);
			copiedHex = hex;
			setTimeout(() => {
				if (copiedHex === hex) copiedHex = null;
			}, 2000);
		} catch {
			// Fallback silently if clipboard is unavailable
		}
	}

	async function handleCompute() {
		if (!onExtractCluster || isLocalExtracting) return;
		isLocalExtracting = true;
		try {
			await onExtractCluster(Number(selectedK));
		} finally {
			isLocalExtracting = false;
		}
	}
</script>

<Card.Root class="border border-border/80 shadow-xs">
	<Card.Header class="pb-3">
		<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<div class="flex items-center gap-2">
					<PaletteIcon class="size-4 text-primary" />
					<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
						{m.image_detail_dom_colors_title()}
					</Card.Title>
				</div>
				<Card.Description class="text-xs text-muted-foreground mt-0.5">
					{m.image_detail_dom_colors_desc()}
				</Card.Description>
			</div>

			<!-- Cluster Selector using shadcn-svelte ToggleGroup -->
			<div class="flex items-center gap-2">
				<ToggleGroup.Root
					type="single"
					bind:value={selectedK}
					variant="outline"
					size="sm"
					class="*:data-[slot=toggle-group-item]:!px-2.5 *:data-[slot=toggle-group-item]:!h-7 *:data-[slot=toggle-group-item]:!text-xs"
				>
					<ToggleGroup.Item value="5">
						5 Colors
					</ToggleGroup.Item>
					<ToggleGroup.Item value="10">
						10 Colors
					</ToggleGroup.Item>
					<ToggleGroup.Item value="20">
						20 Colors
					</ToggleGroup.Item>
				</ToggleGroup.Root>

				{#if hasDataForSelectedK}
					<Badge variant="outline" class="font-mono text-xs">
						{clusters.length} Clusters
					</Badge>
				{/if}
			</div>
		</div>
	</Card.Header>

	<Card.Content class="space-y-4">
		{#if !hasDataForSelectedK}
			<!-- Missing cluster computation empty state -->
			<div class="flex flex-col items-center justify-center p-8 text-center rounded-lg border border-dashed border-border/70 bg-muted/10 gap-2">
				<PaletteIcon class="size-7 stroke-1 text-muted-foreground/60" />
				<div class="text-xs font-semibold text-foreground">
					{selectedK} Dominant Colors not computed yet
				</div>
				<p class="text-xs text-muted-foreground max-w-sm">
					Run clustering analysis with k = {selectedK} to decompose this image into {selectedK} dominant centroid colors and proportional weights.
				</p>
				<Button
					size="sm"
					class="mt-2 h-8 text-xs gap-1.5 font-semibold"
					onclick={handleCompute}
					disabled={isExtracting || isLocalExtracting}
				>
					{#if isLocalExtracting || isExtracting}
						<Loader2Icon class="size-3.5 animate-spin" />
						<span>{m.image_detail_dom_colors_computing({ k: Number(selectedK) })}</span>
					{:else}
						<SparklesIcon class="size-3.5" />
						<span>{m.image_detail_dom_colors_compute({ k: Number(selectedK) })}</span>
					{/if}
				</Button>
			</div>
		{:else}
			<!-- Stacked Color Bar proportional to cluster weights -->
			<div class="space-y-1.5">
				<div class="flex h-6 w-full rounded-lg overflow-hidden border border-border/80 shadow-inner">
					{#each clusters as cluster (cluster.rank)}
						<div
							style="width: {cluster.percentage}%; background-color: {cluster.hex};"
							class="h-full relative group transition-all duration-150 hover:brightness-110 cursor-pointer"
							title="{cluster.hex} • {cluster.percentage}% (Rank #{cluster.rank})"
							role="button"
							tabindex="0"
							onclick={() => copyToClipboard(cluster.hex)}
							onkeydown={(e) => e.key === 'Enter' && copyToClipboard(cluster.hex)}
						></div>
					{/each}
				</div>
				<div class="flex justify-between text-2xs text-muted-foreground px-0.5">
					<span>0%</span>
					<span>50%</span>
					<span>100%</span>
				</div>
			</div>

			<!-- Swatch Chips Grid: adapts cleanly for 5, 10, or 20 clusters -->
			<div
				class="grid gap-2 {selectedK === '20'
					? 'grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-10'
					: selectedK === '10'
					? 'grid-cols-2 sm:grid-cols-3 md:grid-cols-5'
					: 'grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5'}"
			>
				{#each clusters as cluster (cluster.rank)}
					<div class="p-2 rounded-lg border border-border/80 bg-card hover:bg-muted/40 transition-colors flex flex-col gap-1.5">
						<div class="flex items-center gap-1.5">
							<div
								class="size-4.5 rounded-md border border-border/80 shadow-2xs shrink-0"
								style="background-color: {cluster.hex};"
							></div>
							<span class="text-xs font-bold text-foreground truncate">
								{cluster.percentage}%
							</span>
							<span class="ms-auto text-[10px] font-mono text-muted-foreground">
								#{cluster.rank}
							</span>
						</div>

						<div class="flex items-center justify-between pt-0.5 border-t border-border/50">
							<span class="font-mono text-[10px] text-muted-foreground truncate">
								{cluster.hex}
							</span>
							<button
								type="button"
								class="text-muted-foreground hover:text-foreground p-0.5 rounded transition-colors cursor-pointer shrink-0"
								onclick={() => copyToClipboard(cluster.hex)}
								title="Copy Hex"
							>
								{#if copiedHex === cluster.hex}
									<CheckIcon class="size-3 text-emerald-500" />
								{:else}
									<CopyIcon class="size-3" />
								{/if}
							</button>
						</div>

						<div class="text-[9px] font-mono text-muted-foreground/80 truncate">
							{cluster.rgb.join(", ")}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</Card.Content>
</Card.Root>
