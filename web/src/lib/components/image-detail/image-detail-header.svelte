<script lang="ts">
	import { imageService, type ImageItem } from "#lib/images.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as AlertDialog from "#lib/components/ui/alert-dialog/index.js";
	import HeaderActionPortal from "#lib/components/header-action-portal.svelte";
	import * as m from "#lib/paraglide/messages.js";
	import DownloadIcon from "@lucide/svelte/icons/download";
	import Trash2Icon from "@lucide/svelte/icons/trash-2";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import HeartIcon from "@lucide/svelte/icons/heart";

	let {
		image,
		categoryName = "Uncategorized",
		isExtracting = false,
		onExtract,
		onDelete
	}: {
		image: ImageItem;
		categoryName?: string;
		isExtracting?: boolean;
		onExtract: () => void;
		onDelete: () => Promise<void>;
	} = $props();

	let isDeleteDialogOpen = $state(false);
	let isDeleting = $state(false);
	let isTogglingFavorite = $state(false);

	async function handleToggleFavorite() {
		if (isTogglingFavorite) return;
		isTogglingFavorite = true;
		try {
			const res = await imageService.toggleFavorite(image.id);
			image.is_favorite = res.is_favorite;
		} catch (err: any) {
			console.error("Failed to toggle favorite:", err.message);
		} finally {
			isTogglingFavorite = false;
		}
	}

	async function confirmDelete() {
		isDeleting = true;
		try {
			await onDelete();
		} finally {
			isDeleting = false;
			isDeleteDialogOpen = false;
		}
	}
</script>

<!-- Portal Breadcrumbs and Action Toolbar into the Top SiteHeader -->
<HeaderActionPortal>
	{#snippet breadcrumb()}
		<nav class="flex items-center gap-2 text-xs text-muted-foreground min-w-0" aria-label="Breadcrumb">
			<a
				href="/dashboard"
				class="text-sm font-semibold tracking-tight text-foreground hover:text-primary transition-colors shrink-0"
			>
				Perceptra
			</a>

			<span class="text-xs text-muted-foreground/60 shrink-0">/</span>

			<a
				href="/dashboard/images"
				class="hover:text-foreground transition-colors shrink-0"
				title="Back to gallery"
			>
				<span>{m.nav_images()}</span>
			</a>

			<span class="text-xs text-muted-foreground/60 shrink-0">/</span>

			<span class="max-w-[80px] sm:max-w-[100px] md:max-w-[120px] truncate text-muted-foreground hidden md:inline" title={categoryName}>
				{categoryName}
			</span>

			<span class="text-xs text-muted-foreground/60 shrink-0 hidden md:inline">/</span>

			<span class="max-w-[110px] sm:max-w-[150px] md:max-w-[190px] lg:max-w-[240px] truncate font-medium text-foreground font-mono" title={image.filename}>
				{image.filename}
			</span>
		</nav>
	{/snippet}

	<div class="flex items-center gap-2 shrink-0">
		<!-- Search Similar -->
		<Button
			variant="default"
			size="sm"
			class="text-xs h-8 px-3 shadow-xs"
			href="/dashboard/query?image_id={image.id}"
		>
			<span>Search Similar</span>
		</Button>

		<!-- Favorite Toggle -->
		<Button
			variant={image.is_favorite ? "default" : "outline"}
			size="icon"
			class="size-8 border-border {image.is_favorite ? 'bg-rose-500 hover:bg-rose-600 text-white border-rose-500' : 'bg-background text-muted-foreground hover:text-foreground'}"
			title={image.is_favorite ? "Remove from Favorites" : "Add to Favorites"}
			onclick={handleToggleFavorite}
			disabled={isTogglingFavorite}
		>
			<HeartIcon class="size-3.5 {image.is_favorite ? 'fill-current' : ''}" />
		</Button>

		<!-- Transform Image -->
		<Button
			variant="outline"
			size="sm"
			class="text-xs h-8 px-3 border-border bg-background hover:bg-muted/50"
			href="/dashboard/transform?image_id={image.id}"
		>
			<span>Transform</span>
		</Button>

		<!-- Extract / Recompute Descriptors -->
		<Button
			variant="outline"
			size="sm"
			disabled={isExtracting}
			onclick={onExtract}
			class="gap-1.5 text-xs h-8 px-3 border-border bg-background hover:bg-muted/50"
			title="Recompute all visual descriptors"
		>
			{#if isExtracting}
				<Loader2Icon class="size-3.5 animate-spin" />
				<span>Extracting…</span>
			{:else}
				<span>Recompute</span>
			{/if}
		</Button>

		<!-- Download Image -->
		<Button
			variant="outline"
			size="icon"
			class="size-8 border-border bg-background text-muted-foreground hover:text-foreground"
			title="Download original file"
			href={imageService.getImageUrl(image.id, true)}
			download={image.filename}
		>
			<DownloadIcon class="size-3.5" />
		</Button>

		<!-- Delete Image -->
		<Button
			variant="outline"
			size="icon"
			class="size-8 border-border bg-background text-muted-foreground hover:bg-destructive/10 hover:text-destructive hover:border-destructive/30"
			title="Delete image"
			onclick={() => (isDeleteDialogOpen = true)}
		>
			<Trash2Icon class="size-3.5" />
		</Button>
	</div>
</HeaderActionPortal>

<!-- Delete Confirmation Dialog -->
<AlertDialog.Root bind:open={isDeleteDialogOpen}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Delete this image?</AlertDialog.Title>
			<AlertDialog.Description>
				Are you sure you want to permanently delete <strong class="text-foreground">{image.filename}</strong>?
				This will remove the file from storage along with all extracted visual descriptors and derived variations. This action cannot be undone.
			</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel disabled={isDeleting} onclick={() => (isDeleteDialogOpen = false)}>
				Cancel
			</AlertDialog.Cancel>
			<AlertDialog.Action
				class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
				disabled={isDeleting}
				onclick={confirmDelete}
			>
				{#if isDeleting}
					<Loader2Icon class="size-4 animate-spin mr-1.5" />
					Deleting…
				{:else}
					Delete Image
				{/if}
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
