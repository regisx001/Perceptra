<script lang="ts">
	import { goto } from '$app/navigation';
	import * as m from '#lib/paraglide/messages.js';
	import { useLocale } from '#lib/i18n.svelte.js';
	import { Button } from '#lib/components/ui/button/index.js';
	import { Badge } from '#lib/components/ui/badge/index.js';
	import { auth, type User } from '#lib/auth.js';
	import { onMount } from 'svelte';
	import ThemeToggle from '#lib/components/theme-toggle.svelte';

	// Icons
	import GlobeIcon from '@lucide/svelte/icons/globe';
	import LogInIcon from '@lucide/svelte/icons/log-in';
	import ArrowRightIcon from '@tabler/icons-svelte/icons/arrow-right';
	import PhotoIcon from '@tabler/icons-svelte/icons/photo';
	import DatabaseIcon from '@tabler/icons-svelte/icons/database';
	import BoltIcon from '@tabler/icons-svelte/icons/bolt';
	import TargetIcon from '@tabler/icons-svelte/icons/target';
	import RefreshDotIcon from '@tabler/icons-svelte/icons/refresh-dot';
	import SparklesIcon from '@tabler/icons-svelte/icons/sparkles';
	import LayersIcon from '@lucide/svelte/icons/layers';
	import CpuIcon from '@lucide/svelte/icons/cpu';
	import CheckIcon from '@tabler/icons-svelte/icons/check';
	import ThumbsUpIcon from '@lucide/svelte/icons/thumbs-up';
	import ThumbsDownIcon from '@lucide/svelte/icons/thumbs-down';
	import FolderIcon from '@tabler/icons-svelte/icons/folder';
	import SearchIcon from '@lucide/svelte/icons/search';
	import ActivityIcon from '@tabler/icons-svelte/icons/activity';
	import CropIcon from '@tabler/icons-svelte/icons/crop';
	import UploadIcon from '@tabler/icons-svelte/icons/upload';
	import Maximize2Icon from '@lucide/svelte/icons/maximize-2';
	import XIcon from '@lucide/svelte/icons/x';
	import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
	import SlidersIcon from '@tabler/icons-svelte/icons/adjustments';

	const locale = useLocale();
	let currentUser = $state<User | null>(null);
	let emailSignup = $state('');
	let isRedirecting = $state(typeof window !== 'undefined' && auth.isAuthenticated());

	if (typeof window !== 'undefined' && auth.isAuthenticated()) {
		goto('/dashboard', { replaceState: true });
	}

	onMount(async () => {
		if (auth.isAuthenticated()) {
			isRedirecting = true;
			await goto('/dashboard', { replaceState: true });
			return;
		}
		currentUser = auth.getUser();
		try {
			const updated = await auth.fetchCurrentUser();
			if (updated) {
				currentUser = updated;
			}
		} catch {
			// Guest visitor
		}
	});

	// Real Application Pages Showcase Catalog
	interface AppScreen {
		id: string;
		title: string;
		badge: string;
		path: string;
		image: string;
		description: string;
		tags: string[];
		actionHref: string;
		actionLabel: string;
		keyFeatures: { label: string; detail: string }[];
	}

	const showcaseScreens: AppScreen[] = [
		{
			id: 'query',
			title: 'Visual Query Studio',
			badge: 'Multi-Descriptor Engine',
			path: '/dashboard/query',
			image: '/showcase/query-studio.jpg',
			description: 'Interactive query composition with live feature tuning. Upload any reference image or pick from library, dial in descriptor weights (HSV, Moments, Dominant Colors, GLCM, LBP), and run sub-20ms cosine similarity searches with Rocchio relevance feedback.',
			tags: ['Balanced & Custom Presets', 'Dynamic Weight Sliders', 'Candidate Scope Filtering', 'Rocchio Relevance Loop'],
			actionHref: '/dashboard/query',
			actionLabel: 'Open Query Studio',
			keyFeatures: [
				{ label: 'Feature Sliders', detail: 'Calibrate color vs texture weights on the fly' },
				{ label: 'Scope Control', detail: 'Filter candidates across GHIM-10K and personal uploads' },
				{ label: 'Top-K Partitioning', detail: 'Retrieve 8, 12, 24, or 48 nearest visual neighbors' }
			]
		},
		{
			id: 'images',
			title: 'Justified Photo Wall & Batch Operations',
			badge: 'Google Photos Layout',
			path: '/dashboard/images',
			image: '/showcase/gallery-photos.jpg',
			description: 'A responsive justified photo wall modeled after Google Photos that preserves native aspect ratios without distortion. Includes hover/tap top-left checkmark badges and a floating batch action bar for moving images to collections and deleting.',
			tags: ['Aspect Ratio Preserved', 'Multi-Select Checkmarks', 'Batch Collection Assign', 'Batch Delete Modal', 'Infinite Scroll'],
			actionHref: '/dashboard/images',
			actionLabel: 'Explore Image Gallery',
			keyFeatures: [
				{ label: 'Zero Cropping', detail: 'Dynamic row height respects natural portrait and landscape aspect ratios' },
				{ label: 'Google Photos Multi-Select', detail: 'Checkmark badges trigger instant floating action bar' },
				{ label: 'Batch Collections', detail: 'Assign dozens of images to categories in a single operation' }
			]
		},
		{
			id: 'overview',
			title: 'Telemetry & Sequential Latency Trendline',
			badge: 'Live Telemetry & SLAs',
			path: '/dashboard',
			image: '/showcase/overview-dark.png',
			description: 'Comprehensive operational telemetry dashboard. Real-time AreaChart tracking sequential retrieval iterations with horizontal dashed average latency reference lines, search volume timelines, and relevance judgment ratio distributions.',
			tags: ['Sequential Latency Trendline', 'Average Latency Reference Line', 'Search Traffic AreaChart', 'FRE Ratio Gauge'],
			actionHref: '/dashboard',
			actionLabel: 'View Telemetry Dashboard',
			keyFeatures: [
				{ label: 'Sequential Trendline', detail: 'AreaChart showing chronological latency spikes with average SLA line' },
				{ label: 'Relevance Feedback Ratio', detail: 'Monitors relevant vs irrelevant judgment metrics for FRE Group 13' },
				{ label: 'Activity Timeline', detail: 'Daily search frequency and Feature Relevance Estimation iterations' }
			]
		},
		{
			id: 'inspection',
			title: 'Deep Feature Analysis & Color Clustering',
			badge: 'MiniBatchKMeans & 256 Bins',
			path: '/dashboard/images/[id]',
			image: '/showcase/image-descriptors.jpg',
			description: 'Inspect extracted high-dimensional descriptors for any image. Visualizes clustered dominant color centroids via MiniBatchKMeans (k=5) with exact hex codes and percentages, alongside continuous 256-bin HSV frequency distribution curves.',
			tags: ['MiniBatchKMeans (k=5)', 'RGB & Hex Proportions', '256-Bin Continuous HSV Curves', 'GLCM Texture Energy'],
			actionHref: '/dashboard/images',
			actionLabel: 'Inspect Sample Image',
			keyFeatures: [
				{ label: 'Dominant Color Palette', detail: 'MiniBatchKMeans clustering with RGB/Hex values and proportions' },
				{ label: 'HSV Continuous Curves', detail: 'Full 256-bin Hue, Saturation, and Value spectrum graph' },
				{ label: 'Lineage & Similarity', detail: 'One-click similar image retrieval and non-destructive image transform' }
			]
		},
		{
			id: 'transform',
			title: 'Interactive Image Transform Studio',
			badge: 'Client-Side Canvas 2D',
			path: '/dashboard/transform',
			image: '/showcase/image-transform.jpg',
			description: 'In-browser non-destructive image pre-processing. Crop to preset ratios (1:1, 16:9, 9:16), rotate, flip, shear, scale, and apply affine matrix transforms before running feature extraction and CBIR queries.',
			tags: ['Crop & Aspect Presets', 'Rotate, Flip & Shear', 'Affine Matrix Transforms', 'Interactive Canvas Zoom'],
			actionHref: '/dashboard/transform',
			actionLabel: 'Launch Transform Studio',
			keyFeatures: [
				{ label: 'Aspect Ratio Presets', detail: 'Square 1:1, Landscape 16:9, and Portrait 9:16 crop presets' },
				{ label: 'Affine Matrix Controls', detail: 'Interactive numeric rotation, shear, and affine transforms' },
				{ label: 'Derived Image Export', detail: 'Save transformed variations to test transform invariant retrieval' }
			]
		},
		{
			id: 'upload',
			title: 'High-Throughput Batch Ingestion Queue',
			badge: 'Automated Extraction',
			path: '/dashboard/upload',
			image: '/showcase/upload-queue.png',
			description: 'Drag-and-drop batch ingestion with automatic descriptor extraction. Features a toggleable Auto-On descriptor pipeline, target category routing, and real-time per-file progress meters with failure recovery.',
			tags: ['Drag & Drop Multi-file', 'Auto-On Extraction Toggle', 'Target Category Selector', 'Real-time Progress Bars'],
			actionHref: '/dashboard/upload',
			actionLabel: 'Upload Your Dataset',
			keyFeatures: [
				{ label: 'Auto-Processing Switch', detail: 'Toggle immediate background extraction of Color, GLCM, and LBP descriptors' },
				{ label: 'Folder & Category Routing', detail: 'Assign newly uploaded batches directly to existing or new categories' },
				{ label: 'Resilient Queue', detail: 'Per-file status indicators (Pending, Processing, Done) with failure recovery' }
			]
		},
		{
			id: 'categories',
			title: 'Category Hierarchy & Collections',
			badge: 'Semantic Partitioning',
			path: '/dashboard/categories',
			image: '/showcase/categories-hierarchy.jpg',
			description: 'Organize your visual collection into nested category structures and root folder partitions. Search categories in real-time, view image assignment counts, and explore categorized assets in clean grids.',
			tags: ['Nested Category Tree', 'Root & Subfolder Partitions', 'Instant Search Filter', 'Categorized vs Uncategorized KPIs'],
			actionHref: '/dashboard/categories',
			actionLabel: 'Manage Collections',
			keyFeatures: [
				{ label: 'Hierarchy Navigation', detail: 'Root partitions and subfolder levels for structured visual cataloging' },
				{ label: 'Live Search & Filter', detail: 'Instant client-side filter across the entire category hierarchy' },
				{ label: 'Class Indexing', detail: 'Indexes assigned images directly into semantic class clusters' }
			]
		}
	];

	let activeScreenId = $state<string>('query');
	let activeScreen = $derived(showcaseScreens.find((s) => s.id === activeScreenId) ?? showcaseScreens[0]);
	let zoomedImage = $state<string | null>(null);

	// Interactive Simulator State
	const querySamples = [
		{
			id: 'sample-1',
			title: 'Alpine Glacial Lake',
			category: 'Nature & Landscapes',
			colorDist: 65,
			textureDist: 25,
			edgeDist: 10,
			baseSim: 0.964,
			bgGradient: 'from-sky-500/20 via-blue-600/10 to-teal-500/20',
			iconColor: 'text-sky-500',
			results: [
				{ id: 'res-11', name: 'ghim_nature_alpine_lake_02.jpg', category: 'Nature & Landscapes', similarity: 0.968, delta: '+0.04' },
				{ id: 'res-12', name: 'ghim_nature_mountain_fjord.jpg', category: 'Nature & Landscapes', similarity: 0.941, delta: '+0.02' },
				{ id: 'res-13', name: 'ghim_nature_emerald_creek.jpg', category: 'Nature & Landscapes', similarity: 0.915, delta: '-0.01' },
				{ id: 'res-14', name: 'ghim_nature_highland_reservoir.jpg', category: 'Water Partitions', similarity: 0.887, delta: '-0.03' }
			]
		},
		{
			id: 'sample-2',
			title: 'Gothic Cathedral Spire',
			category: 'Architecture & Buildings',
			colorDist: 15,
			textureDist: 55,
			edgeDist: 30,
			baseSim: 0.942,
			bgGradient: 'from-stone-500/20 via-amber-600/10 to-slate-500/20',
			iconColor: 'text-amber-500',
			results: [
				{ id: 'res-21', name: 'ghim_arch_cathedral_portal.jpg', category: 'Architecture & Buildings', similarity: 0.952, delta: '+0.03' },
				{ id: 'res-22', name: 'ghim_arch_medieval_belfry.jpg', category: 'Architecture & Buildings', similarity: 0.934, delta: '+0.01' },
				{ id: 'res-23', name: 'ghim_arch_buttress_vault.jpg', category: 'Architecture & Buildings', similarity: 0.908, delta: '-0.02' },
				{ id: 'res-24', name: 'ghim_arch_stone_masonry.jpg', category: 'Textures', similarity: 0.879, delta: '-0.05' }
			]
		},
		{
			id: 'sample-3',
			title: 'Woven Linen Textile',
			category: 'Patterns & Textures',
			colorDist: 20,
			textureDist: 70,
			edgeDist: 10,
			baseSim: 0.925,
			bgGradient: 'from-orange-500/20 via-rose-600/10 to-amber-500/20',
			iconColor: 'text-rose-500',
			results: [
				{ id: 'res-31', name: 'ghim_texture_twill_weave_08.jpg', category: 'Patterns & Textures', similarity: 0.961, delta: '+0.05' },
				{ id: 'res-32', name: 'ghim_texture_burlap_fabric.jpg', category: 'Patterns & Textures', similarity: 0.938, delta: '+0.02' },
				{ id: 'res-33', name: 'ghim_texture_cotton_canvas.jpg', category: 'Patterns & Textures', similarity: 0.912, delta: '-0.01' },
				{ id: 'res-34', name: 'ghim_texture_herringbone.jpg', category: 'Patterns & Textures', similarity: 0.884, delta: '-0.04' }
			]
		},
		{
			id: 'sample-4',
			title: 'Red Fox in Snowfield',
			category: 'Fauna & Wildlife',
			colorDist: 50,
			textureDist: 35,
			edgeDist: 15,
			baseSim: 0.918,
			bgGradient: 'from-orange-600/20 via-red-600/10 to-amber-500/20',
			iconColor: 'text-orange-500',
			results: [
				{ id: 'res-41', name: 'ghim_fauna_red_fox_standing.jpg', category: 'Fauna & Wildlife', similarity: 0.957, delta: '+0.04' },
				{ id: 'res-42', name: 'ghim_fauna_arctic_fox_winter.jpg', category: 'Fauna & Wildlife', similarity: 0.928, delta: '+0.01' },
				{ id: 'res-43', name: 'ghim_fauna_timber_wolf.jpg', category: 'Fauna & Wildlife', similarity: 0.896, delta: '-0.02' },
				{ id: 'res-44', name: 'ghim_nature_snowy_steppe.jpg', category: 'Nature & Landscapes', similarity: 0.871, delta: '-0.04' }
			]
		}
	];

	let selectedSampleIndex = $state(0);
	let relevanceFeedback = $state<Record<string, 'positive' | 'negative' | null>>({});

	let currentSample = $derived(querySamples[selectedSampleIndex]);

	function toggleFeedback(resultId: string, type: 'positive' | 'negative') {
		if (relevanceFeedback[resultId] === type) {
			relevanceFeedback[resultId] = null;
		} else {
			relevanceFeedback[resultId] = type;
		}
	}

	// Live activity ticker items
	const liveTickerItems = [
		{ type: 'indexed', label: '10,000+ images indexed across GHIM-10K', time: 'Active' },
		{ type: 'query', label: 'Query vector #1042 matched at 96.4% cosine similarity', time: '4s ago' },
		{ type: 'feedback', label: 'Rocchio feedback loop converged in 2 iterations', time: '18s ago' },
		{ type: 'latency', label: 'Sequential Latency Trendline active (Avg: 728.7 ms)', time: 'Just now' },
		{ type: 'layout', label: 'Google Photos Justified Grid enabled with zero cropping', time: '1m ago' },
		{ type: 'precision', label: '84.2% mean average precision @ 20 verified', time: '3m ago' }
	];
