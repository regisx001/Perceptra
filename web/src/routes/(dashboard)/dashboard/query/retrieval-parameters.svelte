<script lang="ts">
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Select from "#lib/components/ui/select/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Separator } from "#lib/components/ui/separator/index.js";
	import { Spinner } from "#lib/components/ui/spinner/index.js";
	import { Checkbox } from "#lib/components/ui/checkbox/index.js";
	import ChevronDownIcon from "@lucide/svelte/icons/chevron-down";
	import TriangleAlertIcon from "@lucide/svelte/icons/triangle-alert";
	import type { CategoryItem } from "#lib/categories.js";

	interface Props {
		isSettingsOpen?: boolean;
		selectedPreset?: "balanced" | "color" | "texture" | "custom";
		searchScope?: string;
		selectedCategory?: string;
		topK?: number;
		activeDescriptors?: Record<string, boolean>;
		activeWeights?: Record<string, number>;
		similarityMetric?: string;
		normalizationMethod?: string;
		categories?: CategoryItem[];
		isSearching?: boolean;
		onExecute?: () => void;
	}

	let {
		isSettingsOpen = $bindable(true),
		selectedPreset = $bindable("balanced"),
		searchScope = $bindable("both"),
		selectedCategory = $bindable("all"),
		topK = $bindable(12),
		activeDescriptors = $bindable({
			color_histogram: true,
			color_moments: true,
			dominant_colors: true,
			glcm: true,
			lbp_histogram: true,
		}),
		activeWeights = $bindable({
			color_histogram: 0.2,
			color_moments: 0.2,
			dominant_colors: 0.2,
			glcm: 0.2,
			lbp_histogram: 0.2,
		}),
		similarityMetric = $bindable("cosine"),
		normalizationMethod = $bindable("none"),
		categories = [],
		isSearching = false,
		onExecute,
	}: Props = $props();

	// Disclosures
	let isSlidersOpen = $state(true);
	let isAdvancedOpen = $state(false);

	// Features Definition
	interface FeatureMeta {
		id: string;
		name: string;
		shortName: string;
		group: "color" | "texture";
		color: string;
	}

	const FEATURES: FeatureMeta[] = [
		{
			id: "color_histogram",
			name: "Color Histogram (HSV)",
			shortName: "HSV",
			group: "color",
			color: "#2563EB",
		},
		{
			id: "color_moments",
			name: "Color Moments",
			shortName: "Moments",
			group: "color",
			color: "#0D9488",
		},
		{
			id: "dominant_colors",
			name: "Dominant Colors",
			shortName: "Dominant",
			group: "color",
			color: "#D97706",
		},
		{
			id: "glcm",
			name: "GLCM Texture",
			shortName: "GLCM",
			group: "texture",
			color: "#16A34A",
		},
		{
			id: "lbp_histogram",
			name: "LBP Texture",
			shortName: "LBP",
			group: "texture",
			color: "#7C3AED",
		},
	];

	const PRESET_CONFIGS: Record<
		"balanced" | "color" | "texture",
		Record<string, { enabled: boolean; weight: number }>
	> = {
		balanced: {
			color_histogram: { enabled: true, weight: 0.2 },
			color_moments: { enabled: true, weight: 0.2 },
			dominant_colors: { enabled: true, weight: 0.2 },
			glcm: { enabled: true, weight: 0.2 },
			lbp_histogram: { enabled: true, weight: 0.2 },
		},
		color: {
			color_histogram: { enabled: true, weight: 0.45 },
			color_moments: { enabled: true, weight: 0.2 },
			dominant_colors: { enabled: true, weight: 0.35 },
			glcm: { enabled: false, weight: 0.2 },
			lbp_histogram: { enabled: false, weight: 0.2 },
		},
		texture: {
			color_histogram: { enabled: false, weight: 0.2 },
			color_moments: { enabled: false, weight: 0.2 },
			dominant_colors: { enabled: false, weight: 0.2 },
			glcm: { enabled: true, weight: 0.55 },
			lbp_histogram: { enabled: true, weight: 0.45 },
		},
	};

	const PRESET_LABELS: Record<string, string> = {
		balanced: "Balanced",
		color: "Color Focus",
		texture: "Texture Focus",
		custom: "Custom",
	};

	const METRIC_LABELS: Record<string, string> = {
		cosine: "Cosine Similarity",
		euclidean: "Euclidean (L2)",
		manhattan: "Manhattan (L1)",
		chisquare: "Chi-Square",
	};

	const NORM_LABELS: Record<string, string> = {
		none: "Raw Vectors",
		l2: "L2 Normalized",
		minmax: "Min-Max [0, 1]",
		zscore: "Z-Score",
		standard: "Z-Score",
	};

	const SCOPE_LABELS: Record<string, string> = {
		both: "Dataset + Uploads",
		ghim10k: "GHIM-10K Only",
		my_images: "Uploads Only",
	};

	// Baseline snapshot for detecting modifications
	function captureSnapshot() {
		return JSON.stringify({
			selectedPreset,
			searchScope,
			selectedCategory,
			topK,
			similarityMetric,
			normalizationMethod,
			activeDescriptors,
			activeWeights,
		});
	}

	let baselineSnapshot = $state(captureSnapshot());
	const isModified = $derived(captureSnapshot() !== baselineSnapshot);

	// Derived Category Groupings
	const datasetCategories = $derived(categories.filter((c) => !c.user_id));
	const userCategories = $derived(categories.filter((c) => !!c.user_id));

	const selectedCategoryLabel = $derived.by(() => {
		if (selectedCategory === "all") return "All Categories";
		const found = categories.find((c) => c.id === selectedCategory);
		return found ? found.name : "Custom";
	});

	// Calculation & Distribution Pipeline
	const activeCount = $derived(
		FEATURES.filter((f) => !!activeDescriptors[f.id]).length,
	);

	const totalWeight = $derived.by(() => {
		let sum = 0;
		for (const f of FEATURES) {
			if (activeDescriptors[f.id]) {
				sum += Number(activeWeights[f.id]) || 0;
			}
		}
		return Math.round(sum * 100) / 100;
	});

	const isValid = $derived(activeCount > 0 && totalWeight > 0);

	const distribution = $derived.by(() => {
		const normalized: Record<string, number> = {};
		const percentages: Record<string, number> = {};

		for (const f of FEATURES) {
			const isEnabled = !!activeDescriptors[f.id];
			const w = Number(activeWeights[f.id]) || 0;
			if (isEnabled && totalWeight > 0) {
				const ratio = w / totalWeight;
				normalized[f.id] = ratio;
				percentages[f.id] = Math.round(ratio * 100);
			} else {
				normalized[f.id] = 0;
				percentages[f.id] = 0;
			}
		}

		if (totalWeight > 0) {
			const activeIds = FEATURES.filter(
				(f) =>
					activeDescriptors[f.id] &&
					(Number(activeWeights[f.id]) || 0) > 0,
			).map((f) => f.id);
			const sum = activeIds.reduce(
				(acc, id) => acc + (percentages[id] || 0),
				0,
			);
			const diff = 100 - sum;
			if (diff !== 0 && activeIds.length > 0) {
				activeIds.sort(
					(a, b) => (normalized[b] || 0) - (normalized[a] || 0),
				);
				percentages[activeIds[0]] =
					(percentages[activeIds[0]] || 0) + diff;
			}
		}

		return { normalized, percentages };
	});

	// Handlers
	function selectPreset(preset: "balanced" | "color" | "texture" | "custom") {
		selectedPreset = preset;
		if (preset === "custom") {
			isSlidersOpen = true;
			return;
		}

		const cfg = PRESET_CONFIGS[preset];
		const nextDescriptors: Record<string, boolean> = {};
		const nextWeights: Record<string, number> = {};

		for (const f of FEATURES) {
			nextDescriptors[f.id] = cfg[f.id].enabled;
			nextWeights[f.id] = cfg[f.id].weight;
		}

		activeDescriptors = nextDescriptors;
		activeWeights = nextWeights;
	}

	function handleWeightChange(id: string, rawVal: number) {
		selectedPreset = "custom";
		const clamped = Math.min(
			1,
			Math.max(0, Number.isFinite(rawVal) ? rawVal : 0),
		);
		activeWeights = {
			...activeWeights,
			[id]: Math.round(clamped * 100) / 100,
		};
	}

	function handleToggleDescriptor(id: string, checked: boolean) {
		selectedPreset = "custom";
		activeDescriptors = {
			...activeDescriptors,
			[id]: checked,
		};
	}

	function equalizeWeights() {
		const activeIds = FEATURES.filter((f) => activeDescriptors[f.id]).map(
			(f) => f.id,
		);
		if (activeIds.length === 0) {
			selectPreset("balanced");
			return;
		}

		const equalVal = Math.round((1.0 / activeIds.length) * 100) / 100;
		const nextWeights = { ...activeWeights };
		for (const id of activeIds) {
			nextWeights[id] = equalVal;
		}
		activeWeights = nextWeights;
		selectedPreset =
			activeIds.length === FEATURES.length ? "balanced" : "custom";
	}

	function resetDefaults() {
		selectPreset("balanced");
		searchScope = "both";
		selectedCategory = "all";
		topK = 12;
		similarityMetric = "cosine";
		normalizationMethod = "none";
		baselineSnapshot = captureSnapshot();
	}

	function handleExecute() {
		if (!isValid || isSearching) return;
		baselineSnapshot = captureSnapshot();
		onExecute?.();
	}
