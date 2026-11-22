<script lang="ts">
	import type { ImageItem } from "#lib/images.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Dialog from "#lib/components/ui/dialog/index.js";

	let {
		image,
		imageUrl,
		derivativesCount = 0,
		onOpenLineage
	}: {
		image: ImageItem;
		imageUrl: string;
		derivativesCount?: number;
		onOpenLineage?: () => void;
	} = $props();

	let isLightboxOpen = $state(false);

	function formatAspectRatio(w?: number | null, h?: number | null): string {
		if (!w || !h) return "";
		const gcd = (a: number, b: number): number => (b === 0 ? a : gcd(b, a % b));
		const divisor = gcd(w, h);
		const rw = Math.round(w / divisor);
		const rh = Math.round(h / divisor);
		if (rw < 20 && rh < 20) return `${rw}:${rh}`;
		return `${(w / h).toFixed(2)}:1`;
	}
</script>

<div class="flex flex-col gap-2">
	<!-- Text above image only (Filename + Check Lineage + Dimensions) -->
	<div class="flex items-center justify-between text-xs text-muted-foreground px-0.5">
		<span class="font-mono text-xs font-semibold text-foreground truncate max-w-[150px] sm:max-w-[180px]" title={image.filename}>
			{image.filename}
		</span>

		<div class="flex items-center gap-2 shrink-0">
			{#if onOpenLineage}
				<Button
					variant="outline"
					size="sm"
					class="h-6 px-2.5 text-xs font-medium border-border bg-background hover:bg-muted shadow-xs gap-1.5"
					onclick={onOpenLineage}
				>
					<span>Check Lineage</span>
					{#if derivativesCount > 0}
						<span class="rounded-full bg-primary/10 text-primary px-1.5 py-0.2 text-[10px] font-mono">
							{derivativesCount}
						</span>
					{/if}
				</Button>
			{/if}

			{#if image.width && image.height}
				<span class="font-mono text-[11px] text-muted-foreground hidden sm:inline">
					{image.width} × {image.height} px
					{#if formatAspectRatio(image.width, image.height)}
						<span class="opacity-70">({formatAspectRatio(image.width, image.height)})</span>
					{/if}
				</span>
			{/if}
		</div>
	</div>

	<!-- Image Preview (No card style, clean container) -->
	<div
		role="button"
		tabindex="0"
		class="group relative flex min-h-[220px] max-h-[340px] w-full cursor-zoom-in items-center justify-center overflow-hidden rounded-xl bg-neutral-900/5 dark:bg-neutral-950/40 p-2 transition-colors"
		onclick={() => (isLightboxOpen = true)}
		onkeydown={(e) => e.key === "Enter" && (isLightboxOpen = true)}
	>
		<img
			src={imageUrl}
			alt={image.filename}
			class="max-h-[320px] w-auto max-w-full rounded-lg object-contain"
			loading="eager"
		/>

		<div class="pointer-events-none absolute inset-0 flex items-center justify-center rounded-xl bg-black/20 opacity-0 backdrop-blur-[1px] transition-opacity group-hover:opacity-100">
			<span class="rounded-full bg-background/90 px-3 py-1 text-xs font-medium text-foreground shadow-sm">
				Click to expand
			</span>
		</div>
	</div>
</div>

<!-- Preview Dialog (Much bigger lightbox modal) -->
<Dialog.Root bind:open={isLightboxOpen}>
	<Dialog.Content class="max-w-[95vw] w-full max-h-[95vh] h-[92vh] border-border bg-background p-4 sm:p-6 flex flex-col">
		<Dialog.Header class="px-1 pt-1 pb-2 shrink-0">
			<div class="flex items-center justify-between">
				<div>
					<Dialog.Title class="truncate text-base font-medium font-mono">
						{image.filename}
					</Dialog.Title>
					<Dialog.Description class="font-mono text-xs text-muted-foreground mt-0.5">
						{image.width ? `${image.width} × ${image.height} px • ` : ""}{image.mime_type}
						{#if formatAspectRatio(image.width, image.height)}
							• {formatAspectRatio(image.width, image.height)} ratio
						{/if}
					</Dialog.Description>
				</div>
			</div>
		</Dialog.Header>

		<div class="mt-2 flex-1 min-h-0 flex items-center justify-center overflow-hidden rounded-xl bg-neutral-900/10 p-4 dark:bg-neutral-950/60">
			<img
				src={imageUrl}
				alt={image.filename}
				class="max-h-full max-w-full w-auto h-auto rounded-lg object-contain shadow-2xl"
			/>
		</div>
	</Dialog.Content>
</Dialog.Root>