</script>

<svelte:head>
	<title>Perceptra - Content-Based Image Retrieval & Visual Discovery Platform</title>
	<meta
		name="description"
		content="Explore high-dimensional visual retrieval across 10,000 reference images. Fused HSV color histograms, Gabor texture filters, Google Photos justified browsing, and real-time latency telemetry."
	/>
</svelte:head>

{#if !isRedirecting}
<div class="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-primary/20 selection:text-primary">
	<!-- ========================================================================= -->
	<!-- 1. HEADER                                                                 -->
	<!-- ========================================================================= -->
	<header class="sticky top-0 z-50 w-full border-b border-border/60 bg-background/90 backdrop-blur-md">
		<div class="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
			<!-- Left: Logo & Core Nav -->
			<div class="flex items-center gap-6">
				<a href="/" class="flex items-center gap-2.5 transition-opacity hover:opacity-90">
					<img
						src="/logo-black.png"
						alt="Perceptra"
						class="h-7 w-auto object-contain dark:hidden"
					/>
					<img
						src="/logo-beige.png"
						alt="Perceptra"
						class="hidden h-7 w-auto object-contain dark:block"
					/>
					<span class="font-extrabold tracking-tight text-base text-foreground font-mono">
						Perceptra<span class="text-primary text-xs font-normal ml-1 px-1.5 py-0.5 rounded-full bg-primary/10">v2.4</span>
					</span>
				</a>

				<nav class="hidden md:flex items-center gap-5 text-xs font-medium text-muted-foreground">
					<a href="#showcase" class="hover:text-foreground transition-colors">Platform Screens</a>
					<a href="#platform" class="hover:text-foreground transition-colors">Features</a>
					<a href="#simulator" class="hover:text-foreground transition-colors">Simulator</a>
					<a href="#benchmarks" class="hover:text-foreground transition-colors">Benchmarks</a>
				</nav>
			</div>

			<!-- Right: Search pill + Theme/Lang + Auth controls -->
			<div class="flex items-center gap-2 sm:gap-2.5 shrink-0">
				<a
					href="/dashboard/images"
					class="hidden lg:flex items-center gap-2 rounded-md border border-input bg-muted/40 px-2.5 py-1 text-xs text-muted-foreground shadow-2xs hover:border-primary/40 transition-colors"
				>
					<SearchIcon class="size-3.5" />
					<span class="font-normal">Search 10,000 GHIM images...</span>
					<kbd class="ml-2 rounded border border-border bg-background px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">/</kbd>
				</a>

				<ThemeToggle />

				<!-- Language toggle button -->
				<button
					type="button"
					onclick={() => locale.toggle()}
					class="inline-flex h-8 items-center gap-1.5 px-2.5 text-xs font-semibold border border-input rounded-md shadow-2xs hover:bg-muted transition-colors cursor-pointer"
					title="Switch language (EN / FR)"
					aria-label="Switch language"
				>
					<GlobeIcon class="size-3.5 text-muted-foreground" />
					<span class="font-mono text-[11px]">{locale.current.toUpperCase()}</span>
				</button>

				{#if currentUser}
					<Button href="/dashboard" size="sm" class="h-8 gap-1.5 px-3.5 text-xs font-semibold shadow-xs">
						<span>{m.landing_cta_dashboard()}</span>
						<ArrowRightIcon class="size-3.5" />
					</Button>
				{:else}
					<a
						href="/login"
						class="text-xs font-semibold text-foreground hover:text-primary transition-colors px-2 py-1"
					>
						{m.auth_sign_in_link()}
					</a>
					<Button
						href="/register"
						size="sm"
						class="h-8 px-3.5 text-xs font-semibold shadow-xs rounded-md"
					>
						{m.auth_signup_button()}
					</Button>
				{/if}
			</div>
		</div>
	</header>

	<!-- ========================================================================= -->
	<!-- 2. HERO SECTION WITH INTERACTIVE APP SHOWCASE                             -->
	<!-- ========================================================================= -->
	<section class="relative pt-12 sm:pt-20 pb-16 overflow-hidden bg-background">
		<!-- Subtle graph-paper grid pattern -->
		<div class="pointer-events-none absolute inset-0 opacity-[0.035] dark:opacity-[0.06] [background-image:linear-gradient(to_right,#0969da_1px,transparent_1px),linear-gradient(to_bottom,#0969da_1px,transparent_1px)] [background-size:32px_32px]"></div>

		<div class="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 text-center flex flex-col items-center">
			<!-- Announcement Pill -->
			<div class="inline-flex items-center gap-2 rounded-full border border-border bg-card/80 px-3.5 py-1 text-xs font-semibold text-foreground shadow-2xs mb-6">
				<span class="size-2 rounded-full bg-emerald-500 animate-pulse"></span>
				<span class="text-muted-foreground font-normal">{m.landing_hero_badge_prod()}</span>
			</div>

			<!-- Big Headline -->
			<h1 class="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-foreground text-balance leading-[1.08] max-w-4xl">
				{m.landing_hero_headline()}
			</h1>

			<!-- Subtitle -->
			<p class="mt-5 text-base sm:text-xl text-muted-foreground max-w-3xl text-balance leading-relaxed">
				{m.landing_hero_lead()}
			</p>

			<!-- Action Row -->
			<div class="mt-8 flex flex-wrap items-center justify-center gap-3">
				<Button
					href="/dashboard"
					size="lg"
					class="h-11 px-6 text-sm font-semibold shadow-sm gap-2"
				>
					<span>{m.landing_cta_dashboard()}</span>
					<ArrowRightIcon class="size-4" />
				</Button>
				<Button
					href="/dashboard/query"
					variant="outline"
					size="lg"
					class="h-11 px-6 text-sm font-semibold shadow-2xs gap-2"
				>
					<TargetIcon class="size-4 text-primary" />
					<span>{m.landing_btn_try_query()}</span>
				</Button>
				<Button
					href="/dashboard/images"
					variant="ghost"
					size="lg"
					class="h-11 px-5 text-sm font-semibold text-muted-foreground hover:text-foreground gap-2"
				>
					<PhotoIcon class="size-4" />
					<span>{m.landing_btn_explore_images()}</span>
				</Button>
			</div>

			<!-- ========================================================================= -->
			<!-- HERO INTERACTIVE APP SHOWCASE WINDOW (Image Tabs + High-Res Mockup)       -->
			<!-- ========================================================================= -->
			<div id="showcase" class="w-full mt-12 text-left">
				<!-- Selector Tabs Bar -->
				<div class="flex items-center justify-center gap-1.5 sm:gap-2 overflow-x-auto pb-4 max-w-full">
					{#each showcaseScreens as screen}
						{@const isActive = activeScreenId === screen.id}
						<button
							type="button"
							onclick={() => activeScreenId = screen.id}
							class="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all cursor-pointer border {isActive ? 'bg-primary text-primary-foreground border-primary shadow-xs' : 'bg-card text-muted-foreground hover:text-foreground border-border hover:bg-muted/50'}"
						>
							{#if screen.id === 'query'}
								<TargetIcon class="size-3.5" />
							{:else if screen.id === 'images'}
								<PhotoIcon class="size-3.5" />
							{:else if screen.id === 'overview'}
								<ActivityIcon class="size-3.5" />
							{:else if screen.id === 'inspection'}
								<SparklesIcon class="size-3.5" />
							{:else if screen.id === 'transform'}
								<CropIcon class="size-3.5" />
							{:else if screen.id === 'upload'}
								<UploadIcon class="size-3.5" />
							{:else}
								<FolderIcon class="size-3.5" />
							{/if}
							<span>{screen.id === 'query' ? m.landing_showcase_query() : screen.id === 'images' ? m.landing_showcase_library() : screen.id === 'overview' ? m.landing_showcase_analytics() : screen.id === 'transform' ? m.landing_showcase_transform() : screen.id === 'upload' ? m.landing_showcase_upload() : screen.id === 'categories' ? m.landing_showcase_categories() : screen.title.split('&')[0].trim()}</span>
						</button>
					{/each}
				</div>

				<!-- Browser Frame Window -->
				<div class="rounded-2xl border border-border/80 bg-card shadow-2xl overflow-hidden">
					<!-- Top Window Chrome -->
					<div class="flex items-center justify-between px-4 py-3 bg-muted/40 border-b border-border/60">
						<div class="flex items-center gap-2">
							<span class="size-3 rounded-full bg-rose-500/80"></span>
							<span class="size-3 rounded-full bg-amber-500/80"></span>
							<span class="size-3 rounded-full bg-emerald-500/80"></span>
						</div>

						<!-- Address Bar Mockup -->
						<div class="flex items-center gap-2 px-3 py-1 rounded-md bg-background/80 border border-border/60 text-xs font-mono text-muted-foreground max-w-sm sm:max-w-md w-full mx-4">
							<span class="text-emerald-500">https://</span>
							<span class="text-foreground truncate">perceptra.internal{activeScreen.path}</span>
						</div>

						<div class="flex items-center gap-2">
							<Badge variant="outline" class="hidden sm:inline-flex text-[10px] font-mono border-primary/30 text-primary">
								{activeScreen.badge}
							</Badge>
							<button
								type="button"
								onclick={() => zoomedImage = activeScreen.image}
								class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors cursor-pointer"
								title="Zoom fullscreen"
								aria-label="Zoom image fullscreen"
							>
								<Maximize2Icon class="size-3.5" />
							</button>
							<Button href={activeScreen.actionHref} size="sm" variant="ghost" class="h-7 px-2 text-xs gap-1 hidden sm:flex">
								<span>Open</span>
								<ExternalLinkIcon class="size-3" />
							</Button>
						</div>
					</div>

					<!-- Screenshot Frame -->
					<div class="relative group bg-muted/20">
						<button
							type="button"
							class="w-full text-left cursor-zoom-in block"
							onclick={() => zoomedImage = activeScreen.image}
							aria-label="Click to enlarge screenshot"
						>
							<img
								src={activeScreen.image}
								alt={activeScreen.title}
								class="w-full h-auto max-h-[640px] object-cover object-top transition-transform duration-300 group-hover:scale-[1.005]"
								loading="eager"
							/>
						</button>

						<div class="absolute bottom-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
							<span class="px-2.5 py-1 rounded-md bg-background/90 text-foreground text-xs font-semibold shadow-md border border-border inline-flex items-center gap-1.5">
								<Maximize2Icon class="size-3" />
								<span>Click to Zoom</span>
							</span>
						</div>
					</div>

					<!-- Bottom Spec & Capabilities Bar -->
					<div class="p-5 sm:p-6 bg-card border-t border-border flex flex-col md:flex-row md:items-center justify-between gap-4">
						<div class="space-y-1.5 max-w-2xl">
							<div class="flex items-center gap-2">
								<h3 class="text-lg font-bold text-foreground">{activeScreen.title}</h3>
								<Badge variant="secondary" class="text-xs">{activeScreen.badge}</Badge>
							</div>
							<p class="text-xs sm:text-sm text-muted-foreground leading-relaxed">
								{activeScreen.description}
							</p>
							<div class="flex flex-wrap items-center gap-1.5 pt-1">
								{#each activeScreen.tags as tag}
									<span class="px-2 py-0.5 rounded text-[11px] font-mono bg-muted/50 text-foreground border border-border/50">
										{tag}
									</span>
								{/each}
							</div>
						</div>

						<div class="shrink-0 flex items-center gap-3">
							<Button
								href={activeScreen.actionHref}
								class="h-9 px-4 text-xs font-semibold gap-1.5 shadow-xs"
							>
								<span>{activeScreen.actionLabel}</span>
								<ArrowRightIcon class="size-3.5" />
							</Button>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Signature GitHub Spectrum Multi-Color Border -->
		<div class="h-1 w-full bg-gradient-to-r from-blue-500 via-indigo-500 via-purple-500 via-pink-500 to-emerald-500 mt-16"></div>
	</section>

	<!-- ========================================================================= -->
	<!-- 3. LIVE ACTIVITY TICKER RIBBON                                            -->
	<!-- ========================================================================= -->
	<section class="border-b border-border bg-card/60 py-3 overflow-x-auto">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex items-center gap-8 whitespace-nowrap text-xs">
			<div class="flex items-center gap-2 font-bold text-foreground">
				<span class="size-2 rounded-full bg-emerald-500 animate-ping"></span>
				<span class="text-emerald-600 dark:text-emerald-400 font-mono">LIVE TELEMETRY</span>
			</div>
			<div class="h-4 w-px bg-border"></div>
			{#each liveTickerItems as item}
				<div class="flex items-center gap-2 text-muted-foreground">
					{#if item.type === 'indexed'}
						<DatabaseIcon class="size-3.5 text-primary" />
					{:else if item.type === 'query'}
						<TargetIcon class="size-3.5 text-emerald-500" />
					{:else if item.type === 'latency'}
						<ActivityIcon class="size-3.5 text-blue-500" />
					{:else if item.type === 'layout'}
						<PhotoIcon class="size-3.5 text-indigo-500" />
					{:else}
						<CpuIcon class="size-3.5 text-amber-500" />
					{/if}
					<span class="font-medium text-foreground">{item.label}</span>
					<span class="text-[10px] text-muted-foreground font-mono">({item.time})</span>
				</div>
				<div class="h-3 w-px bg-border/60"></div>
			{/each}
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 4. "INSIDE PERCEPTRA" BENTO SHOWCASE (Real Screenshots & Deep Dives)      -->
	<!-- ========================================================================= -->
	<section id="platform" class="py-16 sm:py-24 border-b border-border bg-background">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<!-- Section Header -->
			<div class="text-center max-w-3xl mx-auto mb-16">
				<div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs font-semibold mb-3">
					<SparklesIcon class="size-3.5" />
					<span>Production Modules</span>
				</div>
				<h2 class="text-3xl sm:text-5xl font-extrabold tracking-tight text-foreground">
					Inside the Perceptra Platform
				</h2>
				<p class="mt-3 text-sm sm:text-base text-muted-foreground">
					Explore the production interface: multi-descriptor query studio, Google Photos justified wall, deep KMeans color clustering, and live latency telemetry.
				</p>
			</div>

			<!-- Bento Grid Section 1: Hero Split Feature (Visual Query Studio) -->
			<div class="rounded-2xl border border-border bg-card shadow-sm overflow-hidden mb-12">
				<div class="grid grid-cols-1 lg:grid-cols-12 gap-0 items-center">
					<!-- Visual Screenshot -->
					<div class="lg:col-span-7 bg-muted/30 p-4 sm:p-6 border-b lg:border-b-0 lg:border-r border-border">
						<div class="rounded-xl overflow-hidden border border-border shadow-md group relative">
							<button
								type="button"
								class="w-full text-left cursor-zoom-in block"
								onclick={() => zoomedImage = '/showcase/query-studio.jpg'}
								aria-label="Zoom Visual Query Studio screenshot"
							>
								<img
									src="/showcase/query-studio.jpg"
									alt="Visual Query Studio interface"
									class="w-full h-auto object-cover transition-transform duration-300 group-hover:scale-[1.01]"
								/>
							</button>
						</div>
					</div>

					<!-- Detailed Feature Info -->
					<div class="lg:col-span-5 p-6 sm:p-8 space-y-5">
						<div class="space-y-2">
							<Badge variant="outline" class="border-primary/30 text-primary font-mono text-xs">
								Core Engine • /dashboard/query
							</Badge>
							<h3 class="text-2xl font-bold text-foreground">Visual Query Studio</h3>
							<p class="text-xs sm:text-sm text-muted-foreground leading-relaxed">
								Compose queries using any reference image. Dial in feature weights across color and texture descriptors, select candidate scopes, and refine results with Rocchio relevance feedback.
							</p>
						</div>

						<div class="space-y-3 pt-2 text-xs">
							<div class="flex items-start gap-2.5">
								<CheckIcon class="size-4 text-emerald-500 shrink-0 mt-0.5" />
								<div>
									<strong class="text-foreground">Dynamic Weight Sliders:</strong>
									<span class="text-muted-foreground"> Live sliders for HSV Color Histogram, Moments, Dominant Colors, GLCM, and LBP.</span>
								</div>
							</div>
							<div class="flex items-start gap-2.5">
								<CheckIcon class="size-4 text-emerald-500 shrink-0 mt-0.5" />
								<div>
									<strong class="text-foreground">Instant Presets:</strong>
									<span class="text-muted-foreground"> One-click switching between Balanced, Color Focus, Texture Focus, and Custom modes.</span>
								</div>
							</div>
							<div class="flex items-start gap-2.5">
								<CheckIcon class="size-4 text-emerald-500 shrink-0 mt-0.5" />
								<div>
									<strong class="text-foreground">Candidate Scopes:</strong>
									<span class="text-muted-foreground"> Search strictly within the 10,000 GHIM reference set, personal uploads, or combined.</span>
								</div>
							</div>
						</div>

						<div class="pt-4 border-t border-border flex items-center justify-between">
							<span class="text-xs font-mono text-muted-foreground">Cosine Latency: <strong class="text-foreground">16.8 ms</strong></span>
							<Button href="/dashboard/query" size="sm" class="h-8 text-xs font-semibold gap-1.5">
								<span>Launch Studio</span>
								<ArrowRightIcon class="size-3.5" />
							</Button>
						</div>
					</div>
				</div>
			</div>

			<!-- Bento Grid Section 2: Two Equal Cards (Google Photos Justified Wall & Telemetry Trendline) -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
				<!-- Card 1: Google Photos Justified Wall -->
				<div class="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-primary/40 transition-all flex flex-col justify-between">
					<div class="space-y-4">
						<div class="flex items-center justify-between">
							<span class="text-xs font-mono text-primary font-bold px-2.5 py-0.5 rounded-full bg-primary/10 border border-primary/20">
								Google Photos Layout
							</span>
							<span class="text-[11px] font-mono text-muted-foreground">/dashboard/images</span>
						</div>

						<div class="rounded-xl overflow-hidden border border-border shadow-xs group relative">
							<button
								type="button"
								class="w-full text-left cursor-zoom-in block"
								onclick={() => zoomedImage = '/showcase/gallery-photos.jpg'}
								aria-label="Zoom Google Photos Justified Wall screenshot"
							>
								<img
									src="/showcase/gallery-photos.jpg"
									alt="Google Photos justified gallery"
									class="w-full h-auto object-cover transition-transform duration-300 group-hover:scale-[1.01]"
								/>
							</button>
						</div>

						<div class="space-y-1.5">
							<h3 class="text-lg font-bold text-foreground">Justified Image Wall & Batch Actions</h3>
							<p class="text-xs text-muted-foreground leading-relaxed">
								Images flow naturally at fixed row heights without cropping or distortion. Select images with top-left badges to launch the floating toolbar for moving to collections or batch deleting.
							</p>
						</div>

						<div class="grid grid-cols-2 gap-2 text-xs pt-2">
							<div class="p-2.5 rounded-lg bg-muted/30 border border-border/50">
								<div class="font-semibold text-foreground">Zero Image Distortion</div>
								<div class="text-[11px] text-muted-foreground">Calculated aspect ratios maintain full fidelity</div>
							</div>
							<div class="p-2.5 rounded-lg bg-muted/30 border border-border/50">
								<div class="font-semibold text-foreground">Floating Batch Bar</div>
								<div class="text-[11px] text-muted-foreground">Move to collection or delete in one step</div>
							</div>
						</div>
					</div>

					<div class="mt-6 pt-4 border-t border-border flex items-center justify-between">
						<span class="text-xs text-muted-foreground">Batch Operations: <strong class="text-foreground">Supported</strong></span>
						<Button href="/dashboard/images" variant="outline" size="sm" class="h-8 text-xs font-semibold gap-1.5">
							<span>Browse Gallery</span>
							<ArrowRightIcon class="size-3" />
						</Button>
					</div>
				</div>

				<!-- Card 2: Telemetry & Sequential Latency Trendline -->
				<div class="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-primary/40 transition-all flex flex-col justify-between">
					<div class="space-y-4">
						<div class="flex items-center justify-between">
							<span class="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
								Sequential Latency Trendline
							</span>
							<span class="text-[11px] font-mono text-muted-foreground">/dashboard</span>
						</div>

						<div class="rounded-xl overflow-hidden border border-border shadow-xs group relative">
							<button
								type="button"
								class="w-full text-left cursor-zoom-in block"
								onclick={() => zoomedImage = '/showcase/overview-dark.png'}
								aria-label="Zoom Telemetry and Sequential Latency Trendline screenshot"
							>
								<img
									src="/showcase/overview-dark.png"
									alt="Telemetry and latency trendline in dark mode"
									class="w-full h-auto object-cover transition-transform duration-300 group-hover:scale-[1.01]"
								/>
							</button>
						</div>

						<div class="space-y-1.5">
							<h3 class="text-lg font-bold text-foreground">Telemetry & Latency Monitoring</h3>
							<p class="text-xs text-muted-foreground leading-relaxed">
								Live performance monitoring across iterations. Interactive AreaChart visualizes chronological latency progression alongside a dashed horizontal reference line for Average Latency and SLA thresholds.
							</p>
						</div>

						<div class="grid grid-cols-2 gap-2 text-xs pt-2">
							<div class="p-2.5 rounded-lg bg-muted/30 border border-border/50">
								<div class="font-semibold text-foreground">Dashed SLA Reference</div>
								<div class="text-[11px] text-muted-foreground">Visualizes average latency drift instantly</div>
							</div>
							<div class="p-2.5 rounded-lg bg-muted/30 border border-border/50">
								<div class="font-semibold text-foreground">Relevance Ratio Tracking</div>
								<div class="text-[11px] text-muted-foreground">Monitors relevant vs irrelevant feedback</div>
							</div>
						</div>
					</div>

					<div class="mt-6 pt-4 border-t border-border flex items-center justify-between">
						<span class="text-xs text-muted-foreground">Status: <strong class="text-emerald-500">Live Telemetry</strong></span>
						<Button href="/dashboard" variant="outline" size="sm" class="h-8 text-xs font-semibold gap-1.5">
							<span>View Dashboard</span>
							<ArrowRightIcon class="size-3" />
						</Button>
					</div>
				</div>
			</div>

			<!-- Bento Grid Section 3: Three Cards (Descriptors, Transform, Upload) -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
				<!-- Card 3A: Deep Descriptors & KMeans -->
				<div class="rounded-xl border border-border bg-card p-5 space-y-3.5 shadow-2xs flex flex-col justify-between">
					<div class="space-y-3">
						<div class="rounded-lg overflow-hidden border border-border group relative">
							<button
								type="button"
								class="w-full text-left cursor-zoom-in block"
								onclick={() => zoomedImage = '/showcase/image-descriptors.jpg'}
								aria-label="Zoom deep descriptor inspection screenshot"
							>
								<img
									src="/showcase/image-descriptors.jpg"
									alt="Dominant color and HSV curves"
									class="w-full h-40 object-cover object-top transition-transform duration-300 group-hover:scale-[1.02]"
								/>
							</button>
						</div>
						<div class="space-y-1">
							<Badge variant="outline" class="text-[10px] font-mono text-purple-600 dark:text-purple-400">
								MiniBatchKMeans (k=5)
							</Badge>
							<h4 class="text-sm font-bold text-foreground">Feature Inspection & HSV Curves</h4>
							<p class="text-xs text-muted-foreground leading-relaxed">
								Clustered dominant colors with RGB/Hex proportions and full 256-bin continuous HSV distribution frequency curves.
							</p>
						</div>
					</div>
					<Button href="/dashboard/images" variant="outline" size="sm" class="h-7 text-xs font-semibold w-full">
						Inspect Descriptors
					</Button>
				</div>

				<!-- Card 3B: Image Transform Studio -->
				<div class="rounded-xl border border-border bg-card p-5 space-y-3.5 shadow-2xs flex flex-col justify-between">
					<div class="space-y-3">
						<div class="rounded-lg overflow-hidden border border-border group relative">
							<button
								type="button"
								class="w-full text-left cursor-zoom-in block"
								onclick={() => zoomedImage = '/showcase/image-transform.jpg'}
								aria-label="Zoom image transform studio screenshot"
							>
								<img
									src="/showcase/image-transform.jpg"
									alt="Transform workspace tools and resize options"
									class="w-full h-40 object-cover object-top transition-transform duration-300 group-hover:scale-[1.02]"
								/>
							</button>
						</div>
						<div class="space-y-1">
							<Badge variant="outline" class="text-[10px] font-mono text-amber-600 dark:text-amber-400">
								Canvas 2D Transformations
							</Badge>
							<h4 class="text-sm font-bold text-foreground">Image Transform Studio</h4>
							<p class="text-xs text-muted-foreground leading-relaxed">
								Client-side crop to aspect presets (1:1, 16:9, 9:16), rotate, flip, shear, and apply affine matrix transforms non-destructively.
							</p>
						</div>
					</div>
					<Button href="/dashboard/transform" variant="outline" size="sm" class="h-7 text-xs font-semibold w-full">
						Launch Transform
					</Button>
				</div>

				<!-- Card 3C: Batch Upload & Categories -->
				<div class="rounded-xl border border-border bg-card p-5 space-y-3.5 shadow-2xs flex flex-col justify-between">
					<div class="space-y-3">
						<div class="rounded-lg overflow-hidden border border-border group relative">
							<button
								type="button"
								class="w-full text-left cursor-zoom-in block"
								onclick={() => zoomedImage = '/showcase/upload-queue.png'}
								aria-label="Zoom batch upload queue screenshot"
							>
								<img
									src="/showcase/upload-queue.png"
									alt="Upload queue with progress meters"
									class="w-full h-40 object-cover object-top transition-transform duration-300 group-hover:scale-[1.02]"
								/>
							</button>
						</div>
						<div class="space-y-1">
							<Badge variant="outline" class="text-[10px] font-mono text-emerald-600 dark:text-emerald-400">
								Auto-On Extraction
							</Badge>
							<h4 class="text-sm font-bold text-foreground">Batch Upload & Ingestion</h4>
							<p class="text-xs text-muted-foreground leading-relaxed">
								Multi-file drag-and-drop with toggleable Auto-On descriptor extraction, folder routing, and live per-file progress meters.
							</p>
						</div>
					</div>
					<Button href="/dashboard/upload" variant="outline" size="sm" class="h-7 text-xs font-semibold w-full">
						Upload Images
					</Button>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 5. INTERACTIVE RETRIEVAL SIMULATOR                                        -->
	<!-- ========================================================================= -->
	<section id="simulator" class="py-16 sm:py-20 border-b border-border bg-muted/20">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<div class="text-center max-w-2xl mx-auto mb-10">
				<div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border border-primary/20 bg-primary/5 text-primary text-xs font-semibold mb-3">
					<TargetIcon class="size-3.5" />
					<span>Interactive Live Simulator</span>
				</div>
				<h2 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground">
					{m.landing_demo_title()}
				</h2>
				<p class="mt-2 text-xs sm:text-sm text-muted-foreground leading-relaxed">
					{m.landing_demo_subtitle()}
				</p>
			</div>

			<!-- Query Selector Pills -->
			<div class="flex flex-wrap items-center justify-center gap-2 mb-8">
				{#each querySamples as sample, idx}
					<button
						type="button"
						onclick={() => { selectedSampleIndex = idx; relevanceFeedback = {}; }}
						class="flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold border transition-all cursor-pointer {selectedSampleIndex === idx ? 'border-primary bg-primary text-primary-foreground shadow-xs' : 'border-border bg-card text-foreground hover:bg-muted'}"
					>
						<PhotoIcon class="size-3.5" />
						<span>{sample.title}</span>
					</button>
				{/each}
			</div>

			<!-- Interactive Simulator Panel -->
			<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 rounded-xl border border-border bg-card p-6 shadow-xs">
				<!-- Left Column: Query Signature & Descriptor Weights -->
				<div class="lg:col-span-4 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-border pb-6 lg:pb-0 lg:pr-6 space-y-5">
					<div>
						<div class="flex items-center justify-between mb-3">
							<span class="text-xs font-bold text-muted-foreground uppercase tracking-wider">{m.landing_demo_query_label()}</span>
							<span class="text-[11px] font-semibold text-primary px-2 py-0.5 rounded-full bg-primary/10">Input Vector</span>
						</div>

						<div class="relative h-44 rounded-lg border border-border bg-gradient-to-br {currentSample.bgGradient} flex flex-col items-center justify-center p-4 text-center overflow-hidden">
							<div class="p-3 rounded-full bg-background/80 border border-border/60 shadow-xs mb-2">
								<PhotoIcon class="size-8 {currentSample.iconColor}" />
							</div>
							<span class="text-sm font-bold text-foreground">{currentSample.title}</span>
							<span class="text-xs font-medium text-muted-foreground">{currentSample.category}</span>
							<div class="absolute bottom-2 right-2 text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-background/90 border border-border">
								512-D Fused
							</div>
						</div>
					</div>

					<!-- Visual Feature Energy Distribution Bars -->
					<div class="space-y-3">
						<span class="text-xs font-semibold text-foreground">Extracted Descriptor Weights</span>
						
						<div class="space-y-1">
							<div class="flex justify-between text-xs">
								<span class="text-muted-foreground">HSV Color Histogram (72-bin)</span>
								<span class="font-mono font-semibold">{currentSample.colorDist}%</span>
							</div>
							<div class="h-2 rounded-full bg-muted overflow-hidden">
								<div class="h-full bg-blue-500 rounded-full transition-all duration-300" style="width: {currentSample.colorDist}%"></div>
							</div>
						</div>

						<div class="space-y-1">
							<div class="flex justify-between text-xs">
								<span class="text-muted-foreground">Gabor Texture Energy (24-dim)</span>
								<span class="font-mono font-semibold">{currentSample.textureDist}%</span>
							</div>
							<div class="h-2 rounded-full bg-muted overflow-hidden">
								<div class="h-full bg-purple-500 rounded-full transition-all duration-300" style="width: {currentSample.textureDist}%"></div>
							</div>
						</div>

						<div class="space-y-1">
							<div class="flex justify-between text-xs">
								<span class="text-muted-foreground">LBP Micro-patterns</span>
								<span class="font-mono font-semibold">{currentSample.edgeDist}%</span>
							</div>
							<div class="h-2 rounded-full bg-muted overflow-hidden">
								<div class="h-full bg-emerald-500 rounded-full transition-all duration-300" style="width: {currentSample.edgeDist}%"></div>
							</div>
						</div>
					</div>

					<div class="rounded-lg bg-muted/50 p-3 border border-border/80 text-[11px] text-muted-foreground leading-normal">
						<span class="font-semibold text-foreground">Rocchio Relevance Feedback:</span> Click thumbs on the right to simulate dynamic positive/negative query vector adjustment.
					</div>
				</div>

				<!-- Right Column: Top-4 Retrieved Nearest Neighbors -->
				<div class="lg:col-span-8 flex flex-col justify-between space-y-4">
					<div class="flex items-center justify-between">
						<span class="text-xs font-bold text-muted-foreground uppercase tracking-wider">{m.landing_demo_results_label()}</span>
						<span class="text-xs font-mono text-muted-foreground">Index: GHIM-10K &bull; GPU Cosine</span>
					</div>

					<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
						{#each currentSample.results as res}
							{@const feedback = relevanceFeedback[res.id]}
							{@const adjustedSim = feedback === 'positive' ? Math.min(0.999, res.similarity + 0.025) : feedback === 'negative' ? Math.max(0.65, res.similarity - 0.065) : res.similarity}

							<div class="relative rounded-lg border border-border bg-card p-3.5 space-y-3 transition-all hover:border-primary/50 shadow-2xs {feedback === 'positive' ? 'ring-1 ring-emerald-500/50 bg-emerald-50/20 dark:bg-emerald-950/10' : feedback === 'negative' ? 'ring-1 ring-destructive/40 opacity-70' : ''}">
								<div class="flex items-start justify-between gap-2">
									<div class="flex items-center gap-2 min-w-0">
										<div class="size-8 rounded-md bg-muted border border-border flex items-center justify-center shrink-0">
											<PhotoIcon class="size-4 text-primary" />
										</div>
										<div class="min-w-0">
											<p class="text-xs font-semibold text-foreground truncate" title={res.name}>{res.name}</p>
											<p class="text-[11px] text-muted-foreground">{res.category}</p>
										</div>
									</div>

									<div class="text-right shrink-0">
										<span class="text-xs font-mono font-bold {adjustedSim > 0.93 ? 'text-emerald-600 dark:text-emerald-400' : 'text-primary'}">
											{(adjustedSim * 100).toFixed(1)}%
										</span>
									</div>
								</div>

								<div class="h-1.5 w-full rounded-full bg-muted overflow-hidden">
									<div class="h-full bg-primary rounded-full transition-all duration-300" style="width: {adjustedSim * 100}%"></div>
								</div>

								<div class="flex items-center justify-between pt-1 border-t border-border/60 text-xs">
									<span class="text-[10px] text-muted-foreground font-mono">Rank Vector &Delta;: {res.delta}</span>
									<div class="flex items-center gap-1">
										<button
											type="button"
											onclick={() => toggleFeedback(res.id, 'positive')}
											class="p-1 rounded hover:bg-muted text-muted-foreground transition-colors cursor-pointer {feedback === 'positive' ? '!text-emerald-600 dark:!text-emerald-400 bg-emerald-100/50 dark:bg-emerald-950/30' : ''}"
											title="Mark relevant (+ weight)"
											aria-label="Mark relevant"
										>
											<ThumbsUpIcon class="size-3.5" />
										</button>
										<button
											type="button"
											onclick={() => toggleFeedback(res.id, 'negative')}
											class="p-1 rounded hover:bg-muted text-muted-foreground transition-colors cursor-pointer {feedback === 'negative' ? '!text-destructive bg-destructive/10' : ''}"
											title="Mark irrelevant (- weight)"
											aria-label="Mark irrelevant"
										>
											<ThumbsDownIcon class="size-3.5" />
										</button>
									</div>
								</div>
							</div>
						{/each}
					</div>

					<div class="flex items-center justify-between pt-2 text-xs text-muted-foreground border-t border-border">
						<span>Average cosine retrieval time: <strong class="text-foreground font-mono">16.8 ms</strong></span>
						<Button href="/dashboard/query" size="sm" variant="outline" class="h-7 text-xs font-semibold gap-1.5 cursor-pointer">
							<SearchIcon class="size-3" />
							<span>Query Custom Image</span>
						</Button>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 6. BENCHMARK MATRIX & ACADEMIC PRECISION                                   -->
	<!-- ========================================================================= -->
	<section id="benchmarks" class="py-16 sm:py-24 border-b border-border bg-background">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<div class="text-center max-w-2xl mx-auto mb-10">
				<h2 class="text-2xl sm:text-4xl font-extrabold tracking-tight text-foreground">
					GHIM-10K Benchmark Performance Matrix
				</h2>
				<p class="mt-2 text-xs sm:text-sm text-muted-foreground">
					Empirical retrieval precision across 10,000 reference images and 20 ground-truth classes.
				</p>
			</div>

			<!-- Comparison Table -->
			<div class="overflow-x-auto rounded-xl border border-border bg-card shadow-xs mb-12">
				<table class="w-full text-left text-xs">
					<thead class="border-b border-border bg-muted/50 text-muted-foreground font-semibold">
						<tr>
							<th class="px-4 py-3">Feature Extraction Pipeline</th>
							<th class="px-4 py-3">Vector Dim</th>
							<th class="px-4 py-3">Distance Metric</th>
							<th class="px-4 py-3">Mean Average Precision (mAP@20)</th>
							<th class="px-4 py-3">Average Latency</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-border/70 text-foreground font-medium">
						<tr class="hover:bg-muted/40 transition-colors">
							<td class="px-4 py-3 font-semibold">Global Color Histogram (HSV)</td>
							<td class="px-4 py-3 font-mono text-muted-foreground">64-D</td>
							<td class="px-4 py-3 text-muted-foreground">Euclidean (L2)</td>
							<td class="px-4 py-3 font-mono">61.4%</td>
							<td class="px-4 py-3 font-mono text-muted-foreground">14.2 ms</td>
						</tr>
						<tr class="hover:bg-muted/40 transition-colors">
							<td class="px-4 py-3 font-semibold">GLCM Gray-Level Co-occurrence</td>
							<td class="px-4 py-3 font-mono text-muted-foreground">24-D</td>
							<td class="px-4 py-3 text-muted-foreground">Manhattan (L1)</td>
							<td class="px-4 py-3 font-mono">66.8%</td>
							<td class="px-4 py-3 font-mono text-muted-foreground">16.1 ms</td>
						</tr>
						<tr class="hover:bg-muted/40 transition-colors">
							<td class="px-4 py-3 font-semibold">Uniform Local Binary Patterns (LBP)</td>
							<td class="px-4 py-3 font-mono text-muted-foreground">128-D</td>
							<td class="px-4 py-3 text-muted-foreground">Chi-Square (&chi;&sup2;)</td>
							<td class="px-4 py-3 font-mono">68.9%</td>
							<td class="px-4 py-3 font-mono text-muted-foreground">17.5 ms</td>
						</tr>
						<tr class="bg-primary/5 hover:bg-primary/10 transition-colors font-bold text-foreground">
							<td class="px-4 py-3.5 flex items-center gap-2">
								<span class="size-2 rounded-full bg-primary"></span>
								<span>Perceptra Hybrid Fusion (Proposed)</span>
							</td>
							<td class="px-4 py-3.5 font-mono text-primary">512-D</td>
							<td class="px-4 py-3.5 text-primary">Weighted Cosine + Z-Score</td>
							<td class="px-4 py-3.5 font-mono text-emerald-600 dark:text-emerald-400">84.2% (+15.3%)</td>
							<td class="px-4 py-3.5 font-mono">18.4 ms</td>
						</tr>
					</tbody>
				</table>
			</div>

			<!-- 3 Giant Stats -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
				<div class="rounded-xl border border-border bg-card p-6 flex flex-col justify-center text-center">
					<span class="text-4xl font-extrabold font-mono text-emerald-600 dark:text-emerald-400">10,000</span>
					<span class="text-xs font-mono text-muted-foreground uppercase tracking-wider mt-2">GHIM-10K reference images indexed</span>
				</div>
				<div class="rounded-xl border border-border bg-card p-6 flex flex-col justify-center text-center">
					<span class="text-4xl font-extrabold font-mono text-primary">84.2%</span>
					<span class="text-xs font-mono text-muted-foreground uppercase tracking-wider mt-2">Mean average precision @ 20</span>
				</div>
				<div class="rounded-xl border border-border bg-card p-6 flex flex-col justify-center text-center">
					<span class="text-4xl font-extrabold font-mono text-foreground">&lt; 20 ms</span>
					<span class="text-xs font-mono text-muted-foreground uppercase tracking-wider mt-2">Average cosine retrieval speed</span>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 7. PRE-FOOTER CTA SECTION                                                 -->
	<!-- ========================================================================= -->
	<section class="py-16 sm:py-20 border-b border-border bg-background">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
			<div class="lg:col-span-6 space-y-3">
				<div class="h-1 w-8 bg-[#0969da] rounded-full mb-2"></div>
				<h2 class="text-2xl sm:text-4xl font-extrabold tracking-tight text-foreground leading-tight">
					Ready to experience next-generation visual retrieval?
				</h2>
			</div>

			<div class="lg:col-span-6 space-y-4">
				<p class="text-xs sm:text-sm text-muted-foreground leading-relaxed">
					Launch Perceptra to explore multi-descriptor similarity, Google Photos justified browsing, and live latency telemetry across benchmark datasets.
				</p>
				<div class="flex flex-col sm:flex-row items-center gap-2.5 w-full">
					<input
						type="email"
						bind:value={emailSignup}
						placeholder="Enter your email"
						class="w-full h-10 rounded-md border border-input bg-card px-3 text-xs text-foreground placeholder:text-muted-foreground shadow-2xs"
					/>
					<Button
						href="/register"
						class="w-full sm:w-auto h-10 px-5 text-xs font-semibold shrink-0 shadow-xs rounded-md"
					>
						Get Started Free
					</Button>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 8. FOOTER                                                                 -->
	<!-- ========================================================================= -->
	<footer class="border-t border-border bg-card/40 py-12 text-xs text-muted-foreground">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-10">
			<!-- Top Row -->
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-8 border-b border-border">
				<div class="flex items-center gap-3">
					<img
						src="/logo-black.png"
						alt="Perceptra"
						class="h-8 w-auto object-contain dark:hidden"
					/>
					<img
						src="/logo-beige.png"
						alt="Perceptra"
						class="hidden h-8 w-auto object-contain dark:block"
					/>
					<div>
						<div class="flex items-center gap-1.5 font-bold text-foreground">
							<span class="size-2 rounded-xs bg-[#0969da]"></span>
							<span>PERCEPTRA VISUAL SEARCH PLATFORM</span>
						</div>
						<p class="text-[11px] text-muted-foreground mt-0.5">
							Content-based image retrieval with multi-descriptor fusion and FRE Group 13 relevance feedback.
						</p>
					</div>
				</div>
				<Button
					href="/dashboard"
					size="sm"
					class="h-8 px-4 text-xs font-semibold shrink-0 self-start sm:self-auto gap-1"
				>
					<span>Open Platform</span>
					<ArrowRightIcon class="size-3" />
				</Button>
			</div>

			<!-- Multi-Column Links Grid -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-8">
				<div class="space-y-3">
					<h4 class="font-bold text-foreground uppercase tracking-wider text-[11px]">Core Modules</h4>
					<ul class="space-y-2">
						<li><a href="/dashboard" class="hover:text-foreground transition-colors">Telemetry Dashboard</a></li>
						<li><a href="/dashboard/query" class="hover:text-foreground transition-colors">Visual Query Studio</a></li>
						<li><a href="/dashboard/images" class="hover:text-foreground transition-colors">Justified Photo Gallery</a></li>
						<li><a href="/dashboard/transform" class="hover:text-foreground transition-colors">Image Transform Studio</a></li>
						<li><a href="/dashboard/upload" class="hover:text-foreground transition-colors">Batch Ingestion Queue</a></li>
						<li><a href="/dashboard/categories" class="hover:text-foreground transition-colors">Category Hierarchy</a></li>
					</ul>
				</div>

				<div class="space-y-3">
					<h4 class="font-bold text-foreground uppercase tracking-wider text-[11px]">CBIR Descriptors</h4>
					<ul class="space-y-2">
						<li><a href="#platform" class="hover:text-foreground transition-colors">HSV Color Histograms (72-D)</a></li>
						<li><a href="#platform" class="hover:text-foreground transition-colors">Color Moments (Mean, Std, Skew)</a></li>
						<li><a href="#platform" class="hover:text-foreground transition-colors">MiniBatchKMeans Dominant Colors (k=5)</a></li>
						<li><a href="#platform" class="hover:text-foreground transition-colors">GLCM Texture Energy (24-D)</a></li>
						<li><a href="#platform" class="hover:text-foreground transition-colors">Uniform LBP Micro-patterns (128-D)</a></li>
					</ul>
				</div>

				<div class="space-y-3">
					<h4 class="font-bold text-foreground uppercase tracking-wider text-[11px]">Academic Reference</h4>
					<ul class="space-y-2">
						<li><a href="#benchmarks" class="hover:text-foreground transition-colors">GHIM-10K Benchmark</a></li>
						<li><a href="#benchmarks" class="hover:text-foreground transition-colors">Rocchio Algorithm Reformulation</a></li>
						<li><a href="#benchmarks" class="hover:text-foreground transition-colors">Mean Average Precision (mAP)</a></li>
						<li><a href="#benchmarks" class="hover:text-foreground transition-colors">Sequential Latency Trendline</a></li>
					</ul>
				</div>

				<div class="space-y-3">
					<h4 class="font-bold text-foreground uppercase tracking-wider text-[11px]">Project</h4>
					<ul class="space-y-2">
						<li><span class="text-foreground font-semibold">Group 13 Project</span></li>
						<li><a href="/terms" class="hover:text-foreground transition-colors">Terms of Service</a></li>
						<li><a href="/privacy" class="hover:text-foreground transition-colors">Privacy Policy</a></li>
					</ul>
				</div>
			</div>

			<!-- Bottom Legal Line & Status Indicator -->
			<div class="flex flex-col sm:flex-row items-center justify-between gap-4 pt-6 border-t border-border text-[11px]">
				<p>&copy; 2026 Perceptra &bull; Group 13 Academic Project &bull; All rights reserved.</p>
				<div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
					<span class="size-2 rounded-full bg-emerald-500 animate-pulse"></span>
					<span>FAISS Retrieval Engine Operational (10,000 Vectors)</span>
				</div>
			</div>
		</div>
	</footer>

	<!-- ========================================================================= -->
	<!-- 9. SCREENSHOT ZOOM LIGHTBOX MODAL                                         -->
	<!-- ========================================================================= -->
	{#if zoomedImage}
		<div
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 sm:p-8 animate-in fade-in duration-200"
		>
			<button
				type="button"
				class="absolute inset-0 bg-transparent w-full h-full cursor-default"
				onclick={() => zoomedImage = null}
				aria-label="Close zoomed view"
			></button>

			<div
				class="relative z-10 max-w-6xl w-full max-h-[90vh] rounded-2xl overflow-hidden border border-border/60 bg-card shadow-2xl"
			>
				<div class="flex items-center justify-between px-4 py-2.5 bg-muted/70 border-b border-border">
					<span class="text-xs font-mono text-muted-foreground truncate">{zoomedImage}</span>
					<button
						type="button"
						onclick={() => zoomedImage = null}
						class="p-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors cursor-pointer"
						aria-label="Close zoomed view"
					>
						<XIcon class="size-4" />
					</button>
				</div>
				<div class="overflow-auto max-h-[calc(90vh-42px)] p-2 bg-muted/20">
					<img
						src={zoomedImage}
						alt="Zoomed interface preview"
						class="w-full h-auto rounded-lg object-contain shadow-sm"
					/>
				</div>
			</div>
		</div>
	{/if}
</div>
{/if}
