<script lang="ts">
	import { onMount } from "svelte";
	import * as m from "#lib/paraglide/messages.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Input } from "#lib/components/ui/input/index.js";
	import * as AlertDialog from "#lib/components/ui/alert-dialog/index.js";
	import { Skeleton } from "#lib/components/ui/skeleton/index.js";
	import { imageService, type ImageItem } from "#lib/images.js";
	import { categoryService, type CategoryItem } from "#lib/categories.js";
	import HeaderActionPortal from "#lib/components/header-action-portal.svelte";
	import SearchIcon from "@lucide/svelte/icons/search";
	import ImageIcon from "@lucide/svelte/icons/image";
	import PlusIcon from "@lucide/svelte/icons/plus";
	import Trash2Icon from "@lucide/svelte/icons/trash-2";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import FolderIcon from "@lucide/svelte/icons/folder";
	import RefreshCwIcon from "@lucide/svelte/icons/refresh-cw";
	import Wand2Icon from "@lucide/svelte/icons/wand-2";

	interface GalleryImage {
		id: string;
		filename: string;
		url: string;
		categoryId?: string | null;
		fileSize?: number;
		mimeType?: string;
		dimensions?: string;
	}

	const PAGE_SIZE = 25;
	let images = $state<GalleryImage[]>([]);
	let categories = $state<CategoryItem[]>([]);
	let categoryMap = $state<Record<string, string>>({});
	let selectedCategoryFilter = $state<string>("all");
	let searchQuery = $state("");
	let currentPage = $state(1);
	let totalPages = $state(1);
	let totalImages = $state(0);
	let isLoading = $state(false);
	let isLoadingMore = $state(false);
	let loadMoreTriggerRef = $state<HTMLElement | null>(null);

	// Deletion state
	let isDeleteDialogOpen = $state(false);
	let imageToDelete = $state<GalleryImage | null>(null);
	let isDeleting = $state(false);

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
				page: targetPage,
				per_page: PAGE_SIZE
			});

			const mapped: GalleryImage[] = res.images.map((img) => ({
				id: img.id,
				filename: img.filename,
				url: imageService.getImageFileUrl(img.id),
				categoryId: img.category_id,
				fileSize: img.file_size,
				mimeType: img.mime_type,
				dimensions: img.width && img.height ? `${img.width}x${img.height}` : undefined
			}));

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
				<div class="flex items-center gap-2.5">
					<h1 class="text-xl font-bold tracking-tight text-foreground sm:text-2xl">{m.images_title()}</h1>
					<span class="inline-flex items-center font-mono text-xs px-2.5 py-0.5 rounded-full bg-secondary border border-border/80 text-secondary-foreground font-medium">
						{m.images_total_counter({ count: totalImages })}
					</span>
				</div>
				<p class="text-xs text-muted-foreground sm:text-sm">
					{m.images_subtitle()}
				</p>
			</div>
		</div>

		<!-- Dashboard Core Analytics & Controls -->
		<div class="flex flex-col gap-4 px-4 py-4 md:gap-6 md:py-6 lg:px-6">

	<!-- Images Grid -->
	<Card.Root class="border border-border/80 bg-card/60 backdrop-blur-xs shadow-xs p-5 sm:p-6">
		{#if isLoading}
			<!-- Loading Skeleton (2 rows of 5) -->
			<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4.5 sm:gap-5">
				{#each Array(10) as _, i}
					<div class="flex flex-col rounded-lg border border-border/60 overflow-hidden shadow-2xs">
						<Skeleton class="aspect-4/3 w-full" />
						<div class="p-2.5 space-y-1 bg-background/60">
							<Skeleton class="h-3 w-3/4 rounded-xs" />
						</div>
					</div>
				{/each}
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
			<!-- Render Image Cards: 5 images per row on desktop -->
			<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4.5 sm:gap-5">
				{#each filteredImages as img (img.id)}
					<a
						href="/dashboard/images/{img.id}"
						class="group relative flex flex-col rounded-lg border border-border/70 bg-card overflow-hidden shadow-2xs hover:shadow-xs hover:border-primary/40 transition-all text-left"
					>
						<!-- Image Thumbnail with fallback -->
						<div class="aspect-4/3 w-full overflow-hidden bg-muted relative">
							<img
								src={img.url}
								alt={img.filename}
								class="size-full object-cover group-hover:scale-105 transition-transform duration-300"
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

							<!-- Floating Action Buttons -->
							<button
								type="button"
								class="absolute top-2 left-2 size-7 rounded-md bg-background/85 hover:bg-primary hover:text-primary-foreground text-muted-foreground flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-xs shadow-2xs cursor-pointer z-10"
								title="Transform in Studio"
								onclick={(e) => {
									e.preventDefault();
									e.stopPropagation();
									window.location.href = `/dashboard/transform?image_id=${img.id}`;
								}}
							>
								<Wand2Icon class="size-3.5" />
							</button>

							<!-- Floating Delete Button -->
							<button
								type="button"
								class="absolute top-2 right-2 size-7 rounded-md bg-background/85 hover:bg-destructive hover:text-destructive-foreground text-muted-foreground flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-xs shadow-2xs cursor-pointer z-10"
								onclick={(e) => promptDelete(img, e)}
								title="Delete Image"
							>
								<Trash2Icon class="size-3.5" />
							</button>
						</div>

						<!-- Card Details -->
						<div class="p-2.5 bg-background/80 backdrop-blur-xs flex flex-col gap-1">
							<p class="truncate text-xs font-semibold text-foreground group-hover:text-primary transition-colors" title={img.filename}>
								{img.filename}
							</p>
							<div class="flex items-center justify-between text-[11px] text-muted-foreground">
								<span class="truncate max-w-[120px]">
									{img.categoryId && categoryMap[img.categoryId]
										? categoryMap[img.categoryId]
										: "Uncategorized"}
								</span>
								{#if img.dimensions}
									<span class="font-mono text-[10px] opacity-80">{img.dimensions}</span>
								{/if}
							</div>
						</div>
					</a>
				{/each}
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
	</Card.Root>
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
