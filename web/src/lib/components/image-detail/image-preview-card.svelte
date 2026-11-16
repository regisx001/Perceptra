<script lang="ts">
	import type { ImageItem } from "#lib/images.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Dialog from "#lib/components/ui/dialog/index.js";
	import Maximize2Icon from "@lucide/svelte/icons/maximize-2";
	import CheckCircle2Icon from "@lucide/svelte/icons/check-circle-2";
	import ClockIcon from "@lucide/svelte/icons/clock";
	import AlertCircleIcon from "@lucide/svelte/icons/alert-circle";
	import SparklesIcon from "@lucide/svelte/icons/sparkles";

	let {
		image,
		imageUrl
	}: {
		image: ImageItem;
		imageUrl: string;
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

<Card.Root class="overflow-hidden border border-border bg-card shadow-xs">
	<!-- Card Header / Status Banner -->
	<div class="relative flex items-center justify-between border-b border-border/60 bg-muted/30 px-4 py-2.5">
		<div class="flex items-center gap-2">
			{#if image.source_type === "derived"}
				<Badge variant="secondary" class="gap-1 border-primary/20 bg-primary/10 text-primary font-medium text-xs">
					<SparklesIcon class="size-3" />
					Derived
				</Badge>
			{:else}
				<Badge variant="outline" class="font-normal text-xs text-muted-foreground">
					Original Upload
				</Badge>
			{/if}

			{#if image.processing_status === "indexed" || image.processing_status === "completed"}
				<Badge variant="outline" class="gap-1 border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-medium text-xs">
					<CheckCircle2Icon class="size-3" />
					Indexed
				</Badge>
			{:else if image.processing_status === "processing"}
				<Badge variant="outline" class="gap-1 border-blue-500/30 bg-blue-500/10 text-blue-600 dark:text-blue-400 font-medium text-xs">
					<ClockIcon class="size-3 animate-spin" />
					Processing
				</Badge>
			{:else if image.processing_status === "failed"}
				<Badge variant="outline" class="gap-1 border-destructive/30 bg-destructive/10 text-destructive font-medium text-xs">
					<AlertCircleIcon class="size-3" />
					Failed
				</Badge>
			{:else}
				<Badge variant="outline" class="gap-1 border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400 font-medium text-xs">
					<ClockIcon class="size-3" />
					Unindexed
				</Badge>
			{/if}
		</div>

		<Button
			variant="ghost"
			size="icon"
			class="size-8 text-muted-foreground hover:text-foreground"
			title="Open full-resolution lightbox"
			onclick={() => (isLightboxOpen = true)}
		>
			<Maximize2Icon class="size-4" />
		</Button>
	</div>

	<!-- Image Canvas / Viewport -->
	<div
		role="button"
		tabindex="0"
		class="group relative flex min-h-[300px] max-h-[460px] cursor-zoom-in items-center justify-center overflow-hidden bg-neutral-900/5 dark:bg-neutral-950/40 p-4 transition-colors"
		onclick={() => (isLightboxOpen = true)}
		onkeydown={(e) => e.key === "Enter" && (isLightboxOpen = true)}
	>
		<img
			src={imageUrl}
			alt={image.filename}
			class="max-h-[420px] w-auto max-w-full rounded object-contain shadow-sm transition-transform duration-200 group-hover:scale-[1.01]"
			loading="eager"
		/>

		<div class="pointer-events-none absolute inset-0 flex items-center justify-center bg-black/20 opacity-0 backdrop-blur-[1px] transition-opacity group-hover:opacity-100">
			<span class="inline-flex items-center gap-1.5 rounded-full bg-background/90 px-3 py-1.5 text-xs font-medium text-foreground shadow-sm">
				<Maximize2Icon class="size-3.5" />
				Click to expand
			</span>
		</div>
	</div>

	<!-- Bottom Image Metric Bar -->
	{#if image.width && image.height}
		<div class="flex items-center justify-between border-t border-border/50 bg-muted/20 px-4 py-2 text-xs text-muted-foreground">
			<span class="font-mono">
				{image.width} × {image.height} px
			</span>
			{#if formatAspectRatio(image.width, image.height)}
				<span class="font-mono">
					{formatAspectRatio(image.width, image.height)} ratio
				</span>
			{/if}
		</div>
	{/if}
</Card.Root>

<!-- Lightbox Modal -->
<Dialog.Root bind:open={isLightboxOpen}>
	<Dialog.Content class="max-w-5xl border-border bg-background p-2 sm:p-4">
		<Dialog.Header class="px-2 pt-2 pb-0">
			<Dialog.Title class="truncate text-base font-medium">
				{image.filename}
			</Dialog.Title>
			<Dialog.Description class="font-mono text-xs text-muted-foreground">
				{image.width ? `${image.width} × ${image.height} px • ` : ""}{image.mime_type}
			</Dialog.Description>
		</Dialog.Header>

		<div class="mt-3 flex max-h-[75vh] items-center justify-center overflow-auto rounded-lg bg-neutral-900/10 p-2 dark:bg-neutral-950/60">
			<img
				src={imageUrl}
				alt={image.filename}
				class="max-h-[70vh] w-auto max-w-full rounded object-contain shadow-lg"
			/>
		</div>
	</Dialog.Content>
</Dialog.Root>
