<script lang="ts">
	import { onMount } from "svelte";
	import { goto } from "$app/navigation";
	import type { PageData } from "./$types";
	import { imageService, type ImageItem, type DescriptorsMap } from "#lib/images.js";
	import { categoryService, type CategoryItem } from "#lib/categories.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Skeleton } from "#lib/components/ui/skeleton/index.js";
	import ImageDetailHeader from "#lib/components/image-detail/image-detail-header.svelte";
	import ImagePreviewCard from "#lib/components/image-detail/image-preview-card.svelte";
	import ImageMetadataCard from "#lib/components/image-detail/image-metadata-card.svelte";
	import DerivedVersionsCard from "#lib/components/image-detail/derived-versions-card.svelte";
	import UnindexedEmptyState from "#lib/components/image-detail/unindexed-empty-state.svelte";
	import DominantColorsCard from "#lib/components/image-detail/dominant-colors-card.svelte";
	import ColorHistogramCard from "#lib/components/image-detail/color-histogram-card.svelte";
	import ColorMomentsCard from "#lib/components/image-detail/color-moments-card.svelte";
	import GlcmTextureCard from "#lib/components/image-detail/glcm-texture-card.svelte";
	import LbpHistogramCard from "#lib/components/image-detail/lbp-histogram-card.svelte";

	// Icons
	import PaletteIcon from "@lucide/svelte/icons/palette";
	import GridIcon from "@lucide/svelte/icons/grid";
	import AlertCircleIcon from "@lucide/svelte/icons/alert-circle";
	import ArrowLeftIcon from "@lucide/svelte/icons/arrow-left";

	let { data }: { data: PageData } = $props();

	let image = $state<ImageItem | null>(null);
	let descriptors = $state<DescriptorsMap>({});
	let derivatives = $state<ImageItem[]>([]);
	let categories = $state<CategoryItem[]>([]);
	let activeTab = $state<"color" | "texture">("color");

	let isLoading = $state(true);
	let isExtracting = $state(false);
	let error = $state<string | null>(null);

	const categoryMap = $derived.by(() => {
		const map: Record<string, string> = {};
		for (const c of categories) {
			map[c.id] = c.name;
		}
		return map;
	});

	const currentCategoryName = $derived.by(() => {
		if (!image?.category_id) return "Uncategorized";
		return categoryMap[image.category_id] || "Uncategorized";
	});

	const hasDescriptors = $derived.by(() => {
		return Object.keys(descriptors).length > 0;
	});

	async function loadAllData() {
		isLoading = true;
		error = null;

		try {
			const [imgResult, descResult, derivResult, catResult] = await Promise.allSettled([
				imageService.getImage(data.id),
				imageService.getImageDescriptors(data.id),
				imageService.getDerivatives(data.id),
				categoryService.getCategories({ tree: false })
			]);

			if (imgResult.status === "fulfilled") {
				image = imgResult.value;
			} else {
				throw new Error(imgResult.reason?.message || "Failed to load image");
			}

			if (descResult.status === "fulfilled") {
				descriptors = descResult.value.descriptors || {};
			} else {
				descriptors = {};
			}

			if (derivResult.status === "fulfilled") {
				derivatives = derivResult.value || [];
			} else {
				derivatives = [];
			}

			if (catResult.status === "fulfilled") {
				categories = catResult.value || [];
			} else {
				categories = [];
			}
		} catch (err: any) {
			console.error("Error loading image detail:", err);
			error = err.message || "An unexpected error occurred while loading image details.";
		} finally {
			isLoading = false;
		}
	}

	async function handleExtract(force = true) {
		if (!image) return;
		isExtracting = true;
		try {
			const res = await imageService.extractDescriptors(image.id, { force });
			descriptors = res.descriptors || {};
			if (res.processing_status) {
				image.processing_status = res.processing_status;
			}
		} catch (err: any) {
			console.error("Error extracting descriptors:", err);
			alert(`Extraction failed: ${err.message || "Unknown error"}`);
		} finally {
			isExtracting = false;
		}
	}

	async function handleCategoryChange(newCategoryId: string | null) {
		if (!image) return;
		const updated = await imageService.updateImage(image.id, {
			category_id: newCategoryId
		});
		image.category_id = updated.category_id;
	}

	async function handleDelete() {
		if (!image) return;
		await imageService.deleteImage(image.id);
		await goto("/dashboard/images");
	}

	onMount(() => {
		loadAllData();
	});
</script>

