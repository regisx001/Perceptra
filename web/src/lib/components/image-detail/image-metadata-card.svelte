<script lang="ts">
	import type { ImageItem } from "#lib/images.js";
	import type { CategoryItem } from "#lib/categories.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import * as Select from "#lib/components/ui/select/index.js";
	import * as m from "#lib/paraglide/messages.js";
	import CopyIcon from "@lucide/svelte/icons/copy";
	import CheckIcon from "@lucide/svelte/icons/check";
	import ArrowUpRightIcon from "@lucide/svelte/icons/arrow-up-right";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";

	let {
		image,
		categories = [],
		onCategoryChange
	}: {
		image: ImageItem;
		categories: CategoryItem[];
		onCategoryChange: (newCategoryId: string | null) => Promise<void>;
	} = $props();

	let copiedChecksum = $state(false);
	let isUpdatingCategory = $state(false);

	function formatBytes(bytes: number, decimals = 1): string {
		if (!bytes || bytes === 0) return "0 B";
		const k = 1024;
		const dm = decimals < 0 ? 0 : decimals;
		const sizes = ["B", "KB", "MB", "GB"];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
	}

	function formatDate(dateStr?: string): string {
		if (!dateStr) return "—";
		try {
			return new Date(dateStr).toLocaleString(undefined, {
				year: "numeric",
				month: "short",
				day: "numeric",
				hour: "2-digit",
				minute: "2-digit"
			});
		} catch {
			return dateStr;
		}
	}

	async function copyToClipboard(text: string) {
		try {
			await navigator.clipboard.writeText(text);
			copiedChecksum = true;
			setTimeout(() => {
				copiedChecksum = false;
			}, 2000);
		} catch (err) {
			console.error("Failed to copy:", err);
		}
	}

	async function handleCategorySelect(val: string | undefined) {
		if (val === undefined) return;
		isUpdatingCategory = true;
		try {
			const catId = val === "none" ? null : val;
			await onCategoryChange(catId);
		} finally {
			isUpdatingCategory = false;
		}
	}

	const selectedCategoryName = $derived.by(() => {
		if (!image.category_id) return "Uncategorized";
		const found = categories.find((c) => c.id === image.category_id);
		return found ? found.name : "Uncategorized";
	});
</script>

<Card.Root class="border border-border bg-card shadow-xs">
	<Card.Header class="pb-3 pt-4 px-4 sm:px-5">
		<Card.Title class="text-sm font-semibold tracking-tight text-foreground flex items-center gap-2">
			<span>{m.image_detail_meta_title()}</span>
		</Card.Title>
	</Card.Header>

	<Card.Content class="px-4 sm:px-5 pb-5 pt-0 space-y-4">
		<!-- Metadata Key-Value List -->
		<dl class="divide-y divide-border/60 text-xs">
			<div class="flex items-center justify-between py-2.5">
				<dt class="text-muted-foreground">{m.image_detail_meta_filename()}</dt>
				<dd class="font-medium text-foreground max-w-[240px] truncate text-right font-mono" title={image.filename}>
					{image.filename}
				</dd>
			</div>

			<div class="flex items-center justify-between py-2.5">
				<dt class="text-muted-foreground">{m.image_detail_meta_dimensions()}</dt>
				<dd class="font-mono text-foreground">
					{image.width && image.height ? `${image.width} × ${image.height} px` : "—"}
				</dd>
			</div>

			<div class="flex items-center justify-between py-2.5">
				<dt class="text-muted-foreground">{m.image_detail_meta_format()}</dt>
				<dd class="font-mono text-foreground">{image.mime_type || "—"}</dd>
			</div>

			<div class="flex items-center justify-between py-2.5">
				<dt class="text-muted-foreground">{m.image_detail_meta_filesize()}</dt>
				<dd class="font-mono text-foreground">{formatBytes(image.file_size)}</dd>
			</div>

			<div class="flex items-center justify-between py-2.5">
				<dt class="text-muted-foreground">{m.image_detail_meta_uploaded_at()}</dt>
				<dd class="text-foreground">{formatDate(image.created_at)}</dd>
			</div>

			<!-- Category Selector -->
			<div class="flex items-center justify-between py-2.5 gap-2">
				<dt class="text-muted-foreground">{m.image_detail_meta_category()}</dt>
				<dd class="flex items-center gap-1.5">
					{#if isUpdatingCategory}
						<Loader2Icon class="size-3.5 animate-spin text-muted-foreground" />
					{/if}
					<Select.Root
						type="single"
						value={image.category_id || "none"}
						onValueChange={handleCategorySelect}
						disabled={isUpdatingCategory}
					>
						<Select.Trigger class="h-7 text-xs px-2.5 min-w-[130px] font-normal border-border bg-background">
							<span class="truncate">{selectedCategoryName}</span>
						</Select.Trigger>
						<Select.Content align="end">
							<Select.Item value="none">
								<span class="text-muted-foreground italic">{m.categories_uncategorized_label()}</span>
							</Select.Item>
							{#each categories as cat (cat.id)}
								<Select.Item value={cat.id}>
									{cat.name}
								</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
				</dd>
			</div>

			<!-- Checksum Row -->
			{#if image.checksum}
				<div class="flex items-center justify-between py-2.5">
					<dt class="text-muted-foreground">SHA-256 Checksum</dt>
					<dd class="flex items-center gap-1">
						<code class="font-mono text-[11px] text-muted-foreground bg-muted/50 px-1.5 py-0.5 rounded max-w-[180px] truncate" title={image.checksum}>
							{image.checksum.substring(0, 12)}…{image.checksum.substring(image.checksum.length - 8)}
						</code>
						<Button
							variant="ghost"
							size="icon"
							class="size-6 text-muted-foreground hover:text-foreground"
							title="Copy full checksum"
							onclick={() => copyToClipboard(image.checksum || "")}
						>
							{#if copiedChecksum}
								<CheckIcon class="size-3 text-emerald-500" />
							{:else}
								<CopyIcon class="size-3" />
							{/if}
						</Button>
					</dd>
				</div>
			{/if}
		</dl>

		<!-- Lineage Section (if derived image) -->
		{#if image.parent_image_id}
			<div class="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs space-y-2">
				<div class="flex items-center justify-between font-medium text-foreground">
					<span class="text-primary font-medium">
						Lineage & Parent Image
					</span>
					<a
						href="/dashboard/images/{image.parent_image_id}"
						class="inline-flex items-center gap-1 text-primary hover:underline font-mono text-[11px]"
					>
						<span>View Original</span>
						<ArrowUpRightIcon class="size-3" />
					</a>
				</div>

				{#if image.transformation_params}
					<div class="mt-2 pt-2 border-t border-primary/10">
						<div class="text-[11px] font-medium text-muted-foreground mb-1">
							Applied Transformations
						</div>
						<pre class="bg-background/80 p-2 rounded border border-border/40 font-mono text-[11px] text-foreground overflow-x-auto max-h-32">
{JSON.stringify(image.transformation_params, null, 2)}
						</pre>
					</div>
				{/if}
			</div>
		{/if}
	</Card.Content>
</Card.Root>
