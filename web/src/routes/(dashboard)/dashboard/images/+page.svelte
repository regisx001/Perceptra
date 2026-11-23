<script lang="ts">
	import { onMount } from "svelte";
	import * as m from "#lib/paraglide/messages.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Input } from "#lib/components/ui/input/index.js";
	import * as AlertDialog from "#lib/components/ui/alert-dialog/index.js";
	import * as Dialog from "#lib/components/ui/dialog/index.js";
	import * as DropdownMenu from "#lib/components/ui/dropdown-menu/index.js";
	import { Skeleton } from "#lib/components/ui/skeleton/index.js";
	import { imageService, type ImageItem } from "#lib/images.js";
	import { categoryService, type CategoryItem } from "#lib/categories.js";
	import HeaderActionPortal from "#lib/components/header-action-portal.svelte";
	import BatchActionBar from "#lib/components/batch-action-bar.svelte";
	import SearchIcon from "@lucide/svelte/icons/search";
	import ImageIcon from "@lucide/svelte/icons/image";
	import PlusIcon from "@lucide/svelte/icons/plus";
	import Trash2Icon from "@lucide/svelte/icons/trash-2";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import FolderIcon from "@lucide/svelte/icons/folder";
	import FolderInputIcon from "@lucide/svelte/icons/folder-input";
	import RefreshCwIcon from "@lucide/svelte/icons/refresh-cw";
	import Wand2Icon from "@lucide/svelte/icons/wand-2";
	import PencilIcon from "@lucide/svelte/icons/pencil";
	import HeartIcon from "@lucide/svelte/icons/heart";
	import CheckIcon from "@lucide/svelte/icons/check";
	import MoreHorizontalIcon from "@lucide/svelte/icons/more-horizontal";

	interface GalleryImage {
		id: string;
		filename: string;
		url: string;
		categoryId?: string | null;
		fileSize?: number;
		mimeType?: string;
		dimensions?: string;
		width?: number;
		height?: number;
		aspectRatio: number;
		isFavorite?: boolean;
	}

	const PAGE_SIZE = 25;
	let images = $state<GalleryImage[]>([]);
	let categories = $state<CategoryItem[]>([]);
	let categoryMap = $state<Record<string, string>>({});
	let selectedCategoryFilter = $state<string>("all");
	let showFavoritesOnly = $state(false);
	let searchQuery = $state("");
	let currentPage = $state(1);
	let totalPages = $state(1);
	let totalImages = $state(0);
	let isLoading = $state(false);
	let isLoadingMore = $state(false);
	let loadMoreTriggerRef = $state<HTMLElement | null>(null);

	// Photo row height preference (Google Photos justified layout)
	let targetRowHeight = $state<number>(210);

	function setRowHeight(height: number) {
		targetRowHeight = height;
		try {
			localStorage.setItem("perceptra_gallery_row_height", String(height));
		} catch {}
	}

	// Deletion state
	let isDeleteDialogOpen = $state(false);
	let imageToDelete = $state<GalleryImage | null>(null);
	let isDeleting = $state(false);

	// Batch selection state (Google Photos style)
	let selectedIds = $state<Set<string>>(new Set());
	let isMoveDialogOpen = $state(false);
	let isBulkDeleteDialogOpen = $state(false);
	let targetCollectionId = $state<string>("uncategorized");
	let isBatchProcessing = $state(false);
	let batchError = $state<string | null>(null);

	const selectedCount = $derived(selectedIds.size);

	function toggleSelect(id: string, e?: MouseEvent) {
		if (e) {
			e.preventDefault();
			e.stopPropagation();
		}
		const next = new Set(selectedIds);
		if (next.has(id)) {
			next.delete(id);
		} else {
			next.add(id);
		}
		selectedIds = next;
	}

	function selectAll() {
		const next = new Set(selectedIds);
		for (const img of filteredImages) {
			next.add(img.id);
		}
		selectedIds = next;
	}

	function clearSelection() {
		selectedIds = new Set();
	}

	function handleImageClick(img: GalleryImage, e: MouseEvent) {
		if (selectedIds.size > 0) {
			e.preventDefault();
			toggleSelect(img.id);
		}
	}

	$effect(() => {
		function onKeyDown(e: KeyboardEvent) {
			if (e.key === "Escape" && selectedIds.size > 0) {
				clearSelection();
			}
		}
		window.addEventListener("keydown", onKeyDown);
		return () => window.removeEventListener("keydown", onKeyDown);
	});

	function promptBulkMove() {
		if (selectedIds.size === 0) return;
		targetCollectionId = "uncategorized";
		batchError = null;
		isMoveDialogOpen = true;
	}

	async function confirmBulkMove() {
		if (selectedIds.size === 0) return;
		try {
			isBatchProcessing = true;
			batchError = null;
			const categoryId = targetCollectionId === "uncategorized" ? null : targetCollectionId;
			const idsArray = Array.from(selectedIds);
			await imageService.bulkAssign(idsArray, categoryId);

			images = images.map((img) => {
				if (selectedIds.has(img.id)) {
					return { ...img, categoryId };
				}
				return img;
			});

			isMoveDialogOpen = false;
			clearSelection();
		} catch (err: any) {
			console.error("Bulk move failed:", err.message);
			batchError = err.message || "Failed to move images to collection";
		} finally {
			isBatchProcessing = false;
		}
	}

	function promptBulkDelete() {
		if (selectedIds.size === 0) return;
		isBulkDeleteDialogOpen = true;
	}

	async function confirmBulkDelete() {
		if (selectedIds.size === 0) return;
		try {
			isBatchProcessing = true;
			const idsArray = Array.from(selectedIds);
			await imageService.bulkDelete(idsArray);

			images = images.filter((img) => !selectedIds.has(img.id));
			totalImages = Math.max(0, totalImages - idsArray.length);

			isBulkDeleteDialogOpen = false;
			clearSelection();
		} catch (err: any) {
			console.error("Bulk delete failed:", err.message);
		} finally {
			isBatchProcessing = false;
		}
	}

	async function loadCategories() {
		try {
			const res = await categoryService.getCategories({ tree: false });
			categories = res;
			const map: Record<string, string> = {};
			for (const c of res) {
				map[c.id] = c.name;
			}
			categoryMap = map;
		} catch (err: any) {
			console.warn("Could not load categories map:", err.message);
		}
	}

	async function fetchImages(reset = true) {
		try {
			if (reset) {
				isLoading = true;
				currentPage = 1;
				images = [];
			} else {
				isLoadingMore = true;
			}

			const targetPage = reset ? 1 : currentPage + 1;
			const isUncategorized = selectedCategoryFilter === "uncategorized";
			const catId =
				selectedCategoryFilter !== "all" && !isUncategorized
					? selectedCategoryFilter
					: undefined;

			const res = await imageService.listImages({
				category_id: catId,
				uncategorized: isUncategorized ? true : undefined,
				favorites: showFavoritesOnly ? true : undefined,
				page: targetPage,
				per_page: PAGE_SIZE
			});

			const mapped: GalleryImage[] = res.images.map((img) => {
				const w = img.width && img.width > 0 ? img.width : 400;
				const h = img.height && img.height > 0 ? img.height : 300;
				const ratio = Number((w / h).toFixed(3));
				return {
					id: img.id,
					filename: img.filename,
					url: imageService.getImageFileUrl(img.id),
					categoryId: img.category_id,
					fileSize: img.file_size,
					mimeType: img.mime_type,
					dimensions: img.width && img.height ? `${img.width}x${img.height}` : undefined,
					width: img.width || undefined,
					height: img.height || undefined,
					aspectRatio: ratio > 0 ? ratio : 1.333,
					isFavorite: img.is_favorite ?? false,
				};
			});

			if (reset) {
				images = mapped;
			} else {
				images = [...images, ...mapped];
			}

			currentPage = res.pagination.page;
			totalPages = res.pagination.pages;
			totalImages = res.pagination.total;
		} catch (err: any) {
			console.warn("Failed to fetch gallery images:", err.message);
			if (reset) images = [];
		} finally {
			isLoading = false;
			isLoadingMore = false;
		}
	}

	async function loadMore() {
		if (isLoading || isLoadingMore || currentPage >= totalPages) return;
		await fetchImages(false);
	}

	async function toggleFavorite(img: GalleryImage, e: MouseEvent) {
		e.preventDefault();
		e.stopPropagation();
		try {
			const res = await imageService.toggleFavorite(img.id);
			img.isFavorite = res.is_favorite;
			if (showFavoritesOnly && !res.is_favorite) {
				images = images.filter((i) => i.id !== img.id);
				totalImages = Math.max(0, totalImages - 1);
			}
		} catch (err: any) {
			console.error("Toggle favorite failed:", err.message);
		}
	}

	function promptDelete(img: GalleryImage, e: MouseEvent) {
		e.stopPropagation();
		imageToDelete = img;
		isDeleteDialogOpen = true;
	}

	async function confirmDelete() {
		if (!imageToDelete) return;
		try {
			isDeleting = true;
			await imageService.deleteImage(imageToDelete.id);
			images = images.filter((i) => i.id !== imageToDelete?.id);
			totalImages = Math.max(0, totalImages - 1);
		} catch (err: any) {
			console.error("Delete failed:", err.message);
		} finally {
			isDeleting = false;
			isDeleteDialogOpen = false;
			imageToDelete = null;
		}
	}

	// Infinite scroll intersection observer
	$effect(() => {
		if (!loadMoreTriggerRef) return;
		const observer = new IntersectionObserver(
			(entries) => {
				const first = entries[0];
				if (first.isIntersecting && !isLoading && !isLoadingMore && currentPage < totalPages) {
					loadMore();
				}
			},
			{ rootMargin: "250px" }
		);

		observer.observe(loadMoreTriggerRef);
		return () => {
			observer.disconnect();
		};
	});

	// Refetch when category filter changes
	$effect(() => {
		if (selectedCategoryFilter) {
			fetchImages(true);
		}
	});

	onMount(async () => {
		try {
			const savedHeight = localStorage.getItem("perceptra_gallery_row_height");
			if (savedHeight) {
				const parsed = Number(savedHeight);
				if ([160, 210, 270].includes(parsed) || (parsed >= 120 && parsed <= 400)) {
					targetRowHeight = parsed;
				}
			}
		} catch {}

		await loadCategories();
		await fetchImages(true);
	});

	let filteredImages = $derived(
		searchQuery.trim() === ""
			? images
			: images.filter((img) =>
					img.filename.toLowerCase().includes(searchQuery.toLowerCase())
				)
	);

	const allVisibleSelected = $derived(
		filteredImages.length > 0 && filteredImages.every((img) => selectedIds.has(img.id))
	);