<div class="flex min-h-full flex-col bg-background text-foreground">
	{#if isLoading}
		<div class="p-6 space-y-6">
			<div class="flex justify-between items-center">
				<Skeleton class="h-8 w-64" />
				<div class="flex gap-2">
					<Skeleton class="h-8 w-24" />
					<Skeleton class="h-8 w-24" />
				</div>
			</div>
			<div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
				<div class="lg:col-span-5 xl:col-span-4 space-y-6">
					<Skeleton class="h-[360px] w-full rounded-xl" />
					<Skeleton class="h-[240px] w-full rounded-xl" />
				</div>
				<div class="lg:col-span-7 xl:col-span-8 space-y-6">
					<Skeleton class="h-10 w-80 rounded-lg" />
					<Skeleton class="h-[200px] w-full rounded-xl" />
					<Skeleton class="h-[240px] w-full rounded-xl" />
				</div>
			</div>
		</div>
	{:else if error || !image}
		<div class="flex min-h-[60vh] flex-col items-center justify-center p-6 text-center">
			<div class="mb-4 flex size-14 items-center justify-center rounded-2xl bg-destructive/10 text-destructive ring-8 ring-destructive/5">
				<AlertCircleIcon class="size-7" />
			</div>
			<h2 class="text-xl font-semibold tracking-tight text-foreground">Failed to Load Image</h2>
			<p class="mt-2 text-sm text-muted-foreground max-w-md">
				{error || "The requested image could not be found or you do not have permission to view it."}
			</p>
			<Button variant="outline" class="mt-6 gap-2" href="/dashboard/images">
				<ArrowLeftIcon class="size-4" />
				Back to Gallery
			</Button>
		</div>
	{:else}
		<!-- Header with Breadcrumbs & Action Toolbar -->
		<ImageDetailHeader
			{image}
			categoryName={currentCategoryName}
			{isExtracting}
			onExtract={() => handleExtract(true)}
			onDelete={handleDelete}
		/>

		<!-- Two-Column Main Content Grid -->
		<div class="flex-1 p-6">
			<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
				<!-- Left Column (~40%): Visual Preview, Metadata, Lineage & Derivatives -->
				<div class="lg:col-span-5 xl:col-span-4 space-y-6">
					<!-- Preview Card with Lightbox -->
					<ImagePreviewCard
						{image}
						imageUrl={imageService.getImageUrl(image.id)}
					/>

					<!-- Metadata & Properties Card -->
					<ImageMetadataCard
						{image}
						{categories}
						onCategoryChange={handleCategoryChange}
					/>

					<!-- Derived Variations Card -->
					<DerivedVersionsCard
						{derivatives}
						parentImageId={image.id}
					/>
				</div>

				<!-- Right Column (~60%): Visual Descriptors & Feature Analysis -->
				<div class="lg:col-span-7 xl:col-span-8 space-y-6">
					<!-- Feature Navigation Strip -->
					<div class="flex items-center justify-between border-b border-border pb-3">
						<div class="flex items-center gap-1 rounded-lg bg-muted/50 p-1 border border-border/40">
							<button
								type="button"
								class="inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all {activeTab === 'color'
									? 'bg-background text-foreground shadow-xs'
									: 'text-muted-foreground hover:text-foreground'}"
								onclick={() => (activeTab = "color")}
							>
								<PaletteIcon class="size-3.5" />
								<span>Color Features</span>
								{#if hasDescriptors}
									<span class="ml-1 rounded-full bg-primary/10 px-1.5 py-0.2 text-[10px] font-mono text-primary">3</span>
								{/if}
							</button>

							<button
								type="button"
								class="inline-flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all {activeTab === 'texture'
									? 'bg-background text-foreground shadow-xs'
									: 'text-muted-foreground hover:text-foreground'}"
								onclick={() => (activeTab = "texture")}
							>
								<GridIcon class="size-3.5" />
								<span>Texture Features</span>
								{#if hasDescriptors}
									<span class="ml-1 rounded-full bg-primary/10 px-1.5 py-0.2 text-[10px] font-mono text-primary">2</span>
								{/if}
							</button>
						</div>

						{#if hasDescriptors}
							<div class="text-[11px] text-muted-foreground hidden sm:block">
								Standardized CBIR JSON Schemas
							</div>
						{/if}
					</div>

					<!-- Content based on extraction status -->
					{#if !hasDescriptors}
						<UnindexedEmptyState
							{isExtracting}
							onExtract={() => handleExtract(false)}
						/>
					{:else}
						<!-- Descriptors Display based on activeTab -->
						<div class="space-y-6">
							<!-- Color Descriptors -->
							{#if activeTab === "color"}
								{#if descriptors.dominant_colors}
									<DominantColorsCard data={descriptors.dominant_colors} />
								{/if}

								{#if descriptors.color_histogram}
									<ColorHistogramCard data={descriptors.color_histogram} />
								{/if}

								{#if descriptors.color_moments}
									<ColorMomentsCard data={descriptors.color_moments} />
								{/if}
							{:else if activeTab === "texture"}
								<!-- Texture Descriptors -->
								{#if descriptors.glcm}
									<GlcmTextureCard data={descriptors.glcm} />
								{/if}

								{#if descriptors.lbp_histogram}
									<LbpHistogramCard data={descriptors.lbp_histogram} />
								{/if}
							{/if}
						</div>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>
