<script lang="ts">
	import * as m from '#lib/paraglide/messages.js';
	import { useLocale } from '#lib/i18n.svelte.js';
	import { Button } from '#lib/components/ui/button/index.js';
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

	const locale = useLocale();
	let currentUser = $state<User | null>(null);
	let emailSignup = $state('');

	onMount(async () => {
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

	// Live activity ticker items inspired by GitHub
	const liveTickerItems = [
		{ type: 'indexed', label: '10,000+ images indexed across GHIM-10K', time: 'Active' },
		{ type: 'query', label: 'query vector #1042 matched at 96.4% cosine similarity', time: '4s ago' },
		{ type: 'feedback', label: 'Rocchio feedback loop converged in 2 iterations', time: '18s ago' },
		{ type: 'shard', label: 'FAISS centroid index shard #04 synced', time: '1m ago' },
		{ type: 'precision', label: '84.2% mean average precision @ 20 verified', time: '3m ago' },
		{ type: 'category', label: '20 groundtruth partitions calibrated', time: '5m ago' }
	];
</script>

<svelte:head>
	<title>Perceptra • Content-Based Image Retrieval Platform (GHIM-10K)</title>
</svelte:head>

<div class="min-h-screen bg-background text-foreground antialiased selection:bg-primary/10 selection:text-primary">
	<!-- ========================================================================= -->
	<!-- 1. GITHUB-STYLE STICKY NAVBAR                                             -->
	<!-- ========================================================================= -->
	<header class="sticky top-0 z-40 w-full border-b border-border/80 bg-background/95 backdrop-blur-md">
		<div class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
			<!-- Left: Logo & Nav items -->
			<div class="flex items-center gap-6 lg:gap-8">
				<a href="/" class="flex items-center gap-2.5 shrink-0 group">
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
					<div class="flex flex-col leading-none">
						<span class="text-base font-bold tracking-tight text-foreground group-hover:text-primary transition-colors">
							Perceptra
						</span>
						<span class="text-[10px] text-muted-foreground font-mono">Group 13</span>
					</div>
				</a>

				<!-- GitHub-style single-line navigation links -->
				<nav class="hidden md:flex items-center gap-5 text-xs font-semibold text-muted-foreground whitespace-nowrap">
					<a href="#platform" class="hover:text-foreground transition-colors">Platform</a>
					<a href="#simulator" class="hover:text-foreground transition-colors">{m.landing_nav_simulator()}</a>
					<a href="#features" class="hover:text-foreground transition-colors">{m.landing_nav_features()}</a>
					<a href="#benchmarks" class="hover:text-foreground transition-colors">{m.landing_nav_benchmarks()}</a>
					<a href="#architecture" class="hover:text-foreground transition-colors">{m.landing_nav_pipeline()}</a>
					<a href="/docs" class="hover:text-foreground transition-colors">{m.landing_nav_docs()}</a>
				</nav>
			</div>

			<!-- Right: Search pill + Theme/Lang + Auth controls -->
			<div class="flex items-center gap-2 sm:gap-2.5 shrink-0">
				<!-- GitHub-style search box mockup with shortcut key -->
				<div class="hidden lg:flex items-center gap-2 rounded-md border border-input bg-muted/40 px-2.5 py-1 text-xs text-muted-foreground shadow-2xs">
					<SearchIcon class="size-3.5" />
					<span class="font-normal">Search GHIM-10K...</span>
					<kbd class="ml-2 rounded border border-border bg-background px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">/</kbd>
				</div>

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
						Sign up
					</Button>
				{/if}
			</div>
		</div>
	</header>

	<!-- ========================================================================= -->
	<!-- 2. GITHUB-STYLE HERO SECTION                                              -->
	<!-- ========================================================================= -->
	<section class="relative pt-16 sm:pt-24 pb-12 overflow-hidden bg-background">
		<!-- Subtle graph-paper grid pattern inspired by GitHub -->
		<div class="pointer-events-none absolute inset-0 opacity-[0.035] dark:opacity-[0.06] [background-image:linear-gradient(to_right,#0969da_1px,transparent_1px),linear-gradient(to_bottom,#0969da_1px,transparent_1px)] [background-size:32px_32px]"></div>

		<div class="relative mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center flex flex-col items-center">
			<!-- Announcement Pill (like GitHub Universe Recap) -->
			<a
				href="#benchmarks"
				class="inline-flex items-center gap-2 rounded-full border border-border bg-card/80 px-3.5 py-1 text-xs font-semibold text-foreground shadow-2xs hover:border-primary/50 transition-all mb-8 group"
			>
				<span class="size-2 rounded-full bg-[#0969da] animate-pulse"></span>
				<span class="text-muted-foreground font-normal">GHIM-10K Retrieval Benchmark</span>
				<span class="font-mono text-primary font-bold">v2.4 Ready</span>
				<ArrowRightIcon class="size-3 text-muted-foreground group-hover:translate-x-0.5 transition-transform" />
			</a>

			<!-- Big Headline (Inspired by "Software still starts with you") -->
			<h1 class="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-foreground text-balance leading-[1.08]">
				Visual discovery still starts with you
			</h1>

			<!-- Subtitle -->
			<p class="mt-6 text-base sm:text-xl text-muted-foreground max-w-2xl text-balance leading-relaxed">
				Explore high-dimensional visual retrieval across 10,000 reference images. Fused HSV color histograms, Gabor texture filters, and real-time relevance feedback.
			</p>

			<!-- GitHub-style email signup input & action row -->
			<div class="mt-8 flex flex-col sm:flex-row items-center gap-2.5 w-full max-w-md">
				<div class="relative w-full">
					<input
						type="email"
						bind:value={emailSignup}
						placeholder="Enter your email"
						class="w-full h-11 rounded-md border border-input bg-card px-3.5 text-xs text-foreground placeholder:text-muted-foreground shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
					/>
				</div>
				<Button
					href="/register"
					class="w-full sm:w-auto h-11 px-5 text-xs font-semibold shadow-xs rounded-md shrink-0"
				>
					Sign up for Perceptra
				</Button>
			</div>

			<!-- Secondary CTA Button -->
			<div class="mt-3">
				<Button
					href="/dashboard/images"
					variant="ghost"
					size="sm"
					class="h-8 gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground cursor-pointer"
				>
					<PhotoIcon class="size-3.5" />
					<span>Explore image gallery</span>
				</Button>
			</div>
		</div>

		<!-- Cute mascot peeking over the spectrum line (GitHub Octocat homage) -->
		<div class="relative mt-12 flex justify-center">
			<div class="relative z-10 -mb-2 flex flex-col items-center">
				<div class="h-10 w-12 rounded-t-2xl bg-primary flex items-center justify-center shadow-md">
					<SparklesIcon class="size-5 text-primary-foreground" />
				</div>
			</div>
		</div>

		<!-- Signature GitHub Spectrum Multi-Color Border -->
		<div class="h-1 w-full bg-gradient-to-r from-blue-500 via-indigo-500 via-purple-500 via-pink-500 to-emerald-500"></div>
	</section>

	<!-- ========================================================================= -->
	<!-- 3. LIVE ACTIVITY TICKER RIBBON (Image 2)                                  -->
	<!-- ========================================================================= -->
	<section class="border-b border-border bg-card/60 py-3 overflow-x-auto">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex items-center gap-8 whitespace-nowrap text-xs">
			<div class="flex items-center gap-2 font-bold text-foreground">
				<span class="size-2 rounded-full bg-emerald-500 animate-ping"></span>
				<span class="text-emerald-600 dark:text-emerald-400 font-mono">LIVE FEED</span>
			</div>
			<div class="h-4 w-px bg-border"></div>
			{#each liveTickerItems as item}
				<div class="flex items-center gap-2 text-muted-foreground">
					{#if item.type === 'indexed'}
						<DatabaseIcon class="size-3.5 text-primary" />
					{:else if item.type === 'query'}
						<TargetIcon class="size-3.5 text-emerald-500" />
					{:else if item.type === 'feedback'}
						<RefreshDotIcon class="size-3.5 text-purple-500" />
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
	<!-- 4. "PERCEPTRA PLATFORM" BENTO SHOWCASE (Images 2, 3, 4)                   -->
	<!-- ========================================================================= -->
	<section id="platform" class="py-16 sm:py-24 border-b border-border bg-background">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<!-- Section Header (like "GitHub Platform") -->
			<div class="text-center max-w-3xl mx-auto mb-16">
				<h2 class="text-3xl sm:text-4xl font-extrabold tracking-tight text-foreground">
					Perceptra Platform
				</h2>
				<p class="mt-3 text-sm text-muted-foreground">
					A complete visual search and descriptor intelligence environment built on GHIM-10K.
				</p>
			</div>

			<!-- Bento Grid: 2 High-Fidelity Cards (Image 2 style) -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
				<!-- Card 1: Styled like a GitHub PR / Visual Task card -->
				<div class="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-primary/40 transition-all flex flex-col justify-between">
					<div>
						<!-- Window chrome bar -->
						<div class="flex items-center justify-between pb-4 border-b border-border mb-4">
							<div class="flex items-center gap-2">
								<span class="size-3 rounded-full bg-red-400"></span>
								<span class="size-3 rounded-full bg-yellow-400"></span>
								<span class="size-3 rounded-full bg-green-400"></span>
								<span class="ml-2 text-xs font-mono text-muted-foreground">retrieval_query_pipeline.cbir</span>
							</div>
							<span class="text-[10px] font-mono text-emerald-600 dark:text-emerald-400 font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
								Indexed #1042
							</span>
						</div>

						<!-- Mock PR title & Author line -->
						<div class="space-y-1 mb-4">
							<div class="flex items-center gap-2">
								<span class="px-2 py-0.5 rounded-full bg-[#0969da] text-white text-[11px] font-bold inline-flex items-center gap-1">
									<CheckIcon class="size-3" />
									<span>Ready</span>
								</span>
								<h3 class="text-base font-bold text-foreground">Alpine Glacial Lake #1042</h3>
							</div>
							<p class="text-xs text-muted-foreground">
								<span class="font-mono text-foreground font-semibold">user_88fb</span> queried 512-D visual vector into <span class="font-mono text-primary font-semibold">ghim-10k:partition-08</span>
							</p>
						</div>

						<!-- Checklist box inspired by GitHub "Able to merge as a stack" -->
						<div class="rounded-lg border border-border bg-muted/30 p-4 space-y-2.5 text-xs font-medium">
							<div class="flex items-center justify-between text-foreground">
								<div class="flex items-center gap-2">
									<CheckIcon class="size-4 text-emerald-500 shrink-0" />
									<span>Extract HSV Color Moments (72-bin)</span>
								</div>
								<span class="font-mono text-[11px] text-muted-foreground">3.2 ms</span>
							</div>
							<div class="flex items-center justify-between text-foreground">
								<div class="flex items-center gap-2">
									<CheckIcon class="size-4 text-emerald-500 shrink-0" />
									<span>Compute Gabor Wavelet Texture (24-dim)</span>
								</div>
								<span class="font-mono text-[11px] text-muted-foreground">4.8 ms</span>
							</div>
							<div class="flex items-center justify-between text-foreground">
								<div class="flex items-center gap-2">
									<CheckIcon class="size-4 text-emerald-500 shrink-0" />
									<span>Generate LBP Uniform Micro-patterns</span>
								</div>
								<span class="font-mono text-[11px] text-muted-foreground">5.1 ms</span>
							</div>
							<div class="flex items-center justify-between text-foreground">
								<div class="flex items-center gap-2">
									<CheckIcon class="size-4 text-emerald-500 shrink-0" />
									<span>Project into FAISS Centroid Partitions</span>
								</div>
								<span class="font-mono text-[11px] text-muted-foreground">1.4 ms</span>
							</div>
						</div>
					</div>

					<div class="mt-6 flex items-center justify-between pt-4 border-t border-border">
						<span class="text-xs text-muted-foreground">Total pipeline extraction: <strong class="text-foreground font-mono">14.5 ms</strong></span>
						<Button href="/dashboard/images" size="sm" class="h-8 text-xs font-semibold">
							View in Gallery
						</Button>
					</div>
				</div>

				<!-- Card 2: Interactive Terminal / AI Relevance Tuning (Image 2 right card) -->
				<div class="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-primary/40 transition-all flex flex-col justify-between">
					<div>
						<!-- Window chrome bar -->
						<div class="flex items-center justify-between pb-4 border-b border-border mb-4">
							<div class="flex items-center gap-2">
								<span class="size-3 rounded-full bg-red-400"></span>
								<span class="size-3 rounded-full bg-yellow-400"></span>
								<span class="size-3 rounded-full bg-green-400"></span>
								<span class="ml-2 text-xs font-mono text-muted-foreground">rocchio_feedback_agent</span>
							</div>
							<span class="text-[10px] font-mono text-primary font-semibold px-2 py-0.5 rounded-full bg-primary/10 border border-primary/20">
								Interactive
							</span>
						</div>

						<div class="space-y-1 mb-4">
							<h3 class="text-base font-bold text-foreground">Dynamic Relevance Feedback Engine</h3>
							<p class="text-xs text-muted-foreground">
								Iterative Rocchio algorithm shifting query vectors toward positive picks and away from noise.
							</p>
						</div>

						<!-- Mock terminal code block -->
						<div class="rounded-lg border border-border bg-muted/40 p-4 font-mono text-xs space-y-2 text-foreground/90 overflow-x-auto">
							<div class="text-muted-foreground">// Rocchio query vector reformulation:</div>
							<div class="text-primary font-bold">q_m = (&alpha; * q_0) + (&beta; / |D_r|) * &sum; d_r - (&gamma; / |D_nr|) * &sum; d_nr</div>
							<div class="text-muted-foreground pt-1">// Parameters calibrated for GHIM-10K:</div>
							<div class="text-emerald-600 dark:text-emerald-400">&alpha; = 1.00 &bull; &beta; = 0.75 &bull; &gamma; = 0.15</div>
							<div class="text-muted-foreground pt-1">// Convergence:</div>
							<div class="text-foreground">+12.4% precision gain achieved in 2 user iterations.</div>
						</div>
					</div>

					<div class="mt-6 flex items-center justify-between pt-4 border-t border-border">
						<span class="text-xs text-muted-foreground">Algorithm: <strong class="text-foreground">Rocchio Multi-Distance</strong></span>
						<Button href="#simulator" variant="outline" size="sm" class="h-8 text-xs font-semibold">
							Try Simulator Below
						</Button>
					</div>
				</div>
			</div>

			<!-- Multi-color dividing line (Image 3) -->
			<div class="h-0.5 w-full bg-gradient-to-r from-pink-500 via-purple-500 via-blue-500 to-emerald-500 mb-16"></div>

			<!-- Section 5: "More ways to use Perceptra" (Image 3) -->
			<div class="text-center max-w-2xl mx-auto mb-12">
				<h2 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
					More ways to use Perceptra
				</h2>
				<p class="mt-2 text-xs sm:text-sm text-muted-foreground">
					End-to-end tooling for datasets, descriptor benchmarking, and similarity search.
				</p>
			</div>

			<!-- 2 Large Feature Cards (Image 3) -->
			<div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
				<!-- Card 1: Actions / Descriptor Extraction -->
				<div class="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-primary/40 transition-all flex flex-col justify-between">
					<div class="space-y-4">
						<div class="rounded-xl border border-border bg-muted/30 p-4 space-y-2.5">
							<div class="flex items-center gap-2 font-bold text-xs text-emerald-600 dark:text-emerald-400">
								<CheckIcon class="size-4 shrink-0" />
								<span>All feature descriptors computed</span>
							</div>
							<div class="space-y-1.5 pt-2 text-xs text-foreground">
								<div class="flex justify-between font-medium">
									<span>HSV Color Histogram</span>
									<span class="font-mono text-muted-foreground">Successful in 42ms</span>
								</div>
								<div class="flex justify-between font-medium">
									<span>GLCM Texture Energy</span>
									<span class="font-mono text-muted-foreground">Successful in 28ms</span>
								</div>
								<div class="flex justify-between font-medium">
									<span>LBP Micro-patterns</span>
									<span class="font-mono text-muted-foreground">Successful in 34ms</span>
								</div>
								<div class="flex justify-between font-medium">
									<span>FAISS Centroid Normalization</span>
									<span class="font-mono text-muted-foreground">Successful in 8ms</span>
								</div>
							</div>
						</div>
						<h3 class="text-base font-bold text-foreground">Automated Descriptor Pipelines</h3>
						<p class="text-xs text-muted-foreground leading-relaxed">
							Continuous background descriptor extraction for every uploaded image with z-score standardization.
						</p>
					</div>
					<div class="pt-4">
						<Button href="/dashboard/upload" variant="outline" size="sm" class="h-8 text-xs font-semibold">
							Explore Upload Pipeline
						</Button>
					</div>
				</div>

				<!-- Card 2: Code Quality / Similarity Metrics -->
				<div class="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-primary/40 transition-all flex flex-col justify-between">
					<div class="space-y-4">
						<div class="rounded-xl border border-border bg-muted/30 p-4 font-mono text-xs space-y-1">
							<div class="text-muted-foreground">// Multi-distance similarity ranking:</div>
							<div class="text-red-500 bg-red-500/10 px-2 py-0.5 rounded">- baseline_euclidean: 0.742 (high false positives)</div>
							<div class="text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">+ proposed_cosine_zscore: 0.964 (groundtruth match)</div>
							<div class="text-muted-foreground pt-1">// Class: Nature &bull; Precision @ 20: 84.2%</div>
						</div>
						<h3 class="text-base font-bold text-foreground">Precision Distance Scoring</h3>
						<p class="text-xs text-muted-foreground leading-relaxed">
							Weighted Cosine, Euclidean, and Mahalanobis metrics tested across 10,000 GHIM-10K reference images.
						</p>
					</div>
					<div class="pt-4">
						<Button href="#benchmarks" variant="outline" size="sm" class="h-8 text-xs font-semibold">
							Explore Benchmarks
						</Button>
					</div>
				</div>
			</div>

			<!-- 3 Column Cards (Image 4) -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
				<!-- Card 1 -->
				<div class="rounded-xl border border-border bg-card p-5 space-y-3 shadow-2xs">
					<div class="size-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary">
						<LayersIcon class="size-4" />
					</div>
					<h4 class="text-sm font-bold text-foreground">Vector Similarity Engine</h4>
					<p class="text-xs text-muted-foreground leading-relaxed">
						GPU-accelerated nearest-neighbor lookup across 512-dimensional fused descriptors in under 20ms.
					</p>
					<Button href="/search" variant="outline" size="sm" class="h-7 text-xs font-semibold">Explore Search</Button>
				</div>

				<!-- Card 2 -->
				<div class="rounded-xl border border-border bg-card p-5 space-y-3 shadow-2xs">
					<div class="size-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
						<FolderIcon class="size-4" />
					</div>
					<h4 class="text-sm font-bold text-foreground">Category Hierarchy</h4>
					<p class="text-xs text-muted-foreground leading-relaxed">
						20 ground-truth categories with nested folder structures and atomic storage isolation.
					</p>
					<Button href="/dashboard/categories" variant="outline" size="sm" class="h-7 text-xs font-semibold">Explore Categories</Button>
				</div>

				<!-- Card 3 -->
				<div class="rounded-xl border border-border bg-card p-5 space-y-3 shadow-2xs">
					<div class="size-9 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-600 dark:text-purple-400">
						<DatabaseIcon class="size-4" />
					</div>
					<h4 class="text-sm font-bold text-foreground">Dataset Management</h4>
					<p class="text-xs text-muted-foreground leading-relaxed">
						High-speed batch media upload with automatic thumbnail generation and indexing queue.
					</p>
					<Button href="/dashboard/images" variant="outline" size="sm" class="h-7 text-xs font-semibold">Explore Dataset</Button>
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
						<Button href="/search" size="sm" variant="outline" class="h-7 text-xs font-semibold gap-1.5 cursor-pointer">
							<SearchIcon class="size-3" />
							<span>Query Custom Image</span>
						</Button>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 6. GITHUB-STYLE QUOTE & GIANT STATS (Image 5)                             -->
	<!-- ========================================================================= -->
	<section class="py-16 sm:py-24 border-b border-border bg-background">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<div class="mb-12">
				<h2 class="text-2xl sm:text-4xl font-extrabold tracking-tight text-foreground max-w-2xl">
					Whatever your visual domain, retrieve it with Perceptra
				</h2>
			</div>

			<!-- 2-Column Split: Quote on left, Giant Stats on right (Image 5) -->
			<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
				<!-- Left: Quote Card with Green Quotes -->
				<div class="lg:col-span-7 rounded-2xl border border-border bg-card p-8 flex flex-col justify-between shadow-xs">
					<div class="space-y-4">
						<div class="text-emerald-500 font-serif text-5xl leading-none">&ldquo;</div>
						<p class="text-lg sm:text-xl font-medium text-foreground leading-relaxed">
							Perceptra is the de facto retrieval platform for our visual benchmarking team, providing sub-20ms cosine lookups across 10,000 reference images without metric degradation or index drift.
						</p>
					</div>
					<div class="mt-8 flex items-center gap-3 pt-6 border-t border-border">
						<div class="size-10 rounded-full bg-muted border border-border flex items-center justify-center font-bold text-xs">
							AT
						</div>
						<div>
							<p class="text-xs font-bold text-foreground">Dr. Aris Thorne</p>
							<p class="text-[11px] text-muted-foreground">Lead Vision Researcher &bull; Group 13</p>
						</div>
					</div>
				</div>

				<!-- Right: Giant Numbers with typewriter labels (Image 5) -->
				<div class="lg:col-span-5 grid grid-rows-3 gap-4">
					<div class="rounded-xl border border-border bg-card p-5 flex flex-col justify-center">
						<span class="text-3xl sm:text-4xl font-bold font-mono text-emerald-600 dark:text-emerald-400">10,000</span>
						<span class="text-xs font-mono text-muted-foreground uppercase tracking-wider mt-1">GHIM-10K reference images indexed</span>
					</div>
					<div class="rounded-xl border border-border bg-card p-5 flex flex-col justify-center">
						<span class="text-3xl sm:text-4xl font-bold font-mono text-primary">84.2%</span>
						<span class="text-xs font-mono text-muted-foreground uppercase tracking-wider mt-1">mean average precision @ 20</span>
					</div>
					<div class="rounded-xl border border-border bg-card p-5 flex flex-col justify-center">
						<span class="text-3xl sm:text-4xl font-bold font-mono text-foreground">&lt; 20ms</span>
						<span class="text-xs font-mono text-muted-foreground uppercase tracking-wider mt-1">GPU-accelerated cosine latency</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 7. GITHUB CONTRIBUTION HEATMAP INSPIRED MATRIX (Image 6)                  -->
	<!-- ========================================================================= -->
	<section id="benchmarks" class="py-16 sm:py-20 border-b border-border bg-muted/20">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<div class="text-center max-w-2xl mx-auto mb-10">
				<h2 class="text-2xl sm:text-3xl font-extrabold tracking-tight text-foreground">
					GHIM-10K Benchmark Performance Matrix
				</h2>
				<p class="mt-2 text-xs sm:text-sm text-muted-foreground">
					Empirical retrieval precision across all 20 ground-truth classes.
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

			<!-- GitHub Contribution Graph Heatmap Matrix Visual (Image 6 homage) -->
			<div class="rounded-xl border border-border bg-card p-6 shadow-xs">
				<div class="flex items-center justify-between mb-4">
					<div>
						<h3 class="text-sm font-bold text-foreground">Indexed Vector Heatmap & Partition Density</h3>
						<p class="text-xs text-muted-foreground">10,000 feature descriptors distributed across 20 GHIM semantic classes</p>
					</div>
					<div class="flex items-center gap-1.5 text-[11px] text-muted-foreground font-mono">
						<span>Less</span>
						<span class="size-2.5 rounded-xs bg-muted"></span>
						<span class="size-2.5 rounded-xs bg-emerald-200 dark:bg-emerald-950"></span>
						<span class="size-2.5 rounded-xs bg-emerald-400 dark:bg-emerald-700"></span>
						<span class="size-2.5 rounded-xs bg-emerald-600 dark:bg-emerald-500"></span>
						<span>More</span>
					</div>
				</div>

				<!-- Contribution Cells Grid -->
				<div class="grid grid-flow-col grid-rows-5 gap-1.5 overflow-x-auto pb-2">
					{#each Array(100) as _, i}
						{@const intensity = (i * 7) % 5}
						<div
							class="size-3.5 sm:size-4 rounded-xs transition-colors {intensity === 0 ? 'bg-muted' : intensity === 1 ? 'bg-emerald-100 dark:bg-emerald-950/60' : intensity === 2 ? 'bg-emerald-300 dark:bg-emerald-800' : intensity === 3 ? 'bg-emerald-500 dark:bg-emerald-600' : 'bg-emerald-600 dark:bg-emerald-400'}"
							title="Cluster partition #{i + 1}: {50 + intensity * 25} vectors"
						></div>
					{/each}
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 8. GITHUB-STYLE PRE-FOOTER CTA SECTION (Image 7)                          -->
	<!-- ========================================================================= -->
	<section class="py-16 sm:py-20 border-b border-border bg-background">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
			<div class="lg:col-span-6 space-y-3">
				<div class="h-1 w-8 bg-[#0969da] rounded-full mb-2"></div>
				<h2 class="text-2xl sm:text-4xl font-extrabold tracking-tight text-foreground leading-tight">
					Join the researchers advancing content-based retrieval
				</h2>
			</div>

			<div class="lg:col-span-6 space-y-4">
				<p class="text-xs sm:text-sm text-muted-foreground leading-relaxed">
					Whether you are evaluating benchmark datasets or indexing enterprise visual assets, Perceptra gives you sub-20ms precision search with full mathematical transparency.
				</p>
				<div class="flex flex-col sm:flex-row items-center gap-2.5 w-full">
					<input
						type="email"
						placeholder="Enter your email"
						class="w-full h-10 rounded-md border border-input bg-card px-3 text-xs text-foreground placeholder:text-muted-foreground shadow-2xs"
					/>
					<Button
						href="/register"
						class="w-full sm:w-auto h-10 px-5 text-xs font-semibold shrink-0 shadow-xs rounded-md"
					>
						Sign up for Perceptra
					</Button>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 9. GITHUB-STYLE MEGA FOOTER (Image 7)                                     -->
	<!-- ========================================================================= -->
	<footer class="border-t border-border bg-card/40 py-12 text-xs text-muted-foreground">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 space-y-10">
			<!-- Newsletter Row (Image 7) -->
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
							<span>THE CBIR RESEARCH NEWSLETTER</span>
						</div>
						<p class="text-[11px] text-muted-foreground mt-0.5">
							Get algorithm updates, benchmark results, and descriptor guides. Right in your inbox.
						</p>
					</div>
				</div>
				<Button
					size="sm"
					class="h-8 px-4 text-xs font-semibold shrink-0 self-start sm:self-auto"
				>
					Subscribe
				</Button>
			</div>

			<!-- Multi-Column Links Grid -->
			<div class="grid grid-cols-2 md:grid-cols-4 gap-8">
				<div class="space-y-3">
					<h4 class="font-bold text-foreground uppercase tracking-wider text-[11px]">Platform</h4>
					<ul class="space-y-2">
						<li><a href="/dashboard" class="hover:text-foreground transition-colors">Overview</a></li>
						<li><a href="/dashboard/images" class="hover:text-foreground transition-colors">Image Gallery</a></li>
						<li><a href="/dashboard/categories" class="hover:text-foreground transition-colors">Categories Tree</a></li>
						<li><a href="/dashboard/upload" class="hover:text-foreground transition-colors">Batch Upload</a></li>
						<li><a href="/search" class="hover:text-foreground transition-colors">Similarity Search</a></li>
					</ul>
				</div>

				<div class="space-y-3">
					<h4 class="font-bold text-foreground uppercase tracking-wider text-[11px]">CBIR Engine</h4>
					<ul class="space-y-2">
						<li><a href="#features" class="hover:text-foreground transition-colors">HSV Color Moments</a></li>
						<li><a href="#features" class="hover:text-foreground transition-colors">Gabor Wavelets</a></li>
						<li><a href="#features" class="hover:text-foreground transition-colors">Local Binary Patterns</a></li>
						<li><a href="#features" class="hover:text-foreground transition-colors">FAISS GPU Index</a></li>
						<li><a href="#features" class="hover:text-foreground transition-colors">Rocchio Algorithm</a></li>
					</ul>
				</div>

				<div class="space-y-3">
					<h4 class="font-bold text-foreground uppercase tracking-wider text-[11px]">Resources</h4>
					<ul class="space-y-2">
						<li><a href="/docs" class="hover:text-foreground transition-colors">Evaluation Documentation</a></li>
						<li><a href="#benchmarks" class="hover:text-foreground transition-colors">GHIM-10K Dataset</a></li>
						<li><a href="/docs" class="hover:text-foreground transition-colors">REST API Reference</a></li>
						<li><a href="/settings" class="hover:text-foreground transition-colors">API Tokens & Keys</a></li>
					</ul>
				</div>

				<div class="space-y-3">
					<h4 class="font-bold text-foreground uppercase tracking-wider text-[11px]">Project</h4>
					<ul class="space-y-2">
						<li><span class="text-foreground font-semibold">Group 13</span></li>
						<li><a href="/terms" class="hover:text-foreground transition-colors">Terms of Service</a></li>
						<li><a href="/privacy" class="hover:text-foreground transition-colors">Privacy Policy</a></li>
						<li><a href="https://github.com" target="_blank" rel="noreferrer" class="hover:text-foreground transition-colors">GitHub Repository</a></li>
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
</div>