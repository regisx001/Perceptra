<script lang="ts">
	import { onMount } from "svelte";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import * as Tabs from "#lib/components/ui/tabs/index.js";
	import * as Dialog from "#lib/components/ui/dialog/index.js";
	import HeaderActionPortal from "#lib/components/header-action-portal.svelte";
	import {
		queryEngineClient,
		type VisualQueryResultItem,
		type QueryConfigResponse,
		type ExecutionTimeBreakdown,
	} from "#lib/query.js";
	import { imageService, type ImageItem } from "#lib/images.js";
	import { categoryService, type CategoryItem } from "#lib/categories.js";

	// Tabler & Lucide Icons
	import SparklesIcon from "@tabler/icons-svelte/icons/sparkles";
	import AdjustmentsHorizontalIcon from "@tabler/icons-svelte/icons/adjustments-horizontal";
	import PhotoIcon from "@tabler/icons-svelte/icons/photo";
	import UploadIcon from "@tabler/icons-svelte/icons/upload";
	import RefreshDotIcon from "@tabler/icons-svelte/icons/refresh-dot";
	import ThumbsUpIcon from "@tabler/icons-svelte/icons/thumb-up";
	import ThumbsDownIcon from "@tabler/icons-svelte/icons/thumb-down";
	import EyeIcon from "@tabler/icons-svelte/icons/eye";
	import AlertCircleIcon from "@tabler/icons-svelte/icons/alert-circle";
	import XIcon from "@tabler/icons-svelte/icons/x";
	import SlidersIcon from "@tabler/icons-svelte/icons/adjustments";
	import CheckIcon from "@tabler/icons-svelte/icons/check";
	import TargetIcon from "@tabler/icons-svelte/icons/target";

	// State: Configuration & Categories
	let categories = $state<CategoryItem[]>([]);
	let queryConfig = $state<QueryConfigResponse | null>(null);

	// Tier 1: Basic Input Settings
	let querySourceType = $state<"upload" | "existing">("upload");
	let uploadedFile = $state<File | null>(null);
	let previewUrl = $state<string | null>(null);
	let selectedExistingImage = $state<ImageItem | null>(null);

	let searchScope = $state<string>("both");
	let selectedCategory = $state<string>("all");
	let topK = $state<number>(12);

	// Tier 2: Advanced Feature Extraction & Similarity
	let activeDescriptors = $state<Record<string, boolean>>({
		color_histogram: true,
		color_moments: true,
		dominant_colors: true,
		glcm: true,
		lbp_histogram: true,
	});
	let similarityMetric = $state<string>("cosine");
	let normalizationMethod = $state<string>("none");

	// Tier 3: Research & Relevance Feedback (Group 13)
	let activeWeights = $state<Record<string, number>>({});
	let sessionId = $state<string | null>(null);
	let currentIteration = $state<number>(0);
	let precisionAtK = $state<number | null>(null);

	// User Feedback Map: image_id -> 'relevant' | 'irrelevant'
	let feedbackMap = $state<Record<string, "relevant" | "irrelevant">>({});

	// Results & Execution State
	let isSearching = $state(false);
	let isSubmittingFeedback = $state(false);
	let errorMessage = $state<string | null>(null);
	let results = $state<VisualQueryResultItem[]>([]);
	let executionTiming = $state<ExecutionTimeBreakdown | null>(null);
	let totalCandidatesCount = $state<number>(0);

	// Modals
	let isGalleryPickerOpen = $state(false);
	let galleryImages = $state<ImageItem[]>([]);
	let isLoadingGallery = $state(false);

	let inspectionCandidate = $state<VisualQueryResultItem | null>(null);
	let isInspectionOpen = $state(false);

	// Derived
	const relevantCount = $derived(
		Object.values(feedbackMap).filter((v) => v === "relevant").length,
	);
	const irrelevantCount = $derived(
		Object.values(feedbackMap).filter((v) => v === "irrelevant").length,
	);

	onMount(async () => {
		try {
			const [catData, confData] = await Promise.all([
				categoryService.getCategories({ tree: false }),
				queryEngineClient.getConfig(),
			]);
			categories = catData;
			queryConfig = confData;

			// Init default weights
			const n = confData.supported_descriptors.length || 5;
			const initialW: Record<string, number> = {};
			for (const ft of confData.supported_descriptors) {
				initialW[ft] = Number((1.0 / n).toFixed(4));
			}
			activeWeights = initialW;
		} catch (err: any) {
			console.warn(
				"Failed to initialize query configuration:",
				err.message,
			);
		}
	});

	function handleFileSelected(e: Event) {
		const target = e.target as HTMLInputElement;
		if (target.files && target.files[0]) {
			const file = target.files[0];
			uploadedFile = file;
			if (previewUrl) URL.revokeObjectURL(previewUrl);
			previewUrl = URL.createObjectURL(file);
			selectedExistingImage = null;
			errorMessage = null;
		}
	}

	async function openGalleryPicker() {
		isGalleryPickerOpen = true;
		if (galleryImages.length === 0) {
			try {
				isLoadingGallery = true;
				const res = await imageService.listImages({ per_page: 50 });
				galleryImages = res.images || [];
			} catch (err: any) {
				console.error("Failed to load gallery images:", err);
			} finally {
				isLoadingGallery = false;
			}
		}
	}

	function selectGalleryImage(img: ImageItem) {
		selectedExistingImage = img;
		uploadedFile = null;
		if (previewUrl) {
			URL.revokeObjectURL(previewUrl);
			previewUrl = null;
		}
		isGalleryPickerOpen = false;
		errorMessage = null;
	}

	function clearQueryImage() {
		uploadedFile = null;
		selectedExistingImage = null;
		if (previewUrl) {
			URL.revokeObjectURL(previewUrl);
			previewUrl = null;
		}
	}

	function resetQuery() {
		clearQueryImage();
		results = [];
		sessionId = null;
		feedbackMap = {};
		currentIteration = 0;
		precisionAtK = null;
		executionTiming = null;
		errorMessage = null;
	}

	async function executeSearch() {
		if (
			querySourceType === "upload" &&
			!uploadedFile &&
			!previewUrl &&
			!selectedExistingImage
		) {
			errorMessage =
				"Please upload or select a reference image to run a visual query.";
			return;
		}
		if (querySourceType === "existing" && !selectedExistingImage) {
			errorMessage =
				"Please select an image from your library to run a visual query.";
			return;
		}

		errorMessage = null;
		isSearching = true;
		feedbackMap = {};
		currentIteration = 0;
		precisionAtK = null;

		const selectedDescList = Object.keys(activeDescriptors).filter(
			(k) => activeDescriptors[k],
		);
		if (selectedDescList.length === 0) {
			errorMessage =
				"At least one descriptor must be selected for visual retrieval.";
			isSearching = false;
			return;
		}

		try {
			const res = await queryEngineClient.search({
				file: uploadedFile || undefined,
				image_id: selectedExistingImage
					? selectedExistingImage.id
					: undefined,
				scope: searchScope,
				category_id:
					selectedCategory !== "all" ? selectedCategory : undefined,
				top_k: topK,
				metric: similarityMetric,
				normalization: normalizationMethod,
				descriptors: selectedDescList,
				weights: activeWeights,
			});

			results = res.results || [];
			sessionId = res.session_id;
			activeWeights = res.active_weights || activeWeights;
			executionTiming = res.execution_time_ms;
			totalCandidatesCount = res.total_candidates;
		} catch (err: any) {
			errorMessage = err.message || "Failed to execute visual query.";
		} finally {
			isSearching = false;
		}
	}

	function toggleFeedback(imageId: string, type: "relevant" | "irrelevant") {
		if (feedbackMap[imageId] === type) {
			const next = { ...feedbackMap };
			delete next[imageId];
			feedbackMap = next;
		} else {
			feedbackMap = { ...feedbackMap, [imageId]: type };
		}
	}

	async function submitRelevanceFeedback() {
		if (!sessionId) {
			errorMessage =
				"No active search session found. Please run a visual query first.";
			return;
		}

		const relevantIds = Object.keys(feedbackMap).filter(
			(id) => feedbackMap[id] === "relevant",
		);
		const irrelevantIds = Object.keys(feedbackMap).filter(
			(id) => feedbackMap[id] === "irrelevant",
		);

		if (relevantIds.length === 0 && irrelevantIds.length === 0) {
			errorMessage =
				"Please label at least one candidate image as Relevant (+) or Irrelevant (-) before submitting feedback.";
			return;
		}

		errorMessage = null;
		isSubmittingFeedback = true;

		try {
			const res = await queryEngineClient.feedback({
				session_id: sessionId,
				relevant_ids: relevantIds,
				irrelevant_ids: irrelevantIds,
				iteration: currentIteration + 1,
			});

			results = res.results || [];
			activeWeights = res.updated_weights || activeWeights;
			currentIteration = res.iteration;
			precisionAtK = res.precision_at_k;
			feedbackMap = {};
		} catch (err: any) {
			errorMessage =
				err.message || "Failed to submit relevance feedback.";
		} finally {
			isSubmittingFeedback = false;
		}
	}

	function openInspect(item: VisualQueryResultItem) {
		inspectionCandidate = item;
		isInspectionOpen = true;
	}

	function formatDescriptorName(key: string): string {
		switch (key) {
			case "color_histogram":
				return "Color Histogram";
			case "color_moments":
				return "Color Moments";
			case "dominant_colors":
				return "Dominant Colors";
			case "glcm":
				return "GLCM Texture";
			case "lbp_histogram":
				return "LBP Micro-patterns";
			default:
				return key.replace(/_/g, " ");
		}
	}