</script>

<svelte:head>
	<title>{m.images_title()} - Perceptra</title>
</svelte:head>

<HeaderActionPortal>
	<div class="flex items-center gap-2">
		<!-- Search Bar -->
		<div class="relative w-44 sm:w-52 md:w-64">
			<SearchIcon class="size-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
			<Input
				placeholder={m.images_search_placeholder()}
				bind:value={searchQuery}
				class="pl-8 text-xs bg-background/50 h-8 rounded-md"
			/>
		</div>

		<!-- Category Dropdown Filter -->
		<div class="flex items-center">
			<select
				id="category-filter-select"
				bind:value={selectedCategoryFilter}
				onchange={() => fetchImages(true)}
				class="h-8 rounded-md border border-input bg-background/80 px-2.5 text-xs text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
				aria-label="Category filter"
			>
				<option value="all">{m.images_filter_all()}</option>
				<option value="uncategorized">{m.categories_uncategorized_label()}</option>
				{#each categories as cat (cat.id)}
					<option value={cat.id}>{cat.name}</option>
				{/each}
			</select>
		</div>

		<!-- Favorites Filter Toggle Button -->
		<Button
			variant={showFavoritesOnly ? "default" : "outline"}
			size="sm"
			class="h-8 gap-1.5 px-2.5 text-xs shadow-2xs font-semibold"
			onclick={() => {
				showFavoritesOnly = !showFavoritesOnly;
				fetchImages(true);
			}}
			title="Filter by favorites"
		>
			<HeartIcon class="size-3.5 {showFavoritesOnly ? 'fill-current' : ''}" />
			<span class="hidden sm:inline">Favorites</span>
		</Button>

		<!-- Refresh Button -->
		<Button
			variant="outline"
			size="sm"
			class="h-8 gap-1.5 px-2.5 text-xs shadow-2xs font-semibold"
			onclick={() => fetchImages(true)}
			title={m.images_refresh_tooltip()}
		>
			<RefreshCwIcon class="size-3.5 {isLoading ? 'animate-spin' : ''}" />
			<span class="hidden sm:inline">{m.images_refresh()}</span>
		</Button>

		<!-- Upload Images CTA -->
		<Button
			href="/dashboard/upload"
			size="sm"
			class="h-8 gap-1.5 px-3 text-xs font-semibold shadow-xs"
		>
			<PlusIcon class="size-3.5" />
			<span class="hidden sm:inline">{m.upload_title()}</span>
		</Button>
	</div>
</HeaderActionPortal>

<div class="flex flex-1 flex-col">
	<div class="@container/main flex flex-1 flex-col gap-2">
		<!-- Top Welcome & Page Header Bar -->
		<div class="flex flex-col gap-2 px-4 pt-5 sm:flex-row sm:items-center sm:justify-between lg:px-6">
			<div>
				<div class="flex items-baseline gap-2.5">
					<h1 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">{m.images_title()}</h1>
					<span class="font-mono text-xs text-muted-foreground font-medium">
						{m.images_total_counter({ count: totalImages })}
					</span>
				</div>
				<p class="text-xs text-muted-foreground sm:text-sm">
					{m.images_subtitle()}
				</p>
			</div>

			<!-- Photo Row Height / Density Selector -->
			<div class="flex items-center gap-2 pt-2 sm:pt-0">
				<label for="gallery-size-select" class="text-xs text-muted-foreground font-medium shrink-0">Size:</label>
				<select
					id="gallery-size-select"
					value={targetRowHeight}
					onchange={(e) => setRowHeight(Number(e.currentTarget.value))}
					class="h-8 rounded-md border border-input bg-background/80 px-2.5 text-xs text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring cursor-pointer"
					aria-label="Photo size"
				>
					<option value={160}>Compact (160px)</option>
					<option value={210}>Normal (210px)</option>
					<option value={270}>Large (270px)</option>
				</select>
			</div>
		</div>

		<!-- Dashboard Core Analytics & Controls -->
		<div class="flex flex-col gap-4 px-4 py-4 md:gap-6 md:py-6 lg:px-6">

	<!-- Images Grid -->
	{#if isLoading}
			<!-- Loading Skeleton (Justified rows) -->
			<div class="flex flex-wrap gap-2.5 sm:gap-3">
				{#each [1.33, 0.75, 1.77, 1.0, 1.5, 0.8, 1.33, 1.6] as ratio, i}
					<Skeleton
						class="rounded-xl"
						style="
							height: {targetRowHeight}px;
							flex-grow: {ratio};
							flex-basis: calc({ratio} * {targetRowHeight}px);
						"
					/>
				{/each}
				<div class="grow-[99999] h-0 pointer-events-none" style="flex-basis: {targetRowHeight}px;"></div>
			</div>
		{:else if filteredImages.length === 0}
			<!-- Empty State -->
			<div class="flex flex-col items-center justify-center p-16 text-center text-muted-foreground rounded-lg border border-dashed border-border/70 bg-muted/10">
				<div class="mb-3 rounded-full bg-muted/60 p-3 text-muted-foreground/80">
					<ImageIcon class="size-8 stroke-1" />
				</div>
				<p class="text-base font-semibold text-foreground">
					{m.images_empty_title()}
				</p>
				<p class="text-xs mt-1 max-w-sm text-muted-foreground">
					{m.images_empty_desc()}
				</p>
				<Button
					href="/dashboard/upload"
					variant="outline"
					size="sm"
					class="mt-4 gap-1.5 text-xs shadow-2xs"
				>
					<PlusIcon class="size-3.5" />
					<span>{m.upload_title()}</span>
				</Button>
			</div>
		{:else}
			<!-- Render Justified Images Flex Row (Google Photos layout) -->
			<div class="flex flex-wrap gap-2.5 sm:gap-3">
				{#each filteredImages as img (img.id)}
					<a
						href="/dashboard/images/{img.id}"
						class="group relative block overflow-hidden rounded-xl border border-border/80 bg-muted/40 shadow-2xs hover:shadow-md transition-all text-left {selectedIds.has(img.id)
							? 'ring-3 ring-blue-500 ring-offset-2 ring-offset-background border-transparent scale-[0.96]'
							: 'hover:border-primary/50'}"
						style="
							height: {targetRowHeight}px;
							flex-grow: {img.aspectRatio};
							flex-basis: calc({img.aspectRatio} * {targetRowHeight}px);
							max-width: 100%;
						"
						title={img.filename}
						onclick={(e) => handleImageClick(img, e)}
					>
						<!-- Top-Left Check Circle Button (Google Photos style) -->
						<button
							type="button"
							class="absolute top-2.5 left-2.5 z-20 size-6 sm:size-6.5 rounded-full flex items-center justify-center transition-all cursor-pointer {selectedIds.has(img.id)
								? 'bg-blue-600 text-white shadow-md ring-2 ring-white/50 opacity-100 scale-105'
								: selectedIds.size > 0
									? 'border-2 border-white/85 bg-black/35 hover:bg-black/60 hover:border-white shadow-xs opacity-100'
									: 'border-2 border-white/85 bg-black/35 hover:bg-black/60 hover:border-white shadow-xs opacity-0 group-hover:opacity-100'}"
							onclick={(e) => toggleSelect(img.id, e)}
							title={selectedIds.has(img.id) ? "Deselect image" : "Select image"}
							aria-label={selectedIds.has(img.id) ? "Deselect image" : "Select image"}
						>
							{#if selectedIds.has(img.id)}
								<CheckIcon class="size-3.5 stroke-[3]" />
							{/if}
						</button>

						<!-- Image Thumbnail with fallback -->
						<img
							src={img.url}
							alt={img.filename}
							class="size-full object-cover transition-transform"
							loading="lazy"
							onerror={(e) => {
								const target = e.currentTarget as HTMLImageElement;
								target.style.display = 'none';
								target.nextElementSibling?.classList.remove('hidden');
							}}
						/>
						<div class="hidden absolute inset-0 flex flex-col items-center justify-center p-2 text-center text-muted-foreground bg-muted/60">
							<ImageIcon class="size-6 opacity-40 mb-1" />
							<span class="text-[10px] truncate max-w-full font-mono">{img.filename}</span>
						</div>

						<!-- Floating Action Button: 3 horizontal dots overflow menu (hidden during multi-select) -->
						{#if selectedIds.size === 0}
							<div class="absolute top-2.5 right-2.5 flex items-center gap-1.5 z-10">
								{#if img.isFavorite}
									<span
										class="size-7 sm:size-7.5 rounded-full bg-black/60 text-rose-500 flex items-center justify-center backdrop-blur-md shadow-xs pointer-events-none"
										title="Favorited"
									>
										<HeartIcon class="size-3.5 fill-current" />
									</span>
								{/if}

								<DropdownMenu.Root>
									<DropdownMenu.Trigger
										class="size-7 sm:size-7.5 rounded-full bg-black/60 hover:bg-black/85 text-white/90 hover:text-white flex items-center justify-center opacity-90 sm:opacity-0 sm:group-hover:opacity-100 data-[state=open]:opacity-100 transition-all backdrop-blur-md shadow-xs cursor-pointer"
										title="Image actions"
										aria-label="Image actions"
										onclick={(e: MouseEvent) => {
											e.preventDefault();
											e.stopPropagation();
										}}
									>
										<MoreHorizontalIcon class="size-4" />
									</DropdownMenu.Trigger>
									<DropdownMenu.Content align="end" class="w-44 z-50">
										<DropdownMenu.Item
											class="gap-2.5 text-xs cursor-pointer"
											onclick={(e: MouseEvent) => {
												e.preventDefault();
												e.stopPropagation();
												window.location.href = `/dashboard/transform?image_id=${img.id}`;
											}}
										>
											<PencilIcon class="size-3.5 text-muted-foreground" />
											<span>Edit in Studio</span>
										</DropdownMenu.Item>
										<DropdownMenu.Item
											class="gap-2.5 text-xs cursor-pointer"
											onclick={(e: MouseEvent) => {
												e.preventDefault();
												e.stopPropagation();
												toggleFavorite(img, e);
											}}
										>
											<HeartIcon
												class="size-3.5 {img.isFavorite
													? 'fill-current text-rose-500'
													: 'text-muted-foreground'}"
											/>
											<span>{img.isFavorite ? "Remove from Favorites" : "Add to Favorites"}</span>
										</DropdownMenu.Item>
										<DropdownMenu.Separator />
										<DropdownMenu.Item
											variant="destructive"
											class="gap-2.5 text-xs cursor-pointer"
											onclick={(e: MouseEvent) => {
												e.preventDefault();
												e.stopPropagation();
												promptDelete(img, e);
											}}
										>
											<Trash2Icon class="size-3.5" />
											<span>Delete Image</span>
										</DropdownMenu.Item>
									</DropdownMenu.Content>
								</DropdownMenu.Root>
							</div>
						{/if}
					</a>
				{/each}
				<!-- Spacer absorbing remaining space on the last row so images maintain natural width -->
				<div class="grow-[99999] h-0 pointer-events-none" style="flex-basis: {targetRowHeight}px;"></div>
			</div>

			<!-- Infinite Scroll Trigger / Load More -->
			{#if currentPage < totalPages}
				<div
					bind:this={loadMoreTriggerRef}
					class="pt-8 pb-2 flex flex-col items-center justify-center gap-2"
				>
					<Button
						variant="outline"
						size="sm"
						class="gap-2 text-xs font-semibold px-4 shadow-2xs hover:bg-muted"
						onclick={loadMore}
						disabled={isLoadingMore}
					>
						{#if isLoadingMore}
							<Loader2Icon class="size-3.5 animate-spin" />
							<span>{m.categories_loading_more()}</span>
						{:else}
							<PlusIcon class="size-3.5" />
							<span>{m.categories_load_more()}</span>
						{/if}
					</Button>
					<span class="text-[11px] text-muted-foreground font-mono">
						{filteredImages.length} / {totalImages} images
					</span>
				</div>
			{:else if filteredImages.length > PAGE_SIZE}
				<div class="pt-8 pb-2 text-center text-[11px] text-muted-foreground font-mono">
					{m.categories_all_loaded({ total: totalImages })}
				</div>
			{/if}
		{/if}
</div>
</div>
</div>

<!-- Delete Image Confirmation Modal -->
<AlertDialog.Root bind:open={isDeleteDialogOpen}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Delete Image?</AlertDialog.Title>
			<AlertDialog.Description>
				Are you sure you want to permanently delete "{imageToDelete?.filename}"? This action removes the file and its associated index descriptors.
			</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel onclick={() => { isDeleteDialogOpen = false; imageToDelete = null; }}>
				Cancel
			</AlertDialog.Cancel>
			<AlertDialog.Action
				variant="destructive"
				onclick={confirmDelete}
				disabled={isDeleting}
			>
				{#if isDeleting}
					<Loader2Icon class="size-3.5 animate-spin mr-1" />
				{/if}
				Delete Image
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>

<!-- Move to Collection Modal -->
<Dialog.Root bind:open={isMoveDialogOpen}>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2">
				<FolderInputIcon class="size-5 text-primary" />
				<span>Move to Collection</span>
			</Dialog.Title>
			<Dialog.Description>
				Select the destination collection for {selectedCount} {selectedCount === 1 ? 'image' : 'images'}.
			</Dialog.Description>
		</Dialog.Header>

		<div class="py-3 space-y-3">
			{#if batchError}
				<div class="p-3 text-xs rounded-md bg-destructive/10 text-destructive border border-destructive/20">
					{batchError}
				</div>
			{/if}

			<div class="space-y-1.5">
				<label for="move-collection-select" class="text-xs font-semibold text-foreground">
					Target Collection / Category
				</label>
				<select
					id="move-collection-select"
					bind:value={targetCollectionId}
					class="w-full h-9 rounded-md border border-input bg-background px-3 text-xs text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring cursor-pointer"
				>
					<option value="uncategorized">None (Uncategorized)</option>
					{#each categories as cat (cat.id)}
						<option value={cat.id}>{cat.name}</option>
					{/each}
				</select>
			</div>
		</div>

		<Dialog.Footer class="gap-2 sm:gap-0">
			<Button
				variant="outline"
				size="sm"
				onclick={() => { isMoveDialogOpen = false; }}
				disabled={isBatchProcessing}
			>
				Cancel
			</Button>
			<Button
				variant="default"
				size="sm"
				onclick={confirmBulkMove}
				disabled={isBatchProcessing}
				class="gap-1.5 cursor-pointer font-semibold"
			>
				{#if isBatchProcessing}
					<Loader2Icon class="size-3.5 animate-spin" />
				{/if}
				<span>Move Images</span>
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Bulk Delete Images Confirmation Modal -->
<AlertDialog.Root bind:open={isBulkDeleteDialogOpen}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Delete {selectedCount} Images?</AlertDialog.Title>
			<AlertDialog.Description>
				Are you sure you want to permanently delete {selectedCount} {selectedCount === 1 ? 'image' : 'images'}? This action cannot be undone and will remove the files and their feature descriptors.
			</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel onclick={() => { isBulkDeleteDialogOpen = false; }}>
				Cancel
			</AlertDialog.Cancel>
			<AlertDialog.Action
				variant="destructive"
				onclick={confirmBulkDelete}
				disabled={isBatchProcessing}
			>
				{#if isBatchProcessing}
					<Loader2Icon class="size-3.5 animate-spin mr-1" />
				{/if}
				Delete {selectedCount} Images
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>

<!-- Floating Google Photos Batch Actions Dock -->
<BatchActionBar
	selectedCount={selectedCount}
	totalCount={filteredImages.length}
	allSelected={allVisibleSelected}
	onSelectAll={selectAll}
	onDeselectAll={clearSelection}
	onMove={promptBulkMove}
	onDelete={promptBulkDelete}
/>
