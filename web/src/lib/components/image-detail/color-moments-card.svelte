<script lang="ts">
	import * as Card from "#lib/components/ui/card/index.js";
	import type { ColorMomentsFeature } from "#lib/images.js";

	let { data }: { data?: ColorMomentsFeature } = $props();

	const channelLabels: Record<string, { label: string; desc: string; badge: string }> = {
		h: { label: "Hue (H)", desc: "Dominant chromatic frequency", badge: "H" },
		s: { label: "Saturation (S)", desc: "Color purity & vividness", badge: "S" },
		v: { label: "Value (V)", desc: "Luminance & brightness", badge: "V" },
	};
</script>

<Card.Root class="border border-border/80 shadow-xs">
	<Card.Header class="pb-3">
		<div class="flex items-center justify-between">
			<div>
				<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
					Color Moments
				</Card.Title>
				<Card.Description class="text-xs text-muted-foreground">
					First 3 statistical moments (μ, σ, s) in normalized HSV
				</Card.Description>
			</div>
			<span class="text-2xs font-mono px-2 py-0.5 rounded-full bg-muted text-muted-foreground border border-border/60">
				9-D Vector
			</span>
		</div>
	</Card.Header>

	<Card.Content>
		{#if !data || !data.channels}
			<div class="text-xs text-muted-foreground py-4 text-center">
				No color moments data available.
			</div>
		{:else}
			<div class="overflow-x-auto rounded-lg border border-border/80">
				<table class="w-full text-left text-xs">
					<thead class="bg-muted/40 border-b border-border/80 text-2xs uppercase text-muted-foreground font-semibold">
						<tr>
							<th class="py-2.5 px-3">Channel</th>
							<th class="py-2.5 px-3 text-right">Mean (μ)</th>
							<th class="py-2.5 px-3 text-right">Std Dev (σ)</th>
							<th class="py-2.5 px-3 text-right">Skewness (s)</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-border/60">
						{#each ["h", "s", "v"] as ch}
							{@const chMeta = channelLabels[ch]}
							{@const m = data.channels[ch as keyof typeof data.channels]}
							<tr class="hover:bg-muted/30 transition-colors">
								<td class="py-2 px-3">
									<div class="flex items-center gap-2">
										<span class="size-5 rounded flex items-center justify-center font-bold text-2xs bg-muted text-foreground font-mono">
											{chMeta.badge}
										</span>
										<div>
											<div class="font-medium text-foreground">{chMeta.label}</div>
											<div class="text-[10px] text-muted-foreground">{chMeta.desc}</div>
										</div>
									</div>
								</td>
								<td class="py-2 px-3 text-right font-mono font-medium text-foreground">
									{m?.mean !== undefined ? m.mean.toFixed(4) : "—"}
								</td>
								<td class="py-2 px-3 text-right font-mono font-medium text-foreground">
									{m?.std !== undefined ? m.std.toFixed(4) : "—"}
								</td>
								<td class="py-2 px-3 text-right font-mono font-medium {m?.skewness && m.skewness < 0 ? 'text-amber-500' : 'text-foreground'}">
									{m?.skewness !== undefined ? m.skewness.toFixed(4) : "—"}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</Card.Content>
</Card.Root>