</script>

<svelte:head>
	<title>Visual Query - Perceptra</title>
</svelte:head>

<!-- Portal Actions into Top Site Header -->
<HeaderActionPortal>
	{#snippet breadcrumb()}
		<nav
			class="flex items-center gap-2 text-xs text-muted-foreground min-w-0"
			aria-label="Breadcrumb"
		>
			<a
				href="/dashboard"
				class="text-sm font-semibold tracking-tight text-foreground hover:text-primary transition-colors shrink-0"
			>
				Perceptra
			</a>
			<span class="text-xs text-muted-foreground/60 shrink-0">/</span>
			<span class="text-xs text-muted-foreground font-medium shrink-0"
				>Visual Query</span
			>
			{#if uploadedFile}
				<span class="text-xs text-muted-foreground/60 shrink-0">/</span>
				<span
					class="truncate max-w-[140px] sm:max-w-[200px] text-xs text-foreground font-mono font-medium"
					title={uploadedFile.name}
				>
					{uploadedFile.name}
				</span>
			{:else if selectedExistingImage}
				<span class="text-xs text-muted-foreground/60 shrink-0">/</span>
				<span
					class="truncate max-w-[140px] sm:max-w-[200px] text-xs text-foreground font-mono font-medium"
					title={selectedExistingImage.filename}
				>
					{selectedExistingImage.filename}
				</span>
			{/if}
		</nav>
	{/snippet}

	<div class="flex items-center gap-2">
		<Button
			variant="outline"
			size="sm"
			class="h-8 px-2.5 text-xs gap-1.5 shadow-2xs"
			onclick={resetQuery}
		>
			<RefreshDotIcon class="size-3.5" />
			<span>Reset</span>
		</Button>

		<Button
			variant="default"
			size="sm"
			class="h-8 px-3 text-xs font-semibold gap-1.5 shadow-xs"
			disabled={isSearching}
			onclick={executeSearch}
		>
			{#if isSearching}
				<div
					class="size-3 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin"
				></div>
				<span>Retrieving...</span>
			{:else}
				<SparklesIcon class="size-3.5" />
				<span>Execute Query</span>
			{/if}
		</Button>
	</div>
</HeaderActionPortal>

<div class="flex flex-1 flex-col overflow-y-auto">
	<div class="@container/main flex flex-1 flex-col gap-2">
		<!-- Top Welcome & Page Header Bar -->
		<div
			class="flex flex-col gap-2 px-4 pt-5 sm:flex-row sm:items-center sm:justify-between lg:px-6"
		>
			<div>
				<h1
					class="text-xl font-bold tracking-tight text-foreground sm:text-2xl"
				>
					Visual Query Studio
				</h1>
				<p class="text-xs text-muted-foreground sm:text-sm">
					Multi-descriptor content-based visual retrieval with
					interactive Feature Relevance Estimation.
				</p>
			</div>

			<!-- Status Chips -->
			<div class="flex items-center gap-2 pt-2 sm:pt-0">
				{#if executionTiming}
					<div
						class="flex items-center gap-1.5 font-mono text-2xs px-2.5 py-1 rounded-md bg-muted/60 border border-border text-muted-foreground"
					>
						<span class="text-foreground font-semibold"
							>{executionTiming.total_ms}ms total</span
						>
						<span class="text-muted-foreground/60">&bull;</span>
						<span>Ext: {executionTiming.extraction_ms}ms</span>
						<span class="text-muted-foreground/60">&bull;</span>
						<span>Sim: {executionTiming.similarity_ms}ms</span>
					</div>
				{/if}
				{#if currentIteration > 0}
					<Badge
						variant="secondary"
						class="font-mono text-xs text-emerald-600 dark:text-emerald-400"
					>
						Iteration #{currentIteration}
					</Badge>
				{/if}
			</div>
		</div>

		<!-- Dashboard Core Analytics & Controls -->
		<div class="flex flex-col gap-4 px-4 py-4 md:gap-6 md:py-6 lg:px-6">
			<!-- Error Alert -->
			{#if errorMessage}
				<div
					class="p-3.5 rounded-xl border border-destructive/30 bg-destructive/10 text-destructive text-xs flex items-center justify-between shadow-2xs"
				>
					<div class="flex items-center gap-2">
						<AlertCircleIcon class="size-4 shrink-0" />
						<span>{errorMessage}</span>
					</div>
					<button
						type="button"
						class="underline font-bold cursor-pointer"
						onclick={() => (errorMessage = null)}
					>
						Dismiss
					</button>
				</div>
			{/if}

			<!-- 2-COLUMN MAIN STUDIO WORKSPACE -->
			<div
				class="flex flex-col lg:flex-row gap-4 md:gap-6 items-start w-full"
			>
				<!-- ================================================================= -->
				<!-- COLUMN 1: QUERY & CONTROL STUDIO (Left Sidebar: Fixed Width)      -->
				<!-- ================================================================= -->
				<div
					class="w-full lg:w-[380px] xl:w-[400px] shrink-0 space-y-4"
				>
					<!-- CARD 1: REFERENCE QUERY IMAGE -->
					<Card.Root
						class="border-border/80 shadow-xs rounded-xl overflow-hidden bg-card"
					>
						<Card.Header
							class="p-3.5 border-b border-border/50 bg-muted/20 flex flex-row items-center justify-between"
						>
							<Card.Title
								class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5"
							>
								<TargetIcon class="size-3.5 text-primary" />
								<span>Reference Query Image</span>
							</Card.Title>

							{#if previewUrl || selectedExistingImage}
								<button
									type="button"
									class="text-2xs text-muted-foreground hover:text-destructive transition-colors flex items-center gap-1 cursor-pointer"
									onclick={clearQueryImage}
									title="Remove query image"
								>
									<XIcon class="size-3" />
									<span>Clear</span>
								</button>
							{/if}
						</Card.Header>

						<Card.Content class="p-4 space-y-3">
							<!-- Query Preview / Dropzone -->
							<div
								class="relative w-full aspect-4/3 rounded-lg border border-border bg-muted/30 overflow-hidden flex items-center justify-center"
							>
								{#if previewUrl}
									<img
										src={previewUrl}
										alt="Query Upload"
										class="w-full h-full object-contain p-1"
									/>
								{:else if selectedExistingImage}
									<img
										src={imageService.getImageFileUrl(
											selectedExistingImage.id,
										)}
										alt={selectedExistingImage.filename}
										class="w-full h-full object-contain p-1"
									/>
								{:else}
									<div
										class="flex flex-col items-center justify-center p-6 text-center w-full h-full"
									>
										<div
											class="size-10 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-2"
										>
											<UploadIcon class="size-5" />
										</div>
										<p
											class="text-xs font-semibold text-foreground"
										>
											No Query Image Selected
										</p>
										<p
											class="text-2xs text-muted-foreground mt-0.5 max-w-[200px]"
										>
											Upload a local image file or pick an
											indexed image from your library.
										</p>
									</div>
								{/if}
							</div>

							<!-- Image Source Buttons -->
							<div class="grid grid-cols-2 gap-2 pt-1">
								<label
									class="h-8.5 px-2.5 rounded-lg border border-border hover:bg-muted/70 text-xs font-medium flex items-center justify-center gap-1.5 transition-all cursor-pointer shadow-2xs"
								>
									<UploadIcon class="size-3.5 text-primary" />
									<span>Upload File</span>
									<input
										type="file"
										accept="image/jpeg,image/png,image/webp"
										class="hidden"
										onchange={handleFileSelected}
									/>
								</label>

								<Button
									variant="outline"
									size="sm"
									class="h-8.5 px-2.5 text-xs gap-1.5 shadow-2xs"
									onclick={openGalleryPicker}
								>
									<PhotoIcon class="size-3.5 text-primary" />
									<span>Pick Library</span>
								</Button>
							</div>

							<!-- Selected Image File Info -->
							{#if uploadedFile || selectedExistingImage}
								<div
									class="p-2.5 rounded-lg bg-muted/40 border border-border/70 text-2xs space-y-1"
								>
									<div
										class="flex justify-between items-center"
									>
										<span class="text-muted-foreground"
											>Filename:</span
										>
										<span
											class="font-semibold text-foreground truncate max-w-[190px]"
											title={uploadedFile
												? uploadedFile.name
												: selectedExistingImage?.filename}
										>
											{uploadedFile
												? uploadedFile.name
												: selectedExistingImage?.filename}
										</span>
									</div>
									{#if selectedExistingImage}
										<div
											class="flex justify-between items-center"
										>
											<span class="text-muted-foreground"
												>Category:</span
											>
											<span
												class="font-medium text-foreground"
												>{selectedExistingImage.category_id ||
													"Unassigned"}</span
											>
										</div>
										<div
											class="flex justify-between items-center"
										>
											<span class="text-muted-foreground"
												>Dimensions:</span
											>
											<span class="font-mono"
												>{selectedExistingImage.width} &times;
												{selectedExistingImage.height} px</span
											>
										</div>
									{/if}
								</div>
							{/if}
						</Card.Content>
					</Card.Root>

					<!-- CARD 2: RETRIEVAL CONFIGURATION (Basic & Advanced Tabs) -->
					<Card.Root
						class="border-border/80 shadow-xs rounded-xl overflow-hidden bg-card"
					>
						<Card.Header
							class="p-3.5 border-b border-border/50 bg-muted/20"
						>
							<Card.Title
								class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center justify-between"
							>
								<span>Retrieval Settings</span>
								<SlidersIcon class="size-3.5" />
							</Card.Title>
						</Card.Header>

						<Card.Content class="p-4 space-y-4">
							<Tabs.Root value="basic" class="w-full flex flex-col">
								<Tabs.List
									class="grid grid-cols-2 w-full h-8 mb-3 bg-muted/50 p-0.5 rounded-lg"
								>
									<Tabs.Trigger
										value="basic"
										class="text-xs font-semibold py-1"
										>Basic</Tabs.Trigger
									>
									<Tabs.Trigger
										value="advanced"
										class="text-xs font-semibold py-1"
										>Advanced</Tabs.Trigger
									>
								</Tabs.List>

								<!-- TAB 1: BASIC SETTINGS -->
								<Tabs.Content
									value="basic"
									class="space-y-3.5 focus-visible:outline-none"
								>
									<!-- Search Scope -->
									<div class="space-y-1.5">
										<label
											for="scope-selector"
											class="text-xs font-semibold text-foreground block"
										>
											Candidate Scope
										</label>
										<select
											id="scope-selector"
											bind:value={searchScope}
											class="w-full h-8.5 text-xs rounded-lg border border-border bg-background px-2.5 font-medium cursor-pointer focus:ring-1 focus:ring-primary"
										>
											<option value="both"
												>Both (GHIM-10K + My Uploads)</option
											>
											<option value="ghim10k"
												>GHIM-10K Reference Dataset Only</option
											>
											<option value="my_images"
												>My Uploaded Images Only</option
											>
										</select>
									</div>

									<!-- Category Filter -->
									<div class="space-y-1.5">
										<label
											for="cat-selector"
											class="text-xs font-semibold text-foreground block"
										>
											Category Filter
										</label>
										<select
											id="cat-selector"
											bind:value={selectedCategory}
											class="w-full h-8.5 text-xs rounded-lg border border-border bg-background px-2.5 font-medium cursor-pointer focus:ring-1 focus:ring-primary"
										>
											<option value="all"
												>All Categories (Unrestricted)</option
											>
											{#each categories as cat}
												<option value={cat.id}
													>{cat.name}</option
												>
											{/each}
										</select>
									</div>

									<!-- Top-K Results -->
									<div class="space-y-1.5 pt-1">
										<div
											class="flex items-center justify-between text-xs"
										>
											<span
												class="font-semibold text-foreground"
												>Top-K Returned</span
											>
											<span
												class="font-mono font-bold text-primary"
												>{topK} images</span
											>
										</div>
										<input
											type="range"
											min="4"
											max="50"
											step="2"
											bind:value={topK}
											class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
										/>
										<div
											class="flex justify-between text-[10px] text-muted-foreground font-mono"
										>
											<span>4</span>
											<span>12 (default)</span>
											<span>50</span>
										</div>
									</div>
								</Tabs.Content>

								<!-- TAB 2: ADVANCED SETTINGS -->
								<Tabs.Content
									value="advanced"
									class="space-y-3.5 focus-visible:outline-none"
								>
									<!-- Descriptors Selection -->
									<div class="space-y-1.5">
										<span
											class="text-xs font-semibold text-foreground block"
											>Active Descriptors</span
										>
										<div class="grid grid-cols-1 gap-1.5">
											<label
												class="flex items-center justify-between p-2 rounded-lg border border-border bg-card text-xs cursor-pointer hover:bg-muted/50"
											>
												<span class="font-medium"
													>Color Histogram (HSV 256)</span
												>
												<input
													type="checkbox"
													bind:checked={
														activeDescriptors.color_histogram
													}
													class="rounded accent-primary"
												/>
											</label>
											<label
												class="flex items-center justify-between p-2 rounded-lg border border-border bg-card text-xs cursor-pointer hover:bg-muted/50"
											>
												<span class="font-medium"
													>Color Moments (Mean, Std,
													Skew)</span
												>
												<input
													type="checkbox"
													bind:checked={
														activeDescriptors.color_moments
													}
													class="rounded accent-primary"
												/>
											</label>
											<label
												class="flex items-center justify-between p-2 rounded-lg border border-border bg-card text-xs cursor-pointer hover:bg-muted/50"
											>
												<span class="font-medium"
													>Dominant Colors (5
													Clusters)</span
												>
												<input
													type="checkbox"
													bind:checked={
														activeDescriptors.dominant_colors
													}
													class="rounded accent-primary"
												/>
											</label>
											<label
												class="flex items-center justify-between p-2 rounded-lg border border-border bg-card text-xs cursor-pointer hover:bg-muted/50"
											>
												<span class="font-medium"
													>GLCM Texture (4 Angles)</span
												>
												<input
													type="checkbox"
													bind:checked={
														activeDescriptors.glcm
													}
													class="rounded accent-primary"
												/>
											</label>
											<label
												class="flex items-center justify-between p-2 rounded-lg border border-border bg-card text-xs cursor-pointer hover:bg-muted/50"
											>
												<span class="font-medium"
													>LBP Texture (256-bin)</span
												>
												<input
													type="checkbox"
													bind:checked={
														activeDescriptors.lbp_histogram
													}
													class="rounded accent-primary"
												/>
											</label>
										</div>
									</div>

									<!-- Metric & Normalization -->
									<div
										class="space-y-2 pt-1 border-t border-border/60"
									>
										<div class="space-y-1">
											<label
												for="metric-selector"
												class="text-xs font-semibold text-foreground block"
												>Distance / Similarity Metric</label
											>
											<select
												id="metric-selector"
												bind:value={similarityMetric}
												class="w-full h-8 text-xs rounded-lg border border-border bg-background px-2 font-medium cursor-pointer"
											>
												<option value="cosine"
													>Cosine Similarity [0, 1]</option
												>
												<option value="euclidean"
													>Inverted Euclidean (1 / [1
													+ d])</option
												>
											</select>
										</div>

										<div class="space-y-1">
											<label
												for="norm-selector"
												class="text-xs font-semibold text-foreground block"
												>Vector Normalization</label
											>
											<select
												id="norm-selector"
												bind:value={normalizationMethod}
												class="w-full h-8 text-xs rounded-lg border border-border bg-background px-2 font-medium cursor-pointer"
											>
												<option value="none"
													>None (Raw Extracted Vector)</option
												>
												<option value="minmax"
													>Min-Max Normalization [0,
													1]</option
												>
												<option value="standard"
													>Standardization (Z-Score)</option
												>
											</select>
										</div>
									</div>
								</Tabs.Content>
							</Tabs.Root>
						</Card.Content>
					</Card.Root>
				</div>

				<!-- ================================================================= -->
				<!-- COLUMN 2: RETRIEVED NEAREST NEIGHBORS (Right Area: flex-1 full)   -->
				<!-- ================================================================= -->
				<div class="flex-1 min-w-0 w-full space-y-4">
					<Card.Root
						class="border-border/80 shadow-xs rounded-xl overflow-hidden bg-card min-h-[580px] flex flex-col"
					>
						<!-- Results Gallery Header & Relevance Feedback Bar -->
						<Card.Header
							class="p-3.5 sm:p-4 border-b border-border/50 bg-muted/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
						>
							<div class="flex items-center gap-2">
								<Card.Title
									class="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2"
								>
									<span>Retrieved Candidates</span>
									{#if results.length > 0}
										<Badge
											variant="outline"
											class="font-mono text-2xs font-bold"
										>
											{results.length} of {totalCandidatesCount}
											evaluated
										</Badge>
									{/if}
								</Card.Title>

								{#if precisionAtK !== null}
									<Badge
										variant="secondary"
										class="font-mono text-2xs text-emerald-600 dark:text-emerald-400"
									>
										Precision@{results.length}: {(
											precisionAtK * 100
										).toFixed(1)}%
									</Badge>
								{/if}
							</div>

							<!-- Relevance Feedback Submission Controls -->
							<div class="flex items-center gap-2">
								{#if relevantCount > 0 || irrelevantCount > 0}
									<div
										class="flex items-center gap-1.5 text-xs font-medium mr-1"
									>
										<span
											class="inline-flex items-center px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold text-2xs"
										>
											+{relevantCount} Rel
										</span>
										<span
											class="inline-flex items-center px-2 py-0.5 rounded bg-destructive/10 text-destructive font-bold text-2xs"
										>
											-{irrelevantCount} Irrel
										</span>
									</div>

									<Button
										variant="default"
										size="sm"
										class="h-7.5 px-3 text-xs font-semibold gap-1.5 shadow-xs bg-emerald-600 hover:bg-emerald-700 text-white"
										disabled={isSubmittingFeedback}
										onclick={submitRelevanceFeedback}
									>
										{#if isSubmittingFeedback}
											<div
												class="size-3 border-2 border-white border-t-transparent rounded-full animate-spin"
											></div>
											<span>Estimating...</span>
										{:else}
											<RefreshDotIcon class="size-3.5" />
											<span
												>Re-estimate &amp; Re-rank</span
											>
										{/if}
									</Button>
								{/if}
							</div>
						</Card.Header>

						<Card.Content
							class="p-4 sm:p-5 flex-1 flex flex-col justify-center"
						>
							{#if isSearching}
								<div
									class="flex flex-col items-center justify-center py-20 gap-3 text-muted-foreground"
								>
									<div
										class="size-8 border-3 border-primary border-t-transparent rounded-full animate-spin"
									></div>
									<p
										class="text-xs font-semibold text-foreground"
									>
										Computing multi-descriptor similarity...
									</p>
									<p class="text-2xs text-muted-foreground">
										Scanning candidate features &amp;
										calculating weighted distances
									</p>
								</div>
							{:else if results.length === 0}
								<div
									class="flex flex-col items-center justify-center py-20 text-center text-muted-foreground max-w-sm mx-auto space-y-3"
								>
									<div
										class="p-4 rounded-full bg-muted/60 border border-border"
									>
										<SparklesIcon
											class="size-8 text-primary/70"
										/>
									</div>
									<h3
										class="text-sm font-bold text-foreground"
									>
										Ready for Visual Query
									</h3>
									<p
										class="text-xs leading-relaxed text-muted-foreground"
									>
										Select or upload an image in the left
										panel, set your candidate scope, and
										click <strong>Execute Query</strong> to retrieve
										visual nearest neighbors.
									</p>
								</div>
							{:else}
								<!-- Ranked Results Grid: Responsive auto-filling columns -->
								<div
									class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-4"
								>
									{#each results as item (item.image_id)}
										{@const fb = feedbackMap[item.image_id]}
										{@const simPct = (
											item.overall_similarity * 100
										).toFixed(1)}
										{@const colorPct = (
											item.color_similarity * 100
										).toFixed(0)}
										{@const texturePct = (
											item.texture_similarity * 100
										).toFixed(0)}
										{@const isHighMatch =
											item.overall_similarity >= 0.8}

										<div
											class="relative rounded-xl border border-border/80 bg-card p-3 flex flex-col justify-between gap-2.5 transition-all hover:border-primary/50 shadow-2xs group {fb ===
											'relevant'
												? 'ring-2 ring-emerald-500 bg-emerald-500/5'
												: fb === 'irrelevant'
													? 'ring-2 ring-destructive/80 bg-destructive/5 opacity-70'
													: ''}"
										>
											<!-- Image Thumbnail with Badges -->
											<div
												class="relative w-full aspect-square rounded-lg overflow-hidden border border-border bg-muted/40"
											>
												<img
													src={imageService.getImageFileUrl(
														item.image_id,
													)}
													alt={item.filename}
													class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
													loading="lazy"
												/>

												<!-- Rank Badge -->
												<div
													class="absolute top-2 left-2 px-2 py-0.5 rounded-md bg-background/90 backdrop-blur-xs border border-border font-mono text-2xs font-bold text-foreground shadow-xs"
												>
													#{item.rank}
												</div>

												<!-- Similarity Score Badge with color scaling -->
												<div
													class="absolute top-2 right-2 px-2 py-0.5 rounded-md font-mono text-2xs font-bold shadow-xs text-white {isHighMatch
														? 'bg-emerald-600'
														: 'bg-primary'}"
												>
													{simPct}%
												</div>

												<!-- Quick Inspection Button -->
												<button
													type="button"
													class="absolute bottom-2 right-2 size-7 rounded-md bg-background/90 border border-border flex items-center justify-center text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer shadow-xs"
													onclick={() =>
														openInspect(item)}
													title="Inspect Side-by-Side Comparison"
												>
													<EyeIcon class="size-3.5" />
												</button>
											</div>

											<!-- Metadata & Family Scores -->
											<div class="space-y-1.5 pt-0.5">
												<div
													class="flex items-center justify-between text-xs"
												>
													<span
														class="font-bold text-foreground truncate max-w-[150px]"
														title={item.filename}
													>
														{item.filename}
													</span>
													<span
														class="text-2xs text-muted-foreground font-mono"
														>{item.dimensions}</span
													>
												</div>

												<!-- Family Breakdown Pills (Color & Texture) -->
												<div
													class="flex items-center justify-between text-2xs pt-0.5"
												>
													<div
														class="flex items-center gap-1.5"
													>
														<span
															class="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-600 dark:text-blue-400 font-mono font-semibold"
														>
															Color {colorPct}%
														</span>
														<span
															class="px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-600 dark:text-purple-400 font-mono font-semibold"
														>
															Texture {texturePct}%
														</span>
													</div>
													<span
														class="text-muted-foreground text-[11px] truncate max-w-[70px]"
														title={item.category}
													>
														{item.category}
													</span>
												</div>
											</div>

											<!-- Interactive Relevance Feedback Toggles -->
											<div
												class="pt-2 border-t border-border/60 grid grid-cols-2 gap-1.5"
											>
												<button
													type="button"
													class="h-7 px-2 rounded-md border text-2xs font-bold flex items-center justify-center gap-1 transition-all cursor-pointer {fb ===
													'relevant'
														? 'bg-emerald-600 text-white border-emerald-600 shadow-2xs'
														: 'border-border/80 hover:bg-emerald-500/10 hover:text-emerald-600 text-muted-foreground'}"
													onclick={() =>
														toggleFeedback(
															item.image_id,
															"relevant",
														)}
												>
													<ThumbsUpIcon
														class="size-3"
													/>
													<span>Relevant</span>
												</button>

												<button
													type="button"
													class="h-7 px-2 rounded-md border text-2xs font-bold flex items-center justify-center gap-1 transition-all cursor-pointer {fb ===
													'irrelevant'
														? 'bg-destructive text-white border-destructive shadow-2xs'
														: 'border-border/80 hover:bg-destructive/10 hover:text-destructive text-muted-foreground'}"
													onclick={() =>
														toggleFeedback(
															item.image_id,
															"irrelevant",
														)}
												>
													<ThumbsDownIcon
														class="size-3"
													/>
													<span>Irrelevant</span>
												</button>
											</div>
										</div>
									{/each}
								</div>
							{/if}
						</Card.Content>
					</Card.Root>
				</div>
			</div>
		</div>
	</div>
</div>

<!-- ========================================================================= -->
<!-- GALLERY PICKER MODAL                                                      -->
<!-- ========================================================================= -->
<Dialog.Root bind:open={isGalleryPickerOpen}>
	<Dialog.Content class="max-w-2xl p-5 max-h-[80vh] flex flex-col">
		<Dialog.Header class="pb-2">
			<Dialog.Title class="text-base font-bold text-foreground">
				Select Query Image from Library
			</Dialog.Title>
			<Dialog.Description class="text-xs text-muted-foreground">
				Choose an indexed image to serve as the reference query
				representation.
			</Dialog.Description>
		</Dialog.Header>

		<div class="flex-1 overflow-y-auto py-2">
			{#if isLoadingGallery}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-6 border-2 border-primary border-t-transparent rounded-full animate-spin"
					></div>
				</div>
			{:else if galleryImages.length === 0}
				<p class="text-xs text-center text-muted-foreground py-8">
					No images found in your gallery.
				</p>
			{:else}
				<div class="grid grid-cols-3 sm:grid-cols-4 gap-3">
					{#each galleryImages as img}
						<button
							type="button"
							class="group relative aspect-square rounded-lg border border-border overflow-hidden cursor-pointer hover:border-primary transition-all"
							onclick={() => selectGalleryImage(img)}
						>
							<img
								src={imageService.getImageFileUrl(img.id)}
								alt={img.filename}
								class="w-full h-full object-cover group-hover:scale-105 transition-transform"
							/>
							<div
								class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity text-white text-xs font-semibold"
							>
								Select
							</div>
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</Dialog.Content>
</Dialog.Root>

<!-- ========================================================================= -->
<!-- SIDE-BY-SIDE INSPECTION MODAL                                             -->
<!-- ========================================================================= -->
{#if inspectionCandidate}
	<Dialog.Root bind:open={isInspectionOpen}>
		<Dialog.Content class="max-w-2xl p-5">
			<Dialog.Header class="pb-2">
				<Dialog.Title
					class="text-base font-bold text-foreground flex items-center gap-2"
				>
					<span
						>Visual Similarity Inspection (Rank #{inspectionCandidate.rank})</span
					>
					<Badge variant="default" class="font-mono text-xs">
						{(inspectionCandidate.overall_similarity * 100).toFixed(
							1,
						)}% Match
					</Badge>
				</Dialog.Title>
				<Dialog.Description class="text-xs text-muted-foreground">
					Side-by-side descriptor comparison with candidate <strong
						>{inspectionCandidate.filename}</strong
					>.
				</Dialog.Description>
			</Dialog.Header>

			<div class="py-3 space-y-4">
				<!-- Side by Side Images -->
				<div class="grid grid-cols-2 gap-4">
					<div class="space-y-1.5 text-center">
						<span
							class="text-2xs font-bold uppercase tracking-wider text-muted-foreground"
							>Query Reference</span
						>
						<div
							class="aspect-4/3 rounded-lg border border-border bg-muted/40 overflow-hidden flex items-center justify-center"
						>
							{#if previewUrl}
								<img
									src={previewUrl}
									alt="Query"
									class="w-full h-full object-contain"
								/>
							{:else if selectedExistingImage}
								<img
									src={imageService.getImageFileUrl(
										selectedExistingImage.id,
									)}
									alt={selectedExistingImage.filename}
									class="w-full h-full object-contain"
								/>
							{/if}
						</div>
					</div>

					<div class="space-y-1.5 text-center">
						<span
							class="text-2xs font-bold uppercase tracking-wider text-muted-foreground"
							>Candidate #{inspectionCandidate.rank}</span
						>
						<div
							class="aspect-4/3 rounded-lg border border-border bg-muted/40 overflow-hidden flex items-center justify-center"
						>
							<img
								src={imageService.getImageFileUrl(
									inspectionCandidate.image_id,
								)}
								alt={inspectionCandidate.filename}
								class="w-full h-full object-contain"
							/>
						</div>
					</div>
				</div>

				<!-- Feature Breakdown Table -->
				<div class="space-y-2 pt-2 border-t border-border">
					<span class="text-xs font-semibold text-foreground"
						>Per-Descriptor Match Confidence</span
					>
					<div class="space-y-2">
						{#each Object.entries(inspectionCandidate.feature_scores) as [ft, score]}
							{@const pct = Math.round(score * 100)}
							<div class="space-y-1 text-xs">
								<div class="flex justify-between">
									<span
										class="text-muted-foreground font-medium"
										>{formatDescriptorName(ft)}</span
									>
									<span
										class="font-mono font-bold text-foreground"
										>{pct}%</span
									>
								</div>
								<div
									class="h-2 rounded-full bg-muted overflow-hidden"
								>
									<div
										class="h-full bg-primary rounded-full"
										style="width: {pct}%;"
									></div>
								</div>
							</div>
						{/each}
					</div>
				</div>
			</div>
		</Dialog.Content>
	</Dialog.Root>
{/if}
