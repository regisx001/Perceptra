<script lang="ts">
	import { imageService, type ImageItem } from "#lib/images.js";
	import * as Dialog from "#lib/components/ui/dialog/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as m from "#lib/paraglide/messages.js";

	let {
		open = $bindable(false),
		image,
		derivatives = []
	}: {
		open: boolean;
		image: ImageItem;
		derivatives: ImageItem[];
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

<Dialog.Root bind:open>
	<Dialog.Content class="max-w-2xl w-full border-border bg-background p-6 flex flex-col max-h-[85vh]">
		<Dialog.Header class="pb-3 border-b border-border/60 shrink-0">
			<div class="flex items-center justify-between">
				<div>
					<Dialog.Title class="text-base font-semibold tracking-tight text-foreground flex items-center gap-2">
						<span>{m.image_detail_lineage_title()}</span>
						<Badge variant="secondary" class="font-mono text-xs">
							{derivatives.length}
						</Badge>
					</Dialog.Title>
					<Dialog.Description class="text-xs text-muted-foreground mt-0.5">
						{m.image_detail_lineage_desc()}
					</Dialog.Description>
				</div>
			</div>
		</Dialog.Header>

		<div class="space-y-5 overflow-y-auto py-3 min-h-0">
			<!-- Lineage / Parent Image (if this image was itself derived) -->
			{#if image.parent_image_id}
				<div class="rounded-lg border border-primary/20 bg-primary/5 p-4 text-xs space-y-2.5">
					<div class="flex items-center justify-between font-medium text-foreground">
						<span class="text-primary font-medium">
							Parent Origin
						</span>
						<a
							href="/dashboard/images/{image.parent_image_id}"
							class="text-primary hover:underline font-mono text-[11px] font-medium"
							onclick={() => (open = false)}
						>
							View Parent Image →
						</a>
					</div>

					{#if image.transformation_params}
						<div class="mt-2 pt-2 border-t border-primary/10">
							<div class="text-[11px] font-medium text-muted-foreground mb-1">
								Applied Transformations
							</div>
							<pre class="bg-background/80 p-2.5 rounded border border-border/40 font-mono text-[11px] text-foreground overflow-x-auto max-h-36">
{JSON.stringify(image.transformation_params, null, 2)}
							</pre>
						</div>
					{/if}
				</div>
			{/if}

			<!-- Derived Versions Section -->
			<div class="space-y-3">
				<div class="flex items-center justify-between">
					<h4 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
						Derived Versions ({derivatives.length})
					</h4>
					{#if derivatives.length > 0}
						<Button
							variant="outline"
							size="sm"
							class="h-7 text-xs"
							href="/dashboard/transform?image_id={image.id}"
							onclick={() => (open = false)}
						>
							New Variation
						</Button>
					{/if}
				</div>

				{#if derivatives.length > 0}
					<div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
						{#each derivatives as item (item.id)}
							<a
								href="/dashboard/images/{item.id}"
								class="group relative flex flex-col overflow-hidden rounded-lg border border-border bg-muted/20 p-2 transition-all hover:border-primary/50 hover:bg-muted/40 hover:shadow-xs"
								onclick={() => (open = false)}
							>
								<div class="aspect-square w-full overflow-hidden rounded bg-neutral-900/10 dark:bg-neutral-950/60 flex items-center justify-center">
									<img
										src={imageService.getImageUrl(item.id)}
										alt={item.filename}
										class="h-full w-full object-contain"
										loading="lazy"
									/>
								</div>

								<div class="mt-2 space-y-1">
									<Badge variant="outline" class="text-[10px] px-1.5 py-0 font-medium border-primary/20 text-primary truncate max-w-full">
										{getOperationLabel(item)}
									</Badge>
									<p class="truncate font-mono text-[11px] text-muted-foreground">
										{item.width && item.height ? `${item.width} × ${item.height}` : item.filename}
									</p>
								</div>
							</a>
						{/each}
					</div>
				{:else}
					<div class="flex flex-col items-center justify-center rounded-lg border border-dashed border-border/80 bg-muted/10 p-8 text-center">
						<p class="text-sm font-medium text-foreground">No derived versions yet</p>
						<p class="mt-1 text-xs text-muted-foreground max-w-sm">
							Apply non-destructive transformations like crop, resize, rotate, flip, shear, or affine in the Transformation Studio.
						</p>
						<Button
							variant="default"
							size="sm"
							class="mt-4 text-xs h-8 shadow-xs"
							href="/dashboard/transform?image_id={image.id}"
							onclick={() => (open = false)}
						>
							Create Derived Version
						</Button>
					</div>
				{/if}
			</div>
		</div>
	</Dialog.Content>
</Dialog.Root>
