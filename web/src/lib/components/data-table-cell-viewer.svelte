<script lang="ts">
	import PhotoIcon from "@tabler/icons-svelte/icons/photo";
	import SparklesIcon from "@tabler/icons-svelte/icons/sparkles";
	import * as Drawer from "#lib/components/ui/drawer/index.js";
	import { IsMobile } from "#lib/hooks/is-mobile.svelte.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Separator } from "#lib/components/ui/separator/index.js";
	import type { Schema } from "./schemas.js";

	const isMobile = new IsMobile();

	let { item }: { item: Schema } = $props();
</script>

<Drawer.Root direction={isMobile.current ? "bottom" : "right"}>
	<Drawer.Trigger>
		{#snippet child({ props })}
			<div class="flex items-center gap-3">
				<div class="flex size-9 shrink-0 items-center justify-center rounded-md border bg-muted/30 overflow-hidden">
					{#if item.thumbnail}
						<img src={item.thumbnail} alt={item.filename} class="size-full object-cover" />
					{:else}
						<PhotoIcon class="size-4 text-muted-foreground" />
					{/if}
				</div>
				<Button variant="link" class="h-auto p-0 font-medium text-start text-sm text-foreground hover:underline" {...props}>
					{item.filename}
				</Button>
			</div>
		{/snippet}
	</Drawer.Trigger>
	<Drawer.Content class="sm:max-w-md">
		<Drawer.Header class="gap-1 border-b pb-4">
			<div class="flex items-center gap-2">
				<Badge variant="outline" class="font-normal text-xs">{item.category}</Badge>
				<span class="text-xs text-muted-foreground">&bull;</span>
				<span class="text-xs text-muted-foreground font-mono">ID #{item.id}</span>
			</div>
			<Drawer.Title class="text-lg font-semibold tracking-tight">{item.filename}</Drawer.Title>
			<Drawer.Description class="text-xs text-muted-foreground">
				GHIM-10K Image Descriptor & Feature Relevance Inspection
			</Drawer.Description>
		</Drawer.Header>

		<div class="flex flex-col gap-5 p-6 overflow-y-auto">
			<!-- Image Preview Container -->
			<div class="relative aspect-video w-full rounded-lg border bg-muted/20 overflow-hidden flex items-center justify-center">
				{#if item.thumbnail}
					<img src={item.thumbnail} alt={item.filename} class="h-full w-full object-cover" />
				{:else}
					<PhotoIcon class="size-12 text-muted-foreground/50" />
				{/if}
			</div>

			<!-- Visual Descriptors Breakdown -->
			<div class="flex flex-col gap-2.5">
				<h4 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Extracted Descriptors</h4>
				
				<div class="grid grid-cols-2 gap-3 text-xs">
					<div class="rounded-lg border bg-muted/30 p-2.5">
						<span class="text-muted-foreground">Descriptor Family:</span>
						<p class="font-medium mt-0.5 text-foreground">{item.descriptorType}</p>
					</div>
					<div class="rounded-lg border bg-muted/30 p-2.5">
						<span class="text-muted-foreground">Vector Dimension:</span>
						<p class="font-mono font-medium mt-0.5 text-foreground">{item.vectorDim}-D Float32</p>
					</div>
					<div class="rounded-lg border bg-muted/30 p-2.5">
						<span class="text-muted-foreground">Similarity Score:</span>
						<p class="font-mono font-medium mt-0.5 text-foreground">{(item.similarityScore * 100).toFixed(1)}%</p>
					</div>
					<div class="rounded-lg border bg-muted/30 p-2.5">
						<span class="text-muted-foreground">Relevance Weight:</span>
						<p class="font-mono font-medium mt-0.5 text-foreground">{item.feedbackWeight}</p>
					</div>
				</div>
			</div>

			<Separator />

			<!-- Relevance Feedback Adjustment -->
			<div class="flex flex-col gap-3">
				<div class="flex items-center gap-1.5">
					<SparklesIcon class="size-4 text-primary" />
					<h4 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Interactive Relevance Feedback</h4>
				</div>
				<p class="text-xs text-muted-foreground">
					Label this image as relevant to update the query descriptor covariance matrix according to the Group 13 assignment specifications.
				</p>
				<div class="flex gap-2 pt-1">
					<Button variant="default" size="sm" class="flex-1 text-xs">
						Mark Relevant (+1)
					</Button>
					<Button variant="outline" size="sm" class="flex-1 text-xs text-destructive hover:bg-destructive/10">
						Mark Irrelevant (-1)
					</Button>
				</div>
			</div>
		</div>

		<Drawer.Footer class="border-t pt-4">
			<Drawer.Close>
				{#snippet child({ props })}
					<Button variant="outline" class="w-full" {...props}>Close</Button>
				{/snippet}
			</Drawer.Close>
		</Drawer.Footer>
	</Drawer.Content>
</Drawer.Root>
