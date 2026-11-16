<script lang="ts">
	import * as Card from "#lib/components/ui/card/index.js";
	import CopyIcon from "@lucide/svelte/icons/copy";
	import CheckIcon from "@lucide/svelte/icons/check";
	import PaletteIcon from "@lucide/svelte/icons/palette";
	import type { DominantColorsFeature } from "#lib/images.js";

	let { data }: { data?: DominantColorsFeature } = $props();

	let copiedHex = $state<string | null>(null);

	async function copyToClipboard(hex: string) {
		try {
			await navigator.clipboard.writeText(hex);
			copiedHex = hex;
			setTimeout(() => {
				if (copiedHex === hex) copiedHex = null;
			}, 2000);
		} catch {
			// Fallback silently if clipboard blocked
		}
	}
</script>

<Card.Root class="border border-border/80 shadow-xs">
	<Card.Header class="pb-3">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<div class="p-1.5 rounded-md bg-primary/10 text-primary">
					<PaletteIcon class="size-4" />
				</div>
				<div>
					<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
						Dominant Colors
					</Card.Title>
					<Card.Description class="text-xs text-muted-foreground">
						Top 5 clustered color centroids via MiniBatchKMeans (k = 5)
					</Card.Description>
				</div>
			</div>
			{#if data?.clusters?.length}
				<span class="text-2xs font-mono px-2 py-0.5 rounded-full bg-muted text-muted-foreground border border-border/60">
					{data.clusters.length} Clusters
				</span>
			{/if}
		</div>
	</Card.Header>

	<Card.Content class="space-y-4">
		{#if !data || !data.clusters || data.clusters.length === 0}
			<div class="text-xs text-muted-foreground py-4 text-center">
				No dominant color clusters extracted.
			</div>
		{:else}
			<!-- Stacked Color Bar -->
			<div class="space-y-1.5">
				<div class="flex h-6 w-full rounded-lg overflow-hidden border border-border/80 shadow-inner">
					{#each data.clusters as cluster (cluster.rank)}
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

			<!-- Swatch Chips Grid -->
			<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2.5">
				{#each data.clusters as cluster (cluster.rank)}
					<div class="p-2 rounded-lg border border-border/80 bg-card hover:bg-muted/40 transition-colors flex flex-col gap-1.5">
						<div class="flex items-center gap-2">
							<div
								class="size-5 rounded-md border border-border/80 shadow-2xs shrink-0"
								style="background-color: {cluster.hex};"
							></div>
							<span class="text-xs font-bold text-foreground">
								{cluster.percentage}%
							</span>
							<span class="ms-auto text-2xs font-mono text-muted-foreground">
								#{cluster.rank}
							</span>
						</div>

						<div class="flex items-center justify-between pt-0.5 border-t border-border/50">
							<span class="font-mono text-2xs text-muted-foreground">
								{cluster.hex}
							</span>
							<button
								type="button"
								class="text-muted-foreground hover:text-foreground p-0.5 rounded transition-colors cursor-pointer"
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

						<div class="text-[10px] font-mono text-muted-foreground/80 truncate">
							rgb({cluster.rgb.join(", ")})
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</Card.Content>
</Card.Root>