</script>

<Card.Root
	class="border-border/80 shadow-xs rounded-xl overflow-hidden bg-card transition-all duration-200"
>
	<!-- 1. Header Bar -->
	<header
		class="px-4 py-3 bg-muted/20 border-b border-border/50 flex flex-wrap items-center justify-between gap-3 cursor-pointer select-none hover:bg-muted/30 transition-colors"
		onclick={() => (isSettingsOpen = !isSettingsOpen)}
		role="button"
		tabindex="0"
		onkeydown={(e) => {
			if (e.key === "Enter" || e.key === " ") {
				isSettingsOpen = !isSettingsOpen;
				e.preventDefault();
			}
		}}
	>
		<div class="flex items-center gap-2.5 min-w-0">
			<span
				class="text-xs font-semibold uppercase tracking-wider text-foreground"
			>
				Retrieval Parameters
			</span>

			<!-- Modified Text Indicator
			{#if isModified}
				<span class="inline-flex items-center gap-1 text-2xs font-mono font-medium text-primary animate-in fade-in duration-150">
					<span class="size-1.5 rounded-full bg-primary"></span>
					Modified
				</span>
			{/if} -->

			<!-- Summary Chips (Visible when collapsed) -->
			{#if !isSettingsOpen}
				<div
					class="hidden sm:flex items-center gap-1.5 text-xs text-muted-foreground pl-1"
				>
					<span class="text-muted-foreground/40">&bull;</span>
					<span class="font-medium text-foreground">
						{PRESET_LABELS[selectedPreset] || "Custom"}
					</span>
					<span class="text-muted-foreground/40">&bull;</span>
					<span class="font-mono text-2xs">
						{SCOPE_LABELS[searchScope] || searchScope}
					</span>
					<span class="text-muted-foreground/40">&bull;</span>
					<span class="text-2xs truncate max-w-[120px]">
						{selectedCategoryLabel}
					</span>
					<span class="text-muted-foreground/40">&bull;</span>
					<span class="font-mono text-2xs font-semibold text-primary">
						Top {topK}
					</span>
				</div>
			{/if}
		</div>

		<!-- Collapse / Expand Toggle Button -->
		<Button
			variant="outline"
			size="sm"
			class="h-7.5 px-2.5 text-2xs font-medium gap-1.5 rounded-lg border-border/80 bg-background hover:bg-muted"
			onclick={(e) => {
				e.stopPropagation();
				isSettingsOpen = !isSettingsOpen;
			}}
		>
			<span>{isSettingsOpen ? "Collapse" : "Expand"}</span>
			<ChevronDownIcon
				class="size-3 transition-transform duration-200 {isSettingsOpen
					? 'rotate-180'
					: ''}"
			/>
		</Button>
	</header>

	<!-- Collapsible Content -->
	{#if isSettingsOpen}
		<Card.Content class="p-4 sm:p-5 flex flex-col gap-5">
			<!-- SECTION 1: RETRIEVAL PRESET (4 Clean Radio-Cards) -->
			<section
				class="flex flex-col gap-2.5"
				aria-labelledby="preset-heading"
			>
				<div
					class="flex items-baseline justify-between gap-2 flex-wrap"
				>
					<h3
						id="preset-heading"
						class="text-xs font-semibold text-foreground"
					>
						Retrieval Preset
					</h3>
					<span class="text-2xs text-muted-foreground">
						Select calibrated weights or customize descriptors below
					</span>
				</div>

				<div
					class="grid grid-cols-2 lg:grid-cols-4 gap-2.5"
					role="radiogroup"
					aria-labelledby="preset-heading"
				>
					<!-- Balanced -->
					<button
						type="button"
						role="radio"
						aria-checked={selectedPreset === "balanced"}
						class="p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-2 cursor-pointer select-none {selectedPreset ===
						'balanced'
							? 'border-primary bg-primary/5 ring-1 ring-primary/40 shadow-xs'
							: 'border-border/80 bg-card hover:bg-muted/40'}"
						onclick={() => selectPreset("balanced")}
					>
						<div class="flex items-center justify-between w-full">
							<span class="text-xs font-bold text-foreground"
								>Balanced</span
							>
							<span
								class="size-4 rounded-full border flex items-center justify-center transition-colors {selectedPreset ===
								'balanced'
									? 'border-primary bg-primary'
									: 'border-border/80'}"
							>
								{#if selectedPreset === "balanced"}
									<span
										class="size-1.5 rounded-full bg-primary-foreground"
									></span>
								{/if}
							</span>
						</div>
						<p class="text-2xs text-muted-foreground line-clamp-1">
							Equal color &amp; texture
						</p>
					</button>

					<!-- Color Focus -->
					<button
						type="button"
						role="radio"
						aria-checked={selectedPreset === "color"}
						class="p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-2 cursor-pointer select-none {selectedPreset ===
						'color'
							? 'border-primary bg-primary/5 ring-1 ring-primary/40 shadow-xs'
							: 'border-border/80 bg-card hover:bg-muted/40'}"
						onclick={() => selectPreset("color")}
					>
						<div class="flex items-center justify-between w-full">
							<span class="text-xs font-bold text-foreground"
								>Color Focus</span
							>
							<span
								class="size-4 rounded-full border flex items-center justify-center transition-colors {selectedPreset ===
								'color'
									? 'border-primary bg-primary'
									: 'border-border/80'}"
							>
								{#if selectedPreset === "color"}
									<span
										class="size-1.5 rounded-full bg-primary-foreground"
									></span>
								{/if}
							</span>
						</div>
						<p class="text-2xs text-muted-foreground line-clamp-1">
							Prioritize HSV &amp; palette
						</p>
					</button>

					<!-- Texture Focus -->
					<button
						type="button"
						role="radio"
						aria-checked={selectedPreset === "texture"}
						class="p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-2 cursor-pointer select-none {selectedPreset ===
						'texture'
							? 'border-primary bg-primary/5 ring-1 ring-primary/40 shadow-xs'
							: 'border-border/80 bg-card hover:bg-muted/40'}"
						onclick={() => selectPreset("texture")}
					>
						<div class="flex items-center justify-between w-full">
							<span class="text-xs font-bold text-foreground"
								>Texture Focus</span
							>
							<span
								class="size-4 rounded-full border flex items-center justify-center transition-colors {selectedPreset ===
								'texture'
									? 'border-primary bg-primary'
									: 'border-border/80'}"
							>
								{#if selectedPreset === "texture"}
									<span
										class="size-1.5 rounded-full bg-primary-foreground"
									></span>
								{/if}
							</span>
						</div>
						<p class="text-2xs text-muted-foreground line-clamp-1">
							Prioritize GLCM &amp; LBP
						</p>
					</button>

					<!-- Custom -->
					<button
						type="button"
						role="radio"
						aria-checked={selectedPreset === "custom"}
						class="p-3 rounded-xl border text-left transition-all flex flex-col justify-between gap-2 cursor-pointer select-none {selectedPreset ===
						'custom'
							? 'border-primary bg-primary/5 ring-1 ring-primary/40 shadow-xs'
							: 'border-border/80 bg-card hover:bg-muted/40'}"
						onclick={() => selectPreset("custom")}
					>
						<div class="flex items-center justify-between w-full">
							<span class="text-xs font-bold text-foreground"
								>Custom</span
							>
							<span
								class="size-4 rounded-full border flex items-center justify-center transition-colors {selectedPreset ===
								'custom'
									? 'border-primary bg-primary'
									: 'border-border/80'}"
							>
								{#if selectedPreset === "custom"}
									<span
										class="size-1.5 rounded-full bg-primary-foreground"
									></span>
								{/if}
							</span>
						</div>
						<p class="text-2xs text-muted-foreground line-clamp-1">
							Manual feature sliders
						</p>
					</button>
				</div>
			</section>

			<!-- SECTION 2: SEARCH SCOPE & RESULTS (3-Column Grid + Segmented Control) -->
			<section
				class="grid grid-cols-1 md:grid-cols-3 gap-3.5 items-end"
				aria-label="Search Scope and Results"
			>
				<!-- Candidate Scope -->
				<div class="flex flex-col gap-1.5">
					<h3 class="text-xs font-semibold text-foreground">
						Candidate Scope
					</h3>
					<Select.Root
						type="single"
						value={searchScope}
						onValueChange={(val) => {
							if (val) searchScope = val;
						}}
					>
						<Select.Trigger
							class="w-full h-8.5 text-xs font-medium border-border/80 bg-background px-2.5"
						>
							<span class="truncate">
								{#if searchScope === "both"}Both (GHIM-10K + My
									Uploads)
								{:else if searchScope === "ghim10k"}GHIM-10K
									Reference Dataset Only
								{:else}My Uploaded Images Only
								{/if}
							</span>
						</Select.Trigger>
						<Select.Content>
							<Select.Item value="both"
								>Both (GHIM-10K + My Uploads)</Select.Item
							>
							<Select.Item value="ghim10k"
								>GHIM-10K Reference Dataset Only</Select.Item
							>
							<Select.Item value="my_images"
								>My Uploaded Images Only</Select.Item
							>
						</Select.Content>
					</Select.Root>
				</div>

				<!-- Category Filter -->
				<div class="flex flex-col gap-1.5">
					<h3 class="text-xs font-semibold text-foreground">
						Category Filter
					</h3>
					<Select.Root
						type="single"
						value={selectedCategory}
						onValueChange={(val) => {
							if (val) selectedCategory = val;
						}}
					>
						<Select.Trigger
							class="w-full h-8.5 text-xs font-medium border-border/80 bg-background px-2.5"
						>
							<span class="truncate">
								{selectedCategory === "all"
									? "All Categories (Unrestricted)"
									: selectedCategoryLabel}
							</span>
						</Select.Trigger>
						<Select.Content class="max-h-60">
							<Select.Item value="all"
								>All Categories (Unrestricted)</Select.Item
							>
							{#if datasetCategories.length > 0}
								<Select.Separator />
								<Select.Group>
									<Select.GroupHeading
										class="text-2xs font-bold uppercase tracking-wider text-muted-foreground/80 px-2 py-1"
									>
										GHIM-10K Classes
									</Select.GroupHeading>
									{#each datasetCategories as cat (cat.id)}
										<Select.Item value={cat.id}
											>{cat.name}</Select.Item
										>
									{/each}
								</Select.Group>
							{/if}
							{#if userCategories.length > 0}
								<Select.Separator />
								<Select.Group>
									<Select.GroupHeading
										class="text-2xs font-bold uppercase tracking-wider text-muted-foreground/80 px-2 py-1"
									>
										My Categories
									</Select.GroupHeading>
									{#each userCategories as cat (cat.id)}
										<Select.Item value={cat.id}
											>{cat.name}</Select.Item
										>
									{/each}
								</Select.Group>
							{/if}
						</Select.Content>
					</Select.Root>
				</div>

				<!-- Results (Top-K) Segmented Control -->
				<div class="flex flex-col gap-1.5">
					<div class="flex items-center justify-between text-2xs">
						<h3 class="text-xs font-semibold text-foreground">
							Results (Top-K)
						</h3>
						<span class="font-mono text-primary font-bold">
							{topK} images
						</span>
					</div>
					<div
						class="grid grid-cols-4 gap-1 h-8.5 p-1 bg-muted/50 border border-border/80 rounded-lg"
						role="radiogroup"
						aria-label="Results count limit"
					>
						{#each [8, 12, 24, 48] as kVal}
							<button
								type="button"
								role="radio"
								aria-checked={topK === kVal}
								class="rounded-md text-xs font-mono font-medium transition-all flex items-center justify-center {topK ===
								kVal
									? 'bg-card text-primary font-bold shadow-2xs border border-border/40'
									: 'text-muted-foreground hover:text-foreground'}"
								onclick={() => (topK = kVal)}
							>
								{kVal}
							</button>
						{/each}
					</div>
				</div>
			</section>

			<Separator class="border-border/50" />

			<!-- SECTION 3: FEATURE RELEVANCE WEIGHTS -->
			<section
				class="flex flex-col gap-3"
				aria-labelledby="weights-heading"
			>
				<div class="flex items-center justify-between flex-wrap gap-2">
					<div class="flex items-center gap-2">
						<h3
							id="weights-heading"
							class="text-xs font-semibold text-foreground"
						>
							Feature Weights
						</h3>
						<span
							class="text-2xs font-mono {isValid
								? 'text-muted-foreground'
								: 'text-destructive font-semibold'}"
						>
							({activeCount}/{FEATURES.length} active)
						</span>
					</div>

					<div class="flex items-center gap-1.5">
						<Button
							variant="ghost"
							size="sm"
							class="h-7 px-2 text-2xs font-medium text-muted-foreground hover:text-foreground"
							onclick={equalizeWeights}
						>
							Equalize
						</Button>
						<Button
							variant="ghost"
							size="sm"
							class="h-7 px-2 text-2xs font-medium text-primary hover:text-primary/80 gap-1"
							onclick={() => (isSlidersOpen = !isSlidersOpen)}
						>
							<span
								>{isSlidersOpen
									? "Hide Sliders"
									: "Show Sliders"}</span
							>
							<ChevronDownIcon
								class="size-3 transition-transform duration-200 {isSlidersOpen
									? 'rotate-180'
									: ''}"
							/>
						</Button>
					</div>
				</div>

				<!-- Unified Proportional Distribution Track -->
				<div class="flex flex-col gap-1.5">
					<div
						class="w-full h-2 rounded-full overflow-hidden flex bg-muted/60 shadow-inner gap-0.5"
					>
						{#each FEATURES as feat (feat.id)}
							{#if activeDescriptors[feat.id] && distribution.normalized[feat.id] > 0}
								<div
									class="h-full transition-all duration-200 rounded-xs"
									style="width: {distribution.normalized[
										feat.id
									] * 100}%; background-color: {feat.color};"
									title="{feat.name}: {distribution
										.percentages[feat.id]}%"
								></div>
							{/if}
						{/each}
					</div>

					<!-- Distribution Legend -->
					<div
						class="flex flex-wrap items-center gap-x-3.5 gap-y-1 text-2xs text-muted-foreground pt-0.5"
					>
						{#each FEATURES as feat (feat.id)}
							{@const isEnabled = activeDescriptors[feat.id]}
							{@const pct =
								distribution.percentages[feat.id] || 0}
							<div
								class="inline-flex items-center gap-1.5 transition-opacity {isEnabled
									? 'opacity-100'
									: 'opacity-40'}"
							>
								<span
									class="size-2 rounded-full shrink-0"
									style="background-color: {feat.color};"
								></span>
								<span class="font-medium text-foreground"
									>{feat.shortName}:</span
								>
								<span
									class="font-mono tabular-nums text-muted-foreground"
									>{pct}%</span
								>
							</div>
						{/each}
					</div>
				</div>

				<!-- Validation Guardrail Warning -->
				{#if !isValid}
					<div
						class="flex items-center gap-2 p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/25 text-amber-700 dark:text-amber-400 text-xs font-medium"
						role="alert"
					>
						<TriangleAlertIcon
							class="size-4 shrink-0 text-amber-600 dark:text-amber-400"
						/>
						<span>
							{#if activeCount === 0}
								Enable at least one feature descriptor to
								execute visual query.
							{:else}
								Increase at least one active feature weight
								above 0.00.
							{/if}
						</span>
					</div>
				{/if}

				<!-- Collapsible Sliders Well (Flat 2-Column Group Layout) -->
				{#if isSlidersOpen}
					<div
						class="p-3.5 sm:p-4 rounded-xl bg-muted/30 border border-border/70 grid grid-cols-1 md:grid-cols-2 gap-4 lg:gap-6"
					>
						<!-- Group 1: Color Descriptors -->
						<div class="flex flex-col gap-2">
							<div
								class="text-2xs font-bold uppercase tracking-wider text-muted-foreground pb-1.5 border-b border-border/50"
							>
								Color Descriptors
							</div>
							<div class="flex flex-col gap-1.5">
								{#each FEATURES.filter((f) => f.group === "color") as feat (feat.id)}
									{@const isEnabled =
										!!activeDescriptors[feat.id]}
									{@const weight =
										Number(activeWeights[feat.id]) || 0}
									{@const pct =
										distribution.percentages[feat.id] || 0}
									<div
										class="grid grid-cols-[minmax(140px,1.2fr)_1fr_auto] items-center gap-2.5 py-1 px-1.5 rounded-lg hover:bg-muted/40 transition-colors {isEnabled
											? ''
											: 'opacity-40'}"
									>
										<!-- Checkbox & Label -->
										<label
											class="flex items-center gap-2 cursor-pointer select-none min-w-0"
											for="cb-{feat.id}"
										>
											<Checkbox
												id="cb-{feat.id}"
												checked={isEnabled}
												onCheckedChange={(checked) =>
													handleToggleDescriptor(
														feat.id,
														!!checked,
													)}
											/>
											<span
												class="size-2 rounded-full shrink-0"
												style="background-color: {feat.color};"
											></span>
											<span
												class="text-xs font-medium text-foreground truncate"
												title={feat.name}
											>
												{feat.name}
											</span>
										</label>

										<!-- Range Slider -->
										<div
											class="flex items-center min-w-0 px-1"
										>
											<input
												type="range"
												min="0"
												max="1"
												step="0.05"
												value={weight}
												disabled={!isEnabled}
												class="w-full h-1.5 bg-muted rounded-full cursor-pointer accent-primary disabled:cursor-not-allowed"
												style="accent-color: {feat.color};"
												oninput={(e) =>
													handleWeightChange(
														feat.id,
														parseFloat(
															(
																e.target as HTMLInputElement
															).value,
														),
													)}
											/>
										</div>

										<!-- Numeric Weight & Percentage Readout -->
										<div
											class="flex items-center gap-1.5 shrink-0"
										>
											<input
												type="number"
												min="0"
												max="1"
												step="0.05"
												value={weight.toFixed(2)}
												disabled={!isEnabled}
												class="w-13 h-6.5 text-right px-1 text-xs font-mono font-medium rounded-md border border-border/80 bg-background disabled:bg-transparent disabled:border-transparent text-foreground"
												onchange={(e) =>
													handleWeightChange(
														feat.id,
														parseFloat(
															(
																e.target as HTMLInputElement
															).value,
														),
													)}
											/>
											<span
												class="w-8 text-right font-mono text-xs tabular-nums text-muted-foreground font-medium"
											>
												{pct}%
											</span>
										</div>
									</div>
								{/each}
							</div>
						</div>

						<!-- Group 2: Texture Descriptors -->
						<div class="flex flex-col gap-2">
							<div
								class="text-2xs font-bold uppercase tracking-wider text-muted-foreground pb-1.5 border-b border-border/50"
							>
								Texture Descriptors
							</div>
							<div class="flex flex-col gap-1.5">
								{#each FEATURES.filter((f) => f.group === "texture") as feat (feat.id)}
									{@const isEnabled =
										!!activeDescriptors[feat.id]}
									{@const weight =
										Number(activeWeights[feat.id]) || 0}
									{@const pct =
										distribution.percentages[feat.id] || 0}
									<div
										class="grid grid-cols-[minmax(140px,1.2fr)_1fr_auto] items-center gap-2.5 py-1 px-1.5 rounded-lg hover:bg-muted/40 transition-colors {isEnabled
											? ''
											: 'opacity-40'}"
									>
										<!-- Checkbox & Label -->
										<label
											class="flex items-center gap-2 cursor-pointer select-none min-w-0"
											for="cb-{feat.id}"
										>
											<Checkbox
												id="cb-{feat.id}"
												checked={isEnabled}
												onCheckedChange={(checked) =>
													handleToggleDescriptor(
														feat.id,
														!!checked,
													)}
											/>
											<span
												class="size-2 rounded-full shrink-0"
												style="background-color: {feat.color};"
											></span>
											<span
												class="text-xs font-medium text-foreground truncate"
												title={feat.name}
											>
												{feat.name}
											</span>
										</label>

										<!-- Range Slider -->
										<div
											class="flex items-center min-w-0 px-1"
										>
											<input
												type="range"
												min="0"
												max="1"
												step="0.05"
												value={weight}
												disabled={!isEnabled}
												class="w-full h-1.5 bg-muted rounded-full cursor-pointer accent-primary disabled:cursor-not-allowed"
												style="accent-color: {feat.color};"
												oninput={(e) =>
													handleWeightChange(
														feat.id,
														parseFloat(
															(
																e.target as HTMLInputElement
															).value,
														),
													)}
											/>
										</div>

										<!-- Numeric Weight & Percentage Readout -->
										<div
											class="flex items-center gap-1.5 shrink-0"
										>
											<input
												type="number"
												min="0"
												max="1"
												step="0.05"
												value={weight.toFixed(2)}
												disabled={!isEnabled}
												class="w-13 h-6.5 text-right px-1 text-xs font-mono font-medium rounded-md border border-border/80 bg-background disabled:bg-transparent disabled:border-transparent text-foreground"
												onchange={(e) =>
													handleWeightChange(
														feat.id,
														parseFloat(
															(
																e.target as HTMLInputElement
															).value,
														),
													)}
											/>
											<span
												class="w-8 text-right font-mono text-xs tabular-nums text-muted-foreground font-medium"
											>
												{pct}%
											</span>
										</div>
									</div>
								{/each}
							</div>
						</div>
					</div>
				{/if}
			</section>

			<!-- SECTION 4: ADVANCED VECTOR SETTINGS (Decoupled Disclosure) -->
			<section
				class="rounded-xl border border-border/70 bg-card overflow-hidden"
				aria-labelledby="advanced-heading"
			>
				<button
					type="button"
					class="w-full flex items-center justify-between px-3.5 py-2.5 text-left hover:bg-muted/30 transition-colors cursor-pointer select-none"
					onclick={() => (isAdvancedOpen = !isAdvancedOpen)}
					aria-expanded={isAdvancedOpen}
				>
					<div class="flex items-center gap-2 min-w-0">
						<span
							id="advanced-heading"
							class="text-xs font-semibold text-foreground"
						>
							Advanced Vector Settings
						</span>
						<span
							class="text-2xs text-muted-foreground hidden sm:inline"
						>
							&bull; {METRIC_LABELS[similarityMetric] ||
								similarityMetric} &bull; {NORM_LABELS[
								normalizationMethod
							] || normalizationMethod}
						</span>
					</div>
					<ChevronDownIcon
						class="size-3.5 text-muted-foreground transition-transform duration-200 {isAdvancedOpen
							? 'rotate-180'
							: ''}"
					/>
				</button>

				{#if isAdvancedOpen}
					<div
						class="p-3.5 border-t border-border/50 bg-muted/10 grid grid-cols-1 sm:grid-cols-2 gap-3.5"
					>
						<!-- Similarity Metric -->
						<div class="flex flex-col gap-1.5">
							<h3 class="text-xs font-semibold text-foreground">
								Similarity Metric
							</h3>
							<Select.Root
								type="single"
								value={similarityMetric}
								onValueChange={(val) => {
									if (val) similarityMetric = val;
								}}
							>
								<Select.Trigger
									class="w-full h-8.5 text-xs font-medium border-border/80 bg-background px-2.5"
								>
									<span class="truncate"
										>{METRIC_LABELS[similarityMetric] ||
											similarityMetric}</span
									>
								</Select.Trigger>
								<Select.Content>
									<Select.Item value="cosine"
										>Cosine Similarity [0, 1]</Select.Item
									>
									<Select.Item value="euclidean"
										>Euclidean Distance (L2)</Select.Item
									>
									<Select.Item value="manhattan"
										>Manhattan Distance (L1)</Select.Item
									>
									<Select.Item value="chisquare"
										>Chi-Square Distance</Select.Item
									>
								</Select.Content>
							</Select.Root>
						</div>

						<!-- Vector Normalization -->
						<div class="flex flex-col gap-1.5">
							<h3 class="text-xs font-semibold text-foreground">
								Vector Normalization
							</h3>
							<Select.Root
								type="single"
								value={normalizationMethod}
								onValueChange={(val) => {
									if (val) normalizationMethod = val;
								}}
							>
								<Select.Trigger
									class="w-full h-8.5 text-xs font-medium border-border/80 bg-background px-2.5"
								>
									<span class="truncate"
										>{NORM_LABELS[normalizationMethod] ||
											normalizationMethod}</span
									>
								</Select.Trigger>
								<Select.Content>
									<Select.Item value="none"
										>None (Raw Vectors)</Select.Item
									>
									<Select.Item value="l2"
										>L2 Unit Normalization</Select.Item
									>
									<Select.Item value="minmax"
										>Min-Max Scaling [0, 1]</Select.Item
									>
									<Select.Item value="zscore"
										>Z-Score Standardization</Select.Item
									>
								</Select.Content>
							</Select.Root>
						</div>
					</div>
				{/if}
			</section>
		</Card.Content>

		<!-- 5. Footer Bar -->
		<footer
			class="px-4 py-3 bg-muted/20 border-t border-border/60 flex flex-col sm:flex-row items-center justify-between gap-3"
		>
			<div
				class="flex items-center gap-3 w-full sm:w-auto justify-between sm:justify-start"
			>
				<Button
					variant="ghost"
					size="sm"
					class="text-xs text-muted-foreground hover:text-foreground h-8 px-2"
					onclick={resetDefaults}
				>
					Reset Defaults
				</Button>

				<div
					class="text-2xs text-muted-foreground font-mono hidden md:flex items-center gap-1.5"
				>
					<span>{SCOPE_LABELS[searchScope] || searchScope}</span>
					<span>&bull;</span>
					<span>Top {topK}</span>
					<span>&bull;</span>
					<span
						>{METRIC_LABELS[similarityMetric] ||
							similarityMetric}</span
					>
				</div>
			</div>

			<Button
				variant="default"
				size="sm"
				class="h-8.5 px-4 text-xs font-semibold gap-2 shadow-xs w-full sm:w-auto"
				disabled={!isValid || isSearching}
				onclick={handleExecute}
			>
				{#if isSearching}
					<Spinner class="size-3.5" />
					<span>Retrieving...</span>
				{:else}
					<span>Run Query</span>
				{/if}
			</Button>
		</footer>
	{/if}
</Card.Root>
