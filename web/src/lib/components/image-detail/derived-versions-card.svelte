<script lang="ts">
	import { imageService, type ImageItem } from "#lib/images.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Button } from "#lib/components/ui/button/index.js";

	let {
		derivatives = [],
		parentImageId
	}: {
		derivatives: ImageItem[];
		parentImageId: string;
	} = $props();

	function getOperationLabel(derivative: ImageItem): string {
		const params = derivative.transformation_params;
		if (!params || typeof params !== "object") return "Derived";
		const ops: string[] = [];
		if (params.crop) ops.push("Crop");
		if (params.resize) ops.push("Resize");
		if (params.rotate) ops.push("Rotate");
		if (params.flip) ops.push("Flip");
		if (params.shear) ops.push("Shear");
		if (params.affine) ops.push("Affine");
		return ops.length > 0 ? ops.join(" + ") : "Derived";
	}
</script>

<Card.Root class="border border-border bg-card shadow-xs">
	<Card.Header class="pb-3 pt-4 px-4 sm:px-5">
		<div class="flex items-center justify-between">
			<Card.Title class="text-sm font-semibold tracking-tight text-foreground">
				Derived Variations
			</Card.Title>
			<Badge variant="secondary" class="font-mono text-xs">
				{derivatives.length}
			</Badge>
		</div>
	</Card.Header>

	<Card.Content class="px-4 sm:px-5 pb-5 pt-0">
		{#if derivatives.length > 0}
			<div class="grid grid-cols-2 gap-3 sm:grid-cols-2">
				{#each derivatives as item (item.id)}
					<a
						href="/dashboard/images/{item.id}"
						class="group relative flex flex-col overflow-hidden rounded-lg border border-border bg-muted/20 p-2 transition-all hover:border-primary/50 hover:bg-muted/40 hover:shadow-xs"
					>
						<div class="aspect-square w-full overflow-hidden rounded bg-neutral-900/10 dark:bg-neutral-950/60 flex items-center justify-center">
							<img
								src={imageService.getImageUrl(item.id)}
								alt={item.filename}
								class="h-full w-full object-contain transition-transform group-hover:scale-105"
								loading="lazy"
							/>
						</div>

						<div class="mt-2 space-y-1">
							<div class="flex items-center justify-between gap-1">
								<Badge variant="outline" class="text-[10px] px-1.5 py-0 font-medium border-primary/20 text-primary truncate">
									{getOperationLabel(item)}
								</Badge>
							</div>

							<p class="truncate font-mono text-[11px] text-muted-foreground">
								{item.width && item.height ? `${item.width} × ${item.height}` : item.filename}
							</p>
						</div>
					</a>
				{/each}
			</div>
		{:else}
			<div class="flex flex-col items-center justify-center rounded-lg border border-dashed border-border/80 bg-muted/10 p-6 text-center">
				<p class="text-xs font-medium text-foreground">No derived versions yet</p>
				<p class="mt-1 text-[11px] text-muted-foreground max-w-xs">
					Apply non-destructive transformations like crop, resize, rotate, flip, shear, or affine in the Transformation Studio.
				</p>
				<Button
					variant="outline"
					size="sm"
					class="mt-3 text-xs h-7"
					href="/dashboard/transform?image_id={parentImageId}"
				>
					Create Derived Version
				</Button>
			</div>
		{/if}
	</Card.Content>
</Card.Root>
