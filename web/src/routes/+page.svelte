<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { auth, type User } from '#lib/auth.js';
	import { useLocale } from '#lib/i18n.svelte.js';
	import * as m from '#lib/paraglide/messages.js';

	// shadcn-svelte UI components
	import * as Card from '#lib/components/ui/card/index.js';
	import { Button } from '#lib/components/ui/button/index.js';
	import { Badge } from '#lib/components/ui/badge/index.js';
	import * as Tabs from '#lib/components/ui/tabs/index.js';
	import { Slider } from '#lib/components/ui/slider/index.js';
	import * as Dialog from '#lib/components/ui/dialog/index.js';
	import { Separator } from '#lib/components/ui/separator/index.js';
	import ThemeToggle from '#lib/components/theme-toggle.svelte';

	// Icons
	import GlobeIcon from '@lucide/svelte/icons/globe';
	import Maximize2Icon from '@lucide/svelte/icons/maximize-2';
	import XIcon from '@lucide/svelte/icons/x';
	import CheckIcon from '@lucide/svelte/icons/check';
	import ArrowRightIcon from '@lucide/svelte/icons/arrow-right';
	import ExternalLinkIcon from '@lucide/svelte/icons/external-link';
	import SparklesIcon from '@lucide/svelte/icons/sparkles';
	import SlidersHorizontalIcon from '@lucide/svelte/icons/sliders-horizontal';
	import RefreshCwIcon from '@lucide/svelte/icons/refresh-cw';
	import UploadCloudIcon from '@lucide/svelte/icons/upload-cloud';
	import SearchIcon from '@lucide/svelte/icons/search';
	import CropIcon from '@lucide/svelte/icons/crop';
	import RotateCwIcon from '@lucide/svelte/icons/rotate-cw';
	import FlipHorizontalIcon from '@lucide/svelte/icons/flip-horizontal';

	const locale = useLocale();
	let currentUser = $state<User | null>(null);

	onMount(async () => {
		currentUser = auth.getUser();
		try {
			const updated = await auth.fetchCurrentUser();
			if (updated) currentUser = updated;
		} catch {
			// Guest visitor
		}
	});

	/* ------------------------------------------------------------------------
	   1. TOAST NOTIFICATION
	   ------------------------------------------------------------------------ */
	let toastMessage = $state<string>('');
	let isToastVisible = $state(false);
	let toastTimer: ReturnType<typeof setTimeout> | null = null;

	function showToast(msg: string) {
		toastMessage = msg;
		isToastVisible = true;
		if (toastTimer) clearTimeout(toastTimer);
		toastTimer = setTimeout(() => {
			isToastVisible = false;
		}, 2600);
	}

	function copyText(text: string) {
		if (typeof navigator !== 'undefined' && navigator.clipboard) {
			navigator.clipboard.writeText(text).then(
				() => showToast(`Copied ${text} to clipboard`),
				() => copyFallback(text)
			);
		} else {
			copyFallback(text);
		}
	}

	function copyFallback(text: string) {
		try {
			const ta = document.createElement('textarea');
			ta.value = text;
			ta.style.position = 'fixed';
			ta.style.opacity = '0';
			document.body.appendChild(ta);
			ta.select();
			document.execCommand('copy');
			document.body.removeChild(ta);
			showToast(`Copied ${text} to clipboard`);
		} catch {
			showToast(`HEX: ${text}`);
		}
	}

	/* ------------------------------------------------------------------------
	   2. CURATED GALLERY DATASET & PRESETS
	   ------------------------------------------------------------------------ */
	interface CandidateResult {
		title: string;
		file: string;
		url: string;
		colorSim: number;
		texSim: number;
	}

	interface GalleryPhoto {
		id: string;
		title: string;
		filename: string;
		category: string;
		resolution: string;
		dominantHex: string;
		url: string;
		palette?: { hex: string; pct: number; rgb: string }[];
		candidates?: CandidateResult[];
	}

	const GALLERY_ITEMS: GalleryPhoto[] = [
		{
			id: 'terraced',
			title: 'Terraced Fields',
			filename: '04_2184.jpg',
			category: 'Landscapes',
			resolution: '1600×1200',
			dominantHex: '#6F8B3E',
			url: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80',
			palette: [
				{ hex: '#6F8B3E', pct: 34, rgb: '111, 139, 62' },
				{ hex: '#B99848', pct: 24, rgb: '185, 152, 72' },
				{ hex: '#3A4F25', pct: 19, rgb: '58, 79, 37' },
				{ hex: '#D4CFC2', pct: 14, rgb: '212, 207, 194' },
				{ hex: '#262C1E', pct: 9, rgb: '38, 44, 30' }
			],
			candidates: [
				{ title: 'Emerald Terraces', file: '04_2191.jpg', url: 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=600&q=80', colorSim: 0.96, texSim: 0.91 },
				{ title: 'Highland Pasture', file: '04_2208.jpg', url: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=600&q=80', colorSim: 0.89, texSim: 0.97 },
				{ title: 'Golden Valley', file: '04_2140.jpg', url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80', colorSim: 0.94, texSim: 0.82 },
				{ title: 'Contour Ridge', file: '04_2312.jpg', url: 'https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=600&q=80', colorSim: 0.84, texSim: 0.95 }
			]
		},
		{
			id: 'temple',
			title: 'Imperial Temple',
			filename: '12_6023.jpg',
			category: 'Architecture',
			resolution: '1200×1600',
			dominantHex: '#4A80D4',
			url: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=800&q=80',
			palette: [
				{ hex: '#4A80D4', pct: 39, rgb: '74, 128, 212' },
				{ hex: '#171010', pct: 21, rgb: '23, 16, 16' },
				{ hex: '#584C50', pct: 16, rgb: '88, 76, 80' },
				{ hex: '#B4694A', pct: 15, rgb: '180, 105, 74' },
				{ hex: '#C3BDAE', pct: 9, rgb: '195, 189, 174' }
			],
			candidates: [
				{ title: 'Pavilion Eaves', file: '12_6002.jpg', url: 'https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?auto=format&fit=crop&w=600&q=80', colorSim: 0.95, texSim: 0.94 },
				{ title: 'Stone Courtyard', file: '12_6041.jpg', url: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=600&q=80', colorSim: 0.86, texSim: 0.96 },
				{ title: 'Vermilion Gate', file: '12_6089.jpg', url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=600&q=80', colorSim: 0.97, texSim: 0.83 },
				{ title: 'Timber Pagoda', file: '12_6110.jpg', url: 'https://images.unsplash.com/photo-1528360983277-13d401cdc186?auto=format&fit=crop&w=600&q=80', colorSim: 0.82, texSim: 0.93 }
			]
		},
		{
			id: 'autumn',
			title: 'Autumn Canopy',
			filename: '08_4410.jpg',
			category: 'Autumn',
			resolution: '1600×1067',
			dominantHex: '#D9822B',
			url: 'https://images.unsplash.com/photo-1507041957456-9c397ce39c97?auto=format&fit=crop&w=800&q=80',
			palette: [
				{ hex: '#D9822B', pct: 37, rgb: '217, 130, 43' },
				{ hex: '#8F3F1E', pct: 23, rgb: '143, 63, 30' },
				{ hex: '#EAB64D', pct: 18, rgb: '234, 182, 77' },
				{ hex: '#3D2B1F', pct: 13, rgb: '61, 43, 31' },
				{ hex: '#7A8E9C', pct: 9, rgb: '122, 142, 156' }
			],
			candidates: [
				{ title: 'Amber Birch Grove', file: '08_4429.jpg', url: 'https://images.unsplash.com/photo-1476820865390-c52aeebb9891?auto=format&fit=crop&w=600&q=80', colorSim: 0.97, texSim: 0.89 },
				{ title: 'Forest Floor Grain', file: '08_4455.jpg', url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=600&q=80', colorSim: 0.84, texSim: 0.96 },
				{ title: 'Maple Reflection', file: '08_4471.jpg', url: 'https://images.unsplash.com/photo-1509565840034-3c385bbe6451?auto=format&fit=crop&w=600&q=80', colorSim: 0.95, texSim: 0.84 },
				{ title: 'Cedar Timberline', file: '08_4502.jpg', url: 'https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=600&q=80', colorSim: 0.81, texSim: 0.94 }
			]
		},
		{
			id: 'glacier',
			title: 'Alpine Basin',
			filename: '04_2240.jpg',
			category: 'Landscapes',
			resolution: '1600×1200',
			dominantHex: '#3B6E8C',
			url: 'https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=800&q=80'
		},
		{
			id: 'misty',
			title: 'Misty Highlands',
			filename: '04_2276.jpg',
			category: 'Landscapes',
			resolution: '1600×1067',
			dominantHex: '#4E6B5E',
			url: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80'
		},
		{
			id: 'kyoto',
			title: 'Vermilion Shrine',
			filename: '12_6089.jpg',
			category: 'Architecture',
			resolution: '1600×1067',
			dominantHex: '#C94B32',
			url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=800&q=80'
		},
		{
			id: 'stone-arch',
			title: 'Stone Citadel',
			filename: '12_6041.jpg',
			category: 'Architecture',
			resolution: '1600×1200',
			dominantHex: '#7A766E',
			url: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80'
		},
		{
			id: 'birch',
			title: 'Golden Birch Road',
			filename: '08_4429.jpg',
			category: 'Autumn',
			resolution: '1600×1067',
			dominantHex: '#E09F3E',
			url: 'https://images.unsplash.com/photo-1476820865390-c52aeebb9891?auto=format&fit=crop&w=800&q=80'
		},
		{
			id: 'maple',
			title: 'Crimson Foliage',
			filename: '08_4471.jpg',
			category: 'Autumn',
			resolution: '1600×1200',
			dominantHex: '#B84A27',
			url: 'https://images.unsplash.com/photo-1509565840034-3c385bbe6451?auto=format&fit=crop&w=800&q=80'
		},
		{
			id: 'vessel',
			title: 'Harbor Vessel',
			filename: '19_8812.jpg',
			category: 'Maritime',
			resolution: '1600×1067',
			dominantHex: '#3A5E7A',
			url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80'
		},
		{
			id: 'sailing',
			title: 'Deep Water Horizon',
			filename: '19_8845.jpg',
			category: 'Maritime',
			resolution: '1600×1200',
			dominantHex: '#2C4E6E',
			url: 'https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=800&q=80'
		},
		{
			id: 'coast',
			title: 'Coastal Pier',
			filename: '19_8890.jpg',
			category: 'Maritime',
			resolution: '1600×1067',
			dominantHex: '#5C7C8A',
			url: 'https://images.unsplash.com/photo-1468581264429-2548ef9eb732?auto=format&fit=crop&w=800&q=80'
		}
	];

	/* ------------------------------------------------------------------------
	   3. HERO WORKBENCH STATE
	   ------------------------------------------------------------------------ */
	let activeQueryKey = $state('terraced');
	let customQueryObj = $state<GalleryPhoto | null>(null);
	let colorWeight = $state(50);
	const textureWeight = $derived(100 - colorWeight);
	let activePreset = $state<'balanced' | 'color' | 'texture' | null>('balanced');

	const activeQueryData = $derived.by(() => {
		if (customQueryObj) return customQueryObj;
		return GALLERY_ITEMS.find((item) => item.id === activeQueryKey) || GALLERY_ITEMS[0];
	});

	const workbenchPalette = $derived(activeQueryData.palette || GALLERY_ITEMS[0].palette || []);

	const rankedWorkbenchCandidates = $derived.by(() => {
		const cW = colorWeight / 100;
		const tW = textureWeight / 100;
		const list = activeQueryData.candidates || GALLERY_ITEMS[0].candidates || [];
		return list
			.map((cand) => {
				const score = (cand.colorSim * cW + cand.texSim * tW) * 100;
				return { ...cand, score };
			})
			.sort((a, b) => b.score - a.score);
	});

	const simulatedLatency = $derived(
		(14.6 + Math.abs(colorWeight - 50) * 0.04 + (activeQueryData.filename.length % 4) * 0.6).toFixed(1)
	);

	function setQueryPreset(preset: 'balanced' | 'color' | 'texture') {
		activePreset = preset;
		if (preset === 'balanced') colorWeight = 50;
		if (preset === 'color') colorWeight = 80;
		if (preset === 'texture') colorWeight = 20;
	}

	function selectQueryTab(key: string) {
		customQueryObj = null;
		activeQueryKey = key;
	}

	/* ------------------------------------------------------------------------
	   4. HSV 256-BIN SVG CHART INTERACTIVITY
	   ------------------------------------------------------------------------ */
	const BINS = 256;
	const hsvData = { h: [] as number[], s: [] as number[], v: [] as number[] };

	for (let i = 0; i < BINS; i++) {
		const hVal =
			0.165 * Math.exp(-Math.pow((i - 156) / 6.5, 2)) +
			0.095 * Math.exp(-Math.pow((i - 163) / 5, 2)) +
			0.052 * Math.exp(-Math.pow((i - 18) / 11, 2)) +
			0.012 +
			0.008 * Math.sin(i * 0.27) * Math.cos(i * 0.11);

		const sVal =
			0.048 * Math.exp(-Math.pow((i - 188) / 22, 2)) +
			0.036 * Math.exp(-Math.pow((i - 28) / 18, 2)) +
			0.014 +
			0.005 * Math.sin(i * 0.19);

		const vVal =
			0.042 * Math.exp(-Math.pow((i - 216) / 28, 2)) +
			0.031 * Math.exp(-Math.pow((i - 104) / 24, 2)) +
			0.018 +
			0.004 * Math.cos(i * 0.15);

		hsvData.h.push(Math.max(0.002, hVal));
		hsvData.s.push(Math.max(0.002, sVal));
		hsvData.v.push(Math.max(0.002, vVal));
	}

	function buildCurvePath(arr: number[], closeArea = false): string {
		const w = 640,
			base = 196,
			maxH = 180,
			scaleMax = 0.18;
		let d = '';
		for (let i = 0; i < arr.length; i += 2) {
			const x = (i / (arr.length - 1)) * w;
			const y = base - Math.min(1, arr[i] / scaleMax) * maxH;
			d += i === 0 ? `M ${x.toFixed(1)} ${y.toFixed(1)}` : ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
		}
		if (closeArea) {
			d += ` L ${w} ${base} L 0 ${base} Z`;
		}
		return d;
	}

	const pathCurveH = buildCurvePath(hsvData.h);
	const pathCurveS = buildCurvePath(hsvData.s);
	const pathCurveV = buildCurvePath(hsvData.v);
	const pathAreaH = buildCurvePath(hsvData.h, true);
	const pathAreaS = buildCurvePath(hsvData.s, true);
	const pathAreaV = buildCurvePath(hsvData.v, true);

	let activeHsvFilter = $state<'all' | 'h' | 's' | 'v'>('all');
	let cursorBin = $state(157);
	let cursorX = $derived((cursorBin / (BINS - 1)) * 640);
	const yFromVal = (v: number) => 196 - Math.min(1, v / 0.18) * 180;
	let dotHY = $derived(yFromVal(hsvData.h[cursorBin]));
	let dotSY = $derived(yFromVal(hsvData.s[cursorBin]));
	let dotVY = $derived(yFromVal(hsvData.v[cursorBin]));

	function handleHsvMouseMove(e: MouseEvent & { currentTarget: SVGSVGElement }) {
		const rect = e.currentTarget.getBoundingClientRect();
		const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
		cursorBin = Math.min(BINS - 1, Math.round(ratio * (BINS - 1)));
	}

	/* ------------------------------------------------------------------------
	   5. K-MEANS DOMINANT CLUSTERS (k=5 / k=8)
	   ------------------------------------------------------------------------ */
	const CLUSTERS = {
		5: [
			{ hex: '#4A80D4', pct: 39.4, rgb: '74, 128, 212' },
			{ hex: '#171010', pct: 21.4, rgb: '23, 16, 16' },
			{ hex: '#584C50', pct: 15.6, rgb: '88, 76, 80' },
			{ hex: '#B4694A', pct: 15.4, rgb: '180, 105, 74' },
			{ hex: '#C3BDAE', pct: 8.2, rgb: '195, 189, 174' }
		],
		8: [
			{ hex: '#4A80D4', pct: 26.2, rgb: '74, 128, 212' },
			{ hex: '#6EA0E6', pct: 13.2, rgb: '110, 160, 230' },
			{ hex: '#171010', pct: 14.8, rgb: '23, 16, 16' },
			{ hex: '#3B2F2F', pct: 9.6, rgb: '59, 47, 47' },
			{ hex: '#584C50', pct: 11.4, rgb: '88, 76, 80' },
			{ hex: '#B4694A', pct: 10.6, rgb: '180, 105, 74' },
			{ hex: '#D48A6A', pct: 7.4, rgb: '212, 138, 106' },
			{ hex: '#C3BDAE', pct: 6.8, rgb: '195, 189, 174' }
		]
	};
	let kmeansK = $state<5 | 8>(5);
	const activeClusters = $derived(CLUSTERS[kmeansK]);

	/* ------------------------------------------------------------------------
	   6. FEATURE RELEVANCE ESTIMATION (FRE)
	   ------------------------------------------------------------------------ */
	const FRE_CHANNELS = [
		{ key: 'hsv', label: 'HSV', color: 'var(--chart-1)' },
		{ key: 'moments', label: 'Moments', color: 'var(--chart-2)' },
		{ key: 'dominant', label: 'Dominant', color: 'var(--chart-3)' },
		{ key: 'glcm', label: 'GLCM', color: 'var(--chart-4)' },
		{ key: 'lbp', label: 'LBP', color: 'var(--chart-5)' }
	] as const;

	const FRE_ITEMS = [
		{
			id: 'fre1',
			title: 'Pavilion Eaves',
			url: 'https://images.unsplash.com/photo-1547981609-4b6bfe67ca0b?auto=format&fit=crop&w=500&q=80',
			bias: { hsv: 8, moments: 3, dominant: 7, glcm: -9, lbp: -9 }
		},
		{
			id: 'fre2',
			title: 'Stone Courtyard',
			url: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=500&q=80',
			bias: { hsv: -8, moments: -4, dominant: -6, glcm: 10, lbp: 8 }
		},
		{
			id: 'fre3',
			title: 'Vermilion Gate',
			url: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=500&q=80',
			bias: { hsv: 6, moments: 5, dominant: 8, glcm: -10, lbp: -9 }
		}
	];

	let freJudgments = $state<Record<string, number>>({ fre1: 0, fre2: 0, fre3: 0 });
	let freRound = $state(0);

	const freWeights = $derived.by(() => {
		const raw: Record<string, number> = { hsv: 20, moments: 20, dominant: 20, glcm: 20, lbp: 20 };
		let activeCount = 0;
		FRE_ITEMS.forEach((item) => {
			const j = freJudgments[item.id] || 0;
			if (j !== 0) {
				activeCount++;
				for (const k of Object.keys(raw)) {
					raw[k] = Math.max(6, raw[k] + (item.bias as any)[k] * j);
				}
			}
		});

		const total = Object.values(raw).reduce((s, v) => s + v, 0);
		const norm: Record<string, number> = {};
		for (const k of Object.keys(raw)) {
			norm[k] = Math.round((raw[k] / total) * 100);
		}
		const sumNorm = Object.values(norm).reduce((s, v) => s + v, 0);
		norm.hsv += 100 - sumNorm;

		const precision = (78.4 + activeCount * 3.1 + (freRound > 0 ? 1.4 : 0)).toFixed(1);
		const cappedPrecision = Math.min(96.8, Number(precision)).toFixed(1);

		return {
			norm,
			precision: cappedPrecision,
			gain: activeCount > 0 ? (Number(cappedPrecision) - 78.4).toFixed(1) : null
		};
	});

	function toggleJudgment(id: string, val: number) {
		freJudgments[id] = freJudgments[id] === val ? 0 : val;
		freRound++;
	}

	function resetFRE() {
		freJudgments = { fre1: 0, fre2: 0, fre3: 0 };
		freRound = 0;
	}

	/* ------------------------------------------------------------------------
	   7. NON-DESTRUCTIVE TRANSFORM STUDIO STATE
	   ------------------------------------------------------------------------ */
	let tfRotate = $state<0 | 90 | 180>(0);
	let tfFlipX = $state(false);
	let tfShear = $state(0);
	let tfAspect = $state<'original' | '1-1' | '16-9'>('original');

	const tfDerivedOps = $derived.by(() => {
		const ops: string[] = [];
		if (tfRotate !== 0) ops.push(`rot${tfRotate}°`);
		if (tfFlipX) ops.push('flipH');
		if (tfShear !== 0) ops.push(`shear${tfShear}°`);
		if (tfAspect !== 'original') ops.push(tfAspect.replace('-', ':'));
		return ops.length ? `Derived Asset (${ops.join(', ')})` : 'Derived Asset (Unmodified)';
	});

	const tfDims = $derived.by(() => {
		if (tfAspect === '1-1') return '900 × 900 px';
		if (tfAspect === '16-9') return '1200 × 675 px';
		return '1200 × 900 px';
	});

	function resetTransform() {
		tfRotate = 0;
		tfFlipX = false;
		tfShear = 0;
		tfAspect = 'original';
	}

	/* ------------------------------------------------------------------------
	   8. REAL APPLICATION SCREENS SHOWCASE (All 9 high-res Screenshots)
	   ------------------------------------------------------------------------ */
	interface AppScreenShowcase {
		id: string;
		title: string;
		badge: string;
		path: string;
		image: string;
		description: string;
		tags: string[];
		highlights: string[];
	}

	const appScreens: AppScreenShowcase[] = [
		{
			id: 'overview',
			title: 'Overview & Sequential Latency Telemetry',
			badge: 'Real-Time SLA & Performance Metrics',
			path: '/dashboard',
			image: '/screenshots/01-Overview-Page.png',
			description:
				'Operational telemetry dashboard tracking sequential CBIR iterations with horizontal average latency reference benchmarks, 100-bin latency distribution histograms, and relevance judgment ratio distributions.',
			tags: ['Sequential Latency AreaChart', 'Average SLA Line', 'Latency Distribution Histogram', 'FRE Relevance Ratio'],
			highlights: ['AreaChart showing sequential retrieval iterations', 'Sub-20ms threshold indicator', 'Descriptor & Modality Split breakdown']
		},
		{
			id: 'query',
			title: 'Visual Query Studio & Similarity Search',
			badge: 'Multi-Descriptor Engine & Top-K',
			path: '/dashboard/query',
			image: '/screenshots/09-retreiving-page.png',
			description:
				'Compose visual similarity queries using uploaded reference images or dataset items. Fine-tune weights across HSV, Moments, Dominant Colors, GLCM, and LBP descriptors, and inspect nearest-neighbor cosine distances.',
			tags: ['5-Descriptor Weight Calibration', 'Cosine & Euclidean Partitions', 'Candidate Scope Filtering', 'Rocchio Relevance Loop'],
			highlights: ['Interactive descriptor sliders with balanced presets', 'Nearest neighbor ranking with distance matrices', 'Direct pivoting into relevance feedback']
		},
		{
			id: 'images',
			title: 'Justified Photo Wall & Batch Operations',
			badge: 'Google Photos Layout Engine',
			path: '/dashboard/images',
			image: '/screenshots/03-Image-list.png',
			description:
				'A responsive justified flex layout preserving native image aspect ratios without distortion. Features hover/tap multi-select checkmarks and a floating batch action bar.',
			tags: ['Aspect Ratio Preserved', 'Multi-Select Checkmarks', 'Batch Collection Assign', 'Batch Delete Modal', 'View Transitions'],
			highlights: ['Zero letterboxing or cropping in grid layout', 'One-click floating batch bar for collections', 'Native View Transitions into detail view']
		},
		{
			id: 'transform',
			title: 'Image Transform Studio & Affine Engine',
			badge: 'Client-Side Canvas 2D',
			path: '/dashboard/transform',
			image: '/screenshots/04-Transform-studio.png',
			description:
				'Interactive non-destructive image pre-processing. Rotate, flip, shear, scale, and crop images to preset ratios before running feature extraction and test transform-invariant similarity retrieval.',
			tags: ['Crop & Aspect Presets', 'Rotate, Flip & Shear', 'Affine Matrix Transforms', 'Asset Lineage Tracking'],
			highlights: ['Live numeric control over affine matrices', 'Lineage tracking linking parent and derived assets', 'Instant re-extraction on modified variations']
		},
		{
			id: 'details',
			title: 'Deep Feature Inspection & Histograms',
			badge: '256 Bins & MiniBatchKMeans (k=5)',
			path: '/dashboard/images/[id]',
			image: '/screenshots/08-image-details-page.png',
			description:
				'Inspect extracted high-dimensional descriptors for any image. Visualizes clustered dominant color centroids via MiniBatchKMeans with exact hex values, alongside full 256-bin continuous HSV frequency curves.',
			tags: ['MiniBatchKMeans (k=5)', 'Exact Hex & Proportions', '256-Bin Continuous HSV Curves', 'GLCM & LBP Texture Vectors'],
			highlights: ['Continuous Hue, Saturation, and Value graphs', 'Copyable hex code chips for dominant palettes', 'One-click similar image retrieval']
		},
		{
			id: 'upload',
			title: 'High-Throughput Batch Upload Queue',
			badge: 'Automated Extraction Pipeline',
			path: '/dashboard/upload',
			image: '/screenshots/05-upload-page.png',
			description:
				'Drag-and-drop batch ingestion with automatic descriptor extraction. Features a toggleable Auto-On descriptor pipeline, target category routing, and real-time per-file progress meters with failure resilience.',
			tags: ['Drag & Drop Multi-file', 'Auto-On Extraction Toggle', 'Target Category Selector', 'Real-time Progress Bars'],
			highlights: ['Automated background feature extraction', 'Folder & category routing on ingest', 'Failure recovery and retry queue']
		},
		{
			id: 'categories',
			title: 'Category Hierarchy & Collections',
			badge: 'Semantic Partitioning',
			path: '/dashboard/categories',
			image: '/screenshots/06-category-page.png',
			description:
				'Organize your visual collection into nested category structures and root partitions. Search categories in real-time, view image assignment counts, and explore categorized assets in clean grids.',
			tags: ['Nested Category Tree', 'Root & Subfolder Partitions', 'Instant Search Filter', 'Coverage KPI Metrics'],
			highlights: ['Tree hierarchy for structured image cataloging', 'Real-time category filtering', 'Semantic class cluster assignments']
		},
		{
			id: 'favorites',
			title: 'Curated Favorites & Visual Bookmarks',
			badge: 'Personalized Collections',
			path: '/dashboard/favorites',
			image: '/screenshots/07-favourite-page.png',
			description:
				'Bookmarked visual assets organized for rapid reference, batch category management, and instant transition to the similarity retrieval pipeline with smooth view transitions.',
			tags: ['One-Click Bookmark Toggle', 'Batch Operations', 'Seamless View Transitions', 'Google Photos Wall'],
			highlights: ['Rapid bookmark toggle on any image', 'Batch assign favorite assets to categories', 'Preserves natural aspect ratios']
		},
		{
			id: 'auth',
			title: 'Secure Authentication & Session Access',
			badge: 'JWT & Access Control',
			path: '/login',
			image: '/screenshots/02-auth-page.png',
			description:
				'Clean authenticated gateway with visual branding, persistent session cookies, and single-click credential verification with automated redirect.',
			tags: ['JWT Token Storage', 'Split Hero Layout', 'Instant Form Validation', 'Secure Cookie Storage'],
			highlights: ['Robust JWT authentication flow', 'Split-screen editorial vector branding', 'Seamless session persistence']
		}
	];

	let activeScreenId = $state('overview');
	const activeScreen = $derived(appScreens.find((s) => s.id === activeScreenId) || appScreens[0]);
	let zoomedImage = $state<string | null>(null);
	let isLightboxOpen = $state(false);

	function openLightbox(img: string) {
		zoomedImage = img;
		isLightboxOpen = true;
	}

	/* ------------------------------------------------------------------------
	   9. GALLERY SHOWCASE & FIND SIMILAR BRIDGE
	   ------------------------------------------------------------------------ */
	let activeCategory = $state('all');
	let galleryDensity = $state<'comfortable' | 'compact'>('comfortable');

	const filteredGallery = $derived(
		activeCategory === 'all'
			? GALLERY_ITEMS
			: GALLERY_ITEMS.filter((item) => item.category === activeCategory)
	);

	function loadPhotoIntoWorkbench(item: GalleryPhoto) {
		if (item.palette && item.candidates) {
			customQueryObj = null;
			activeQueryKey = item.id;
		} else {
			const pool = GALLERY_ITEMS.filter((g) => g.id !== item.id);
			const sameCat = pool.filter((g) => g.category === item.category);
			const others = pool.filter((g) => g.category !== item.category);
			const top4 = [...sameCat, ...others].slice(0, 4).map((g, idx) => ({
				title: g.title,
				file: g.filename,
				url: g.url,
				colorSim: Number((0.95 - idx * 0.03).toFixed(2)),
				texSim: Number((0.88 + (idx % 2) * 0.06 - idx * 0.02).toFixed(2))
			}));

			customQueryObj = {
				id: item.id,
				title: item.title,
				filename: item.filename,
				url: item.url,
				resolution: item.resolution,
				category: item.category,
				dominantHex: item.dominantHex,
				palette: [
					{ hex: item.dominantHex || '#4A80D4', pct: 38, rgb: '74, 128, 212' },
					{ hex: '#2B303A', pct: 22, rgb: '43, 48, 58' },
					{ hex: '#7A7870', pct: 18, rgb: '122, 120, 112' },
					{ hex: '#D4A373', pct: 13, rgb: '212, 163, 115' },
					{ hex: '#E9ECEF', pct: 9, rgb: '233, 236, 239' }
				],
				candidates: top4
			};
		}

		if (typeof document !== 'undefined') {
			const wb = document.getElementById('workbench');
			if (wb) wb.scrollIntoView({ behavior: 'smooth', block: 'center' });
		}
		showToast(`Loaded "${item.filename}" into Visual Query Workbench`);
	}

	/* ------------------------------------------------------------------------
	   10. CLOSING BAND LOCAL DRAG-AND-DROP
	   ------------------------------------------------------------------------ */
	let isDragOver = $state(false);
	let fileInputEl = $state<HTMLInputElement | null>(null);

	function handleLocalFile(file: File) {
		if (!file || !file.type.startsWith('image/')) {
			showToast('Please select a valid image file (JPG, PNG, WEBP).');
			return;
		}
		const objectUrl = URL.createObjectURL(file);
		loadPhotoIntoWorkbench({
			id: 'local-upload',
			title: file.name,
			filename: file.name,
			category: 'Landscapes',
			resolution: 'Custom Upload',
			dominantHex: '#3B82F6',
			url: objectUrl
		});
	}

	function onFileInputChange(e: Event & { currentTarget: HTMLInputElement }) {
		if (e.currentTarget.files && e.currentTarget.files[0]) {
			handleLocalFile(e.currentTarget.files[0]);
		}
	}

	function onDrop(e: DragEvent) {
		e.preventDefault();
		isDragOver = false;
		if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files[0]) {
			handleLocalFile(e.dataTransfer.files[0]);
		}
	}
</script>

<svelte:head>
	<title>Perceptra — Content-Based Image Retrieval &amp; Visual Discovery</title>
	<meta
		name="description"
		content="Search images by what they actually look like. Multi-descriptor visual retrieval with 768-D HSV histograms, MiniBatchKMeans dominant colors, GLCM/LBP texture matrices, and Feature Relevance Estimation."
	/>
</svelte:head>

<div class="min-h-screen bg-background text-foreground antialiased flex flex-col">
	<!-- ========================================================================
	     1. STICKY NAVIGATION BAR
	     ======================================================================== -->
	<header class="sticky top-0 z-50 h-16 w-full border-b border-border bg-background/85 backdrop-blur-md transition-colors">
		<div class="container mx-auto flex h-full max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
			<a href="#workbench" class="flex items-center gap-2.5 text-foreground hover:opacity-90 transition-opacity">
				<svg class="size-7 shrink-0 text-primary" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
					<rect x="33" y="13" width="13.5" height="13.5" rx="3.2" fill="currentColor" />
					<rect x="44" y="30" width="14.5" height="14.5" rx="3.4" fill="currentColor" />
					<rect x="28" y="44" width="13.5" height="13.5" rx="3.2" fill="currentColor" />
					<rect x="13" y="57" width="13.5" height="13.5" rx="3.2" fill="currentColor" />
					<path
						d="M60.5 13H74.5C87.8 13 96 22.8 96 36.5C96 50.2 87.2 60.5 73.5 60.5H59.5C56.5 60.5 54.5 62.5 54.5 65.5V72.5C54.5 81.2 47.2 88.5 38.5 88.5H37.8C36.2 88.5 35 87.3 35 85.7V75.5H29.8C27.8 75.5 26.5 74.2 26.5 72.2V70.3C26.5 68.3 27.8 67 29.8 67H35V60.2C35 56.8 37.5 54.5 41 54.5H48.5C50.4 54.5 51.8 53.1 51.8 51.2V49.2C51.8 46.8 53.7 45 56.2 45H70.8C76.2 45 79.8 41.4 79.8 36.5C79.8 31.6 76.2 28 70.8 28H60.5C57.5 28 55.5 26 55.5 23V18C55.5 15 57.5 13 60.5 13Z"
						fill="currentColor"
					/>
				</svg>
				<span class="text-lg font-bold tracking-tight">Perceptra</span>
			</a>

			<nav class="hidden md:flex items-center gap-7 text-sm font-medium text-muted-foreground" aria-label="Primary Navigation">
				<a href="#descriptors" class="hover:text-foreground transition-colors">Descriptors</a>
				<a href="#workbench" class="hover:text-foreground transition-colors">Query Studio</a>
				<a href="#transform" class="hover:text-foreground transition-colors">Transform</a>
				<a href="#screens" class="hover:text-foreground transition-colors">Platform Screens</a>
				<a href="#gallery" class="hover:text-foreground transition-colors">Gallery</a>
			</nav>

			<div class="flex items-center gap-2">
				<!-- Language Switcher -->
				<Button
					variant="outline"
					size="icon"
					class="size-8"
					onclick={() => locale.toggle()}
					title={m.nav_toggle_language()}
					aria-label={m.nav_toggle_language()}
				>
					<GlobeIcon class="size-4" />
				</Button>

				<!-- Theme Toggle -->
				<ThemeToggle />

				{#if currentUser}
					<Button href="/dashboard" size="sm" class="ml-1 gap-1.5 shadow-xs">
						<span>Dashboard</span>
						<ArrowRightIcon class="size-3.5" />
					</Button>
				{:else}
					<Button href="/login" variant="ghost" size="sm">
						Sign In
					</Button>
					<Button href="/dashboard/query" size="sm" class="ml-1 gap-1.5 shadow-xs">
						<span>Launch Studio</span>
						<ArrowRightIcon class="size-3.5" />
					</Button>
				{/if}
			</div>
		</div>
	</header>

	<main class="flex-1">
		<!-- ======================================================================
		     2. HERO SECTION (ASYMMETRIC 12-COLUMN SPLIT)
		     ====================================================================== -->
		<section class="py-12 sm:py-16 lg:py-20 border-b border-border">
			<div class="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
				<div class="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
					<!-- Left Column (5 cols) -->
					<div class="lg:col-span-5 flex flex-col items-start text-left">
						<Badge variant="secondary" class="mb-5 gap-2 px-3 py-1 font-mono text-[11px] font-medium tracking-wide border border-border">
							<span class="size-2 rounded-full bg-primary inline-block animate-pulse"></span>
							<span>CBIR ENGINE · MULTI-DESCRIPTOR RETRIEVAL</span>
						</Badge>

						<h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold tracking-tight text-foreground leading-[1.1] mb-5">
							Search images by what they actually look like.
						</h1>

						<p class="text-base sm:text-lg text-muted-foreground leading-relaxed max-w-xl mb-7">
							Perceptra indexes visual archives through 768-D HSV color histograms, MiniBatchKMeans dominant palettes, and GLCM/LBP texture matrices. Refine nearest-neighbor rankings in milliseconds with iterative Feature Relevance Estimation—zero manual tagging required.
						</p>

						<div class="flex flex-wrap items-center gap-3 mb-8">
							<Button href="#workbench" size="default" class="gap-2 shadow-sm">
								<span>Start Visual Query</span>
								<ArrowRightIcon class="size-4" />
							</Button>
							<Button href="#screens" variant="outline" size="default" class="shadow-2xs">
								Platform Tour
							</Button>
						</div>

						<div class="w-full pt-5 border-t border-border flex flex-wrap items-center gap-x-3 gap-y-2 font-mono text-xs text-muted-foreground">
							<span>5 Descriptors</span>
							<span class="text-border">|</span>
							<span>768-D HSV</span>
							<span class="text-border">|</span>
							<span>MiniBatchKMeans</span>
							<span class="text-border">|</span>
							<span>FRE Re-Ranking</span>
						</div>
					</div>

					<!-- Right Column (7 cols): Live Visual Query Workbench -->
					<div id="workbench" class="lg:col-span-7">
						<Card.Root class="shadow-md border-border bg-card overflow-hidden">
							<Card.Header class="p-4 sm:p-5 pb-3 border-b border-border">
								<div class="flex flex-wrap items-center justify-between gap-3">
									<div class="flex items-center gap-1.5 p-1 rounded-lg bg-muted/60 border border-border">
										<Button
											type="button"
											variant={activeQueryKey === 'terraced' && !customQueryObj ? 'secondary' : 'ghost'}
											size="sm"
											class="h-7 text-xs font-medium px-2.5 {activeQueryKey === 'terraced' && !customQueryObj ? 'shadow-2xs' : ''}"
											onclick={() => selectQueryTab('terraced')}
										>
											Terraced Fields
										</Button>
										<Button
											type="button"
											variant={activeQueryKey === 'temple' && !customQueryObj ? 'secondary' : 'ghost'}
											size="sm"
											class="h-7 text-xs font-medium px-2.5 {activeQueryKey === 'temple' && !customQueryObj ? 'shadow-2xs' : ''}"
											onclick={() => selectQueryTab('temple')}
										>
											Imperial Temple
										</Button>
										<Button
											type="button"
											variant={activeQueryKey === 'autumn' && !customQueryObj ? 'secondary' : 'ghost'}
											size="sm"
											class="h-7 text-xs font-medium px-2.5 {activeQueryKey === 'autumn' && !customQueryObj ? 'shadow-2xs' : ''}"
											onclick={() => selectQueryTab('autumn')}
										>
											Autumn Canopy
										</Button>
									</div>

									<Badge variant="outline" class="font-mono text-xs gap-1.5 px-2.5 py-1">
										<span>Cosine</span>
										<span class="font-semibold text-emerald-600 dark:text-emerald-400">{simulatedLatency} ms</span>
									</Badge>
								</div>
							</Card.Header>

							<Card.Content class="p-4 sm:p-5">
								<div class="grid grid-cols-1 sm:grid-cols-12 gap-5">
									<!-- Query Reference & Weight Controls (5 cols) -->
									<div class="sm:col-span-5 flex flex-col gap-4 p-3 rounded-lg bg-muted/40 border border-border/60">
										<div class="relative aspect-4/3 w-full rounded-md overflow-hidden bg-muted border border-border/80">
											<img src={activeQueryData.url} alt={activeQueryData.title} class="size-full object-cover" />
											<span class="absolute bottom-2 left-2 font-mono text-[10px] bg-background/85 text-foreground px-2 py-0.5 rounded backdrop-blur-xs shadow-xs border border-border/50">
												{activeQueryData.filename}
											</span>
										</div>

										<!-- 5-Cluster Dominant Color Strip -->
										<div class="flex flex-col gap-1.5">
											<div class="flex justify-between items-center text-[11px] font-mono text-muted-foreground">
												<span>DOMINANT PALETTE</span>
												<span>k=5</span>
											</div>
											<div class="flex h-2.5 w-full rounded-full overflow-hidden border border-border/70" aria-label="Dominant color proportions">
												{#each workbenchPalette as c}
													<div class="h-full transition-all duration-300" style="width:{c.pct}%; background-color:{c.hex};" title="{c.hex} ({c.pct}%)"></div>
												{/each}
											</div>
										</div>

										<!-- Weight Presets & Sliders -->
										<div class="flex flex-col gap-3 pt-2 border-t border-border/60">
											<div class="flex items-center gap-1.5">
												<Button
													type="button"
													variant={activePreset === 'balanced' ? 'default' : 'outline'}
													size="sm"
													class="h-6 text-[11px] px-2"
													onclick={() => setQueryPreset('balanced')}
												>
													Balanced
												</Button>
												<Button
													type="button"
													variant={activePreset === 'color' ? 'default' : 'outline'}
													size="sm"
													class="h-6 text-[11px] px-2"
													onclick={() => setQueryPreset('color')}
												>
													Color
												</Button>
												<Button
													type="button"
													variant={activePreset === 'texture' ? 'default' : 'outline'}
													size="sm"
													class="h-6 text-[11px] px-2"
													onclick={() => setQueryPreset('texture')}
												>
													Texture
												</Button>
											</div>

											<div class="space-y-1.5">
												<div class="flex justify-between text-xs font-medium">
													<span class="text-primary">Color Weight</span>
													<span class="font-mono text-muted-foreground">{colorWeight}%</span>
												</div>
												<Slider
													type="single"
													bind:value={colorWeight}
													min={0}
													max={100}
													step={1}
													class="cursor-pointer"
												/>
											</div>

											<div class="flex justify-between text-xs font-medium text-muted-foreground">
												<span>Texture Weight (Inverse)</span>
												<span class="font-mono">{textureWeight}%</span>
											</div>
										</div>
									</div>

									<!-- Ranked Candidates Grid (7 cols) -->
									<div class="sm:col-span-7 flex flex-col gap-3">
										<div class="flex justify-between items-center text-xs font-mono text-muted-foreground pb-1">
											<span>TOP-4 RETRIEVED NEIGHBORS</span>
											<span>GHIM-10K · Cosine</span>
										</div>

										<div class="grid grid-cols-2 gap-3">
											{#each rankedWorkbenchCandidates as cand, idx}
												<div class="group flex flex-col gap-2 p-2 rounded-lg bg-card border border-border shadow-2xs hover:shadow-sm transition-all text-left">
													<div class="relative aspect-4/3 w-full rounded-md overflow-hidden bg-muted">
														<img src={cand.url} alt={cand.title} loading="lazy" class="size-full object-cover group-hover:scale-105 transition-transform duration-300" />
														<Badge class="absolute top-1.5 left-1.5 h-4.5 px-1.5 text-[10px] font-mono">
															#{idx + 1}
														</Badge>
														<span class="absolute top-1.5 right-1.5 font-mono text-[10px] bg-background/90 text-foreground px-1.5 py-0.5 rounded backdrop-blur-xs font-medium border border-border/40">
															{cand.score.toFixed(1)}%
														</span>
													</div>
													<div class="flex flex-col px-0.5">
														<span class="text-xs font-medium truncate text-foreground" title={cand.title}>{cand.title}</span>
														<span class="text-[10px] font-mono text-muted-foreground">{cand.file}</span>
													</div>
												</div>
											{/each}
										</div>
									</div>
								</div>
							</Card.Content>
						</Card.Root>
					</div>
				</div>
			</div>
		</section>

		<!-- ======================================================================
		     3. MULTI-DESCRIPTOR ARCHITECTURE (#descriptors)
		     ====================================================================== -->
		<section id="descriptors" class="py-16 sm:py-20 border-b border-border">
			<div class="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
				<div class="max-w-3xl mb-12 text-left">
					<Badge variant="outline" class="mb-3 font-mono text-[11px] uppercase tracking-wider">
						Descriptor Pipeline
					</Badge>
					<h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-foreground mb-4">
						Five complementary visual signatures, fused into one query vector.
					</h2>
					<p class="text-muted-foreground text-base sm:text-lg leading-relaxed">
						Every ingested image is decomposed into continuous color distributions, perceptual centroids, and spatial texture matrices—enabling precise retrieval across lighting, scale, and structural variations.
					</p>
				</div>

				<!-- Bento Grid -->
				<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
					<!-- Panel A: Interactive HSV 256-Bin Chart (7 cols) -->
					<Card.Root class="lg:col-span-7 shadow-xs border-border bg-card">
						<Card.Header class="p-5 pb-3">
							<div class="flex flex-wrap items-center justify-between gap-3">
								<div>
									<Card.Title class="text-lg font-semibold">HSV Color Distribution (256 Bins)</Card.Title>
									<Card.Description class="text-xs">Continuous frequency curves for Hue, Saturation, and Value channels.</Card.Description>
								</div>

								<div class="flex items-center gap-1 p-0.5 rounded-lg bg-muted/60 border border-border">
									<Button
										type="button"
										variant={activeHsvFilter === 'all' ? 'secondary' : 'ghost'}
										size="sm"
										class="h-6 text-xs px-2"
										onclick={() => (activeHsvFilter = 'all')}
									>
										All
									</Button>
									<Button
										type="button"
										variant={activeHsvFilter === 'h' ? 'secondary' : 'ghost'}
										size="sm"
										class="h-6 text-xs px-2"
										onclick={() => (activeHsvFilter = 'h')}
									>
										Hue
									</Button>
									<Button
										type="button"
										variant={activeHsvFilter === 's' ? 'secondary' : 'ghost'}
										size="sm"
										class="h-6 text-xs px-2"
										onclick={() => (activeHsvFilter = 's')}
									>
										Sat
									</Button>
									<Button
										type="button"
										variant={activeHsvFilter === 'v' ? 'secondary' : 'ghost'}
										size="sm"
										class="h-6 text-xs px-2"
										onclick={() => (activeHsvFilter = 'v')}
									>
										Val
									</Button>
								</div>
							</div>
						</Card.Header>

						<Card.Content class="p-5 pt-1 flex flex-col gap-4">
							<div class="relative w-full rounded-lg bg-muted/30 border border-border p-3 overflow-hidden">
								<svg
									class="w-full h-48 cursor-crosshair overflow-visible"
									role="img"
									viewBox="0 0 640 210"
									preserveAspectRatio="none"
									aria-label="HSV 256-bin frequency chart"
									onmousemove={handleHsvMouseMove}
								>
									<!-- Horizontal Reference Lines -->
									<line x1="0" y1="42" x2="640" y2="42" stroke="currentColor" class="text-border" stroke-dasharray="3 4" />
									<line x1="0" y1="96" x2="640" y2="96" stroke="currentColor" class="text-border" stroke-dasharray="3 4" />
									<line x1="0" y1="150" x2="640" y2="150" stroke="currentColor" class="text-border" stroke-dasharray="3 4" />
									<line x1="0" y1="196" x2="640" y2="196" stroke="currentColor" class="text-border" />

									<!-- Area Fills -->
									<path class="transition-opacity duration-200" fill="var(--chart-1)" fill-opacity="0.15" d={pathAreaH} style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 'h' ? 1 : 0};"></path>
									<path class="transition-opacity duration-200" fill="var(--chart-3)" fill-opacity="0.15" d={pathAreaS} style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 's' ? 1 : 0};"></path>
									<path class="transition-opacity duration-200" fill="var(--chart-2)" fill-opacity="0.15" d={pathAreaV} style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 'v' ? 1 : 0};"></path>

									<!-- Frequency Curves -->
									<path class="transition-opacity duration-200" fill="none" stroke="var(--chart-1)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d={pathCurveH} style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 'h' ? 1 : 0.12};"></path>
									<path class="transition-opacity duration-200" fill="none" stroke="var(--chart-3)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d={pathCurveS} style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 's' ? 1 : 0.12};"></path>
									<path class="transition-opacity duration-200" fill="none" stroke="var(--chart-2)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d={pathCurveV} style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 'v' ? 1 : 0.12};"></path>

									<!-- Cursor & Intersection Dots -->
									<line x1={cursorX.toFixed(1)} y1="8" x2={cursorX.toFixed(1)} y2="196" stroke="currentColor" class="text-muted-foreground" stroke-width="1" stroke-dasharray="3 3" opacity="0.65" />
									<circle cx={cursorX.toFixed(1)} cy={dotHY.toFixed(1)} r="3.5" fill="var(--chart-1)" style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 'h' ? 1 : 0.15};" />
									<circle cx={cursorX.toFixed(1)} cy={dotSY.toFixed(1)} r="3.5" fill="var(--chart-3)" style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 's' ? 1 : 0.15};" />
									<circle cx={cursorX.toFixed(1)} cy={dotVY.toFixed(1)} r="3.5" fill="var(--chart-2)" style="opacity: {activeHsvFilter === 'all' || activeHsvFilter === 'v' ? 1 : 0.15};" />
								</svg>

								<!-- Tooltip Readout -->
								<div class="absolute top-3 right-3 p-2.5 rounded-md bg-background/95 border border-border shadow-sm text-xs font-mono pointer-events-none min-w-36">
									<div class="text-muted-foreground mb-1">Bin {cursorBin + 1} (of 256)</div>
									<div class="flex justify-between gap-4"><span style="color:var(--chart-1);">Hue</span><span>{hsvData.h[cursorBin].toFixed(3)}</span></div>
									<div class="flex justify-between gap-4"><span style="color:var(--chart-3);">Sat</span><span>{hsvData.s[cursorBin].toFixed(3)}</span></div>
									<div class="flex justify-between gap-4"><span style="color:var(--chart-2);">Val</span><span>{hsvData.v[cursorBin].toFixed(3)}</span></div>
								</div>
							</div>

							<div class="flex flex-wrap justify-between items-center text-xs font-mono text-muted-foreground pt-1 border-t border-border/60">
								<span>Peak Hue: <strong class="text-foreground">16.91%</strong> · Peak Sat: <strong class="text-foreground">3.27%</strong></span>
								<span>Resolution: 256 bins · Vector: 768-D (L1)</span>
							</div>
						</Card.Content>
					</Card.Root>

					<!-- Panel B: Dominant Colors Clustered Analysis (5 cols) -->
					<Card.Root class="lg:col-span-5 shadow-xs border-border bg-card">
						<Card.Header class="p-5 pb-3">
							<div class="flex flex-wrap items-center justify-between gap-3">
								<div>
									<Card.Title class="text-lg font-semibold">Dominant Colors Analysis</Card.Title>
									<Card.Description class="text-xs">Perceptual centroids via MiniBatchKMeans.</Card.Description>
								</div>

								<div class="flex items-center gap-1 p-0.5 rounded-lg bg-muted/60 border border-border">
									<Button
										type="button"
										variant={kmeansK === 5 ? 'secondary' : 'ghost'}
										size="sm"
										class="h-6 text-xs px-2"
										onclick={() => (kmeansK = 5)}
									>
										k=5
									</Button>
									<Button
										type="button"
										variant={kmeansK === 8 ? 'secondary' : 'ghost'}
										size="sm"
										class="h-6 text-xs px-2"
										onclick={() => (kmeansK = 8)}
									>
										k=8
									</Button>
								</div>
							</div>
						</Card.Header>

						<Card.Content class="p-5 pt-1 flex flex-col gap-4">
							<div class="flex flex-col gap-1.5">
								<div class="flex justify-between items-center text-[11px] font-mono text-muted-foreground">
									<span>CLUSTER PROPORTIONS</span>
									<span>{kmeansK} Clusters · 100%</span>
								</div>
								<div class="flex h-3 w-full rounded-full overflow-hidden border border-border">
									{#each activeClusters as c}
										<div class="h-full transition-all duration-300" style="width:{c.pct}%; background-color:{c.hex};" title="{c.hex} ({c.pct}%)"></div>
									{/each}
								</div>
							</div>

							<div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
								{#each activeClusters as c}
									<button
										type="button"
										class="flex flex-col gap-1 p-2 rounded-lg bg-muted/40 border border-border/80 hover:border-primary/50 text-left transition-colors cursor-pointer group"
										onclick={() => copyText(c.hex)}
										title="Click to copy {c.hex}"
									>
										<div class="flex items-center justify-between gap-1.5">
											<span class="size-3 rounded-full border border-border/60 shrink-0" style="background-color:{c.hex};"></span>
											<span class="font-mono text-xs font-semibold text-foreground">{c.pct.toFixed(1)}%</span>
										</div>
										<span class="font-mono text-[11px] text-muted-foreground group-hover:text-foreground">{c.hex}</span>
										<span class="font-mono text-[10px] text-muted-foreground/80">rgb({c.rgb})</span>
									</button>
								{/each}
							</div>

							<div class="flex justify-between items-center text-xs font-mono text-muted-foreground pt-3 border-t border-border/60 mt-auto">
								<span>Click swatch to copy HEX</span>
								<span>Space: CIELAB / sRGB</span>
							</div>
						</Card.Content>
					</Card.Root>
				</div>

				<!-- Compact Technical Strip: Color Moments, GLCM, LBP -->
				<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
					<!-- Color Moments -->
					<Card.Root class="shadow-xs border-border bg-card">
						<Card.Header class="p-4 pb-2">
							<div class="flex justify-between items-center">
								<div class="flex items-center gap-2">
									<span class="size-2.5 rounded-full" style="background-color: var(--chart-2);"></span>
									<span class="font-semibold text-sm">Color Moments</span>
								</div>
								<Badge variant="outline" class="font-mono text-[10px]">9-D · Global</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-4 pt-1 flex flex-col gap-3">
							<p class="text-xs text-muted-foreground leading-relaxed">
								First three statistical moments across H, S, V channels capturing chromatic balance and exposure.
							</p>
							<div class="grid grid-cols-3 gap-2 pt-2 border-t border-border/60 font-mono text-center">
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Mean</span><span class="text-xs font-semibold text-foreground">0.482</span></div>
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Std Dev</span><span class="text-xs font-semibold text-foreground">0.214</span></div>
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Skew</span><span class="text-xs font-semibold text-foreground">+0.341</span></div>
							</div>
						</Card.Content>
					</Card.Root>

					<!-- GLCM Texture -->
					<Card.Root class="shadow-xs border-border bg-card">
						<Card.Header class="p-4 pb-2">
							<div class="flex justify-between items-center">
								<div class="flex items-center gap-2">
									<span class="size-2.5 rounded-full" style="background-color: var(--chart-4);"></span>
									<span class="font-semibold text-sm">GLCM Texture</span>
								</div>
								<Badge variant="outline" class="font-mono text-[10px]">24-D · 4 Angles</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-4 pt-1 flex flex-col gap-3">
							<p class="text-xs text-muted-foreground leading-relaxed">
								Gray-Level Co-occurrence spatial statistics quantifying surface roughness, contrast, and periodicity.
							</p>
							<div class="grid grid-cols-3 gap-2 pt-2 border-t border-border/60 font-mono text-center">
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Contrast</span><span class="text-xs font-semibold text-foreground">14.28</span></div>
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Homog.</span><span class="text-xs font-semibold text-foreground">0.794</span></div>
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Energy</span><span class="text-xs font-semibold text-foreground">0.312</span></div>
							</div>
						</Card.Content>
					</Card.Root>

					<!-- LBP Texture -->
					<Card.Root class="shadow-xs border-border bg-card">
						<Card.Header class="p-4 pb-2">
							<div class="flex justify-between items-center">
								<div class="flex items-center gap-2">
									<span class="size-2.5 rounded-full" style="background-color: var(--chart-5);"></span>
									<span class="font-semibold text-sm">LBP Texture</span>
								</div>
								<Badge variant="outline" class="font-mono text-[10px]">128-D · Uniform</Badge>
							</div>
						</Card.Header>
						<Card.Content class="p-4 pt-1 flex flex-col gap-3">
							<p class="text-xs text-muted-foreground leading-relaxed">
								Rotation-invariant Local Binary Patterns encoding micro-edges, foliage grain, and fine surface details.
							</p>
							<div class="grid grid-cols-3 gap-2 pt-2 border-t border-border/60 font-mono text-center">
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Radius</span><span class="text-xs font-semibold text-foreground">R=2 px</span></div>
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Neighbors</span><span class="text-xs font-semibold text-foreground">P=16</span></div>
								<div class="flex flex-col"><span class="text-[10px] text-muted-foreground">Entropy</span><span class="text-xs font-semibold text-foreground">4.82 b</span></div>
							</div>
						</Card.Content>
					</Card.Root>
				</div>
			</div>
		</section>

		<!-- ======================================================================
		     4. INTERACTIVE WORKFLOW SECTION (#studio & #transform)
		     ====================================================================== -->
		<section class="py-16 sm:py-20 border-b border-border">
			<div class="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
				<div class="max-w-3xl mb-12 text-left">
					<Badge variant="outline" class="mb-3 font-mono text-[11px] uppercase tracking-wider">
						Interactive Workflows
					</Badge>
					<h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-foreground mb-4">
						Steer retrieval precision and prepare derived assets in place.
					</h2>
					<p class="text-muted-foreground text-base sm:text-lg leading-relaxed">
						Test Perceptra’s Feature Relevance Estimation feedback loop and non-destructive client-side image transform studio right on this page.
					</p>
				</div>

				<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
					<!-- Left: Feature Relevance Estimation (FRE) Mini-Demo -->
					<Card.Root id="studio" class="shadow-xs border-border bg-card">
						<Card.Header class="p-5 pb-3">
							<div class="flex items-center justify-between">
								<div>
									<Card.Title class="text-lg font-semibold">Feature Relevance Estimation (FRE)</Card.Title>
									<Card.Description class="text-xs">Mark candidates relevant or irrelevant to calibrate descriptor weights.</Card.Description>
								</div>
								<Button variant="ghost" size="sm" class="h-8 text-xs gap-1" onclick={resetFRE}>
									<RefreshCwIcon class="size-3.5" />
									<span>Reset</span>
								</Button>
							</div>
						</Card.Header>

						<Card.Content class="p-5 pt-1 flex flex-col gap-4">
							<div class="flex justify-between items-center p-2.5 rounded-lg bg-muted/40 border border-border font-mono text-xs">
								<span>Round: <strong class="text-foreground">{freRound}</strong></span>
								<span>mAP@20: <strong class="text-emerald-600 dark:text-emerald-400 font-semibold">{freWeights.precision}%</strong></span>
							</div>

							<!-- 3 Retrieved Images with Feedback Actions -->
							<div class="grid grid-cols-3 gap-3">
								{#each FRE_ITEMS as item}
									{@const j = freJudgments[item.id] || 0}
									<div class="flex flex-col gap-2 p-2 rounded-lg bg-muted/30 border transition-all {j === 1 ? 'border-emerald-500 bg-emerald-500/5' : j === -1 ? 'border-destructive bg-destructive/5 opacity-80' : 'border-border'}">
										<div class="aspect-4/3 w-full rounded-md overflow-hidden bg-muted">
											<img src={item.url} alt={item.title} loading="lazy" class="size-full object-cover" />
										</div>
										<span class="text-xs font-medium truncate px-0.5 text-foreground">{item.title}</span>
										<div class="grid grid-cols-2 gap-1.5">
											<Button
												type="button"
												variant={j === 1 ? 'default' : 'outline'}
												size="sm"
												class="h-7 text-xs {j === 1 ? 'bg-emerald-600 hover:bg-emerald-700 text-white' : ''}"
												onclick={() => toggleJudgment(item.id, 1)}
												title="Relevant (+)"
											>
												+
											</Button>
											<Button
												type="button"
												variant={j === -1 ? 'destructive' : 'outline'}
												size="sm"
												class="h-7 text-xs"
												onclick={() => toggleJudgment(item.id, -1)}
												title="Irrelevant (-)"
											>
												−
											</Button>
										</div>
									</div>
								{/each}
							</div>

							<!-- 5-Segment Dynamic Weights Bar -->
							<div class="flex flex-col gap-1.5 pt-2">
								<div class="flex justify-between items-center text-[11px] font-mono text-muted-foreground">
									<span>ADAPTIVE WEIGHTS</span>
									<span>{freWeights.gain ? `+${freWeights.gain}% mAP gain` : 'Baseline Weights'}</span>
								</div>
								<div class="flex h-3 w-full rounded-full overflow-hidden border border-border">
									{#each FRE_CHANNELS as ch}
										<div class="h-full transition-all duration-300" style="width:{freWeights.norm[ch.key]}%; background-color:{ch.color};" title="{ch.label}: {freWeights.norm[ch.key]}%"></div>
									{/each}
								</div>
								<div class="flex flex-wrap gap-x-3 gap-y-1 text-[11px] font-mono text-muted-foreground pt-1">
									{#each FRE_CHANNELS as ch}
										<span class="inline-flex items-center gap-1.5">
											<span class="size-2 rounded-full" style="background-color:{ch.color};"></span>
											{ch.label} {freWeights.norm[ch.key]}%
										</span>
									{/each}
								</div>
							</div>
						</Card.Content>
					</Card.Root>

					<!-- Right: Non-Destructive Image Transform Studio Mini-Demo -->
					<Card.Root id="transform" class="shadow-xs border-border bg-card">
						<Card.Header class="p-5 pb-3">
							<div class="flex items-center justify-between">
								<div>
									<Card.Title class="text-lg font-semibold">Transform Studio</Card.Title>
									<Card.Description class="text-xs">Rotate, mirror flip, shear, and aspect crop with asset lineage.</Card.Description>
								</div>
								<Button variant="ghost" size="sm" class="h-8 text-xs gap-1" onclick={resetTransform}>
									<RefreshCwIcon class="size-3.5" />
									<span>Reset</span>
								</Button>
							</div>
						</Card.Header>

						<Card.Content class="p-5 pt-1 flex flex-col gap-4">
							<div class="h-52 w-full rounded-lg bg-muted/40 border border-border flex items-center justify-center p-3 overflow-hidden">
								<div
									class="rounded-md overflow-hidden bg-background shadow-xs transition-all duration-200"
									style="
										aspect-ratio: {tfAspect === '1-1' ? '1/1' : tfAspect === '16-9' ? '16/9' : '4/3'};
										width: {tfAspect === '1-1' ? '170px' : tfAspect === '16-9' ? '250px' : '200px'};
									"
								>
									<img
										src="https://images.unsplash.com/photo-1508804185872-d7badad00f7d?auto=format&fit=crop&w=800&q=80"
										alt="Temple preview"
										class="size-full object-cover transition-transform duration-200"
										style="transform: rotate({tfRotate}deg) scaleX({tfFlipX ? -1 : 1}) skewX({tfShear}deg);"
									/>
								</div>
							</div>

							<!-- Controls -->
							<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
								<div class="flex flex-col gap-1.5">
									<span class="font-medium text-muted-foreground">Rotation</span>
									<div class="flex items-center gap-1">
										<Button
											type="button"
											variant={tfRotate === 0 ? 'default' : 'outline'}
											size="sm"
											class="h-7 text-xs flex-1"
											onclick={() => (tfRotate = 0)}
										>
											0°
										</Button>
										<Button
											type="button"
											variant={tfRotate === 90 ? 'default' : 'outline'}
											size="sm"
											class="h-7 text-xs flex-1"
											onclick={() => (tfRotate = 90)}
										>
											90°
										</Button>
										<Button
											type="button"
											variant={tfRotate === 180 ? 'default' : 'outline'}
											size="sm"
											class="h-7 text-xs flex-1"
											onclick={() => (tfRotate = 180)}
										>
											180°
										</Button>
									</div>
								</div>

								<div class="flex flex-col gap-1.5">
									<span class="font-medium text-muted-foreground">Aspect Crop</span>
									<div class="flex items-center gap-1">
										<Button
											type="button"
											variant={tfAspect === 'original' ? 'default' : 'outline'}
											size="sm"
											class="h-7 text-xs flex-1"
											onclick={() => (tfAspect = 'original')}
										>
											Orig
										</Button>
										<Button
											type="button"
											variant={tfAspect === '1-1' ? 'default' : 'outline'}
											size="sm"
											class="h-7 text-xs flex-1"
											onclick={() => (tfAspect = '1-1')}
										>
											1:1
										</Button>
										<Button
											type="button"
											variant={tfAspect === '16-9' ? 'default' : 'outline'}
											size="sm"
											class="h-7 text-xs flex-1"
											onclick={() => (tfAspect = '16-9')}
										>
											16:9
										</Button>
									</div>
								</div>
							</div>

							<div class="flex items-center justify-between gap-4 pt-1">
								<Button
									type="button"
									variant={tfFlipX ? 'default' : 'outline'}
									size="sm"
									class="h-7 text-xs gap-1.5"
									onclick={() => (tfFlipX = !tfFlipX)}
								>
									<FlipHorizontalIcon class="size-3.5" />
									<span>Flip Horizontal</span>
								</Button>

								<div class="flex items-center gap-2 flex-1 max-w-xs">
									<span class="text-xs font-mono text-muted-foreground shrink-0">Shear: {tfShear}°</span>
									<Slider
										type="single"
										bind:value={tfShear}
										min={-15}
										max={15}
										step={1}
										class="cursor-pointer"
									/>
								</div>
							</div>

							<div class="flex justify-between items-center text-xs font-mono text-muted-foreground p-2 rounded bg-muted/40 border border-border">
								<span>12_6023.jpg → <strong class="text-foreground">{tfDerivedOps}</strong></span>
								<span>{tfDims}</span>
							</div>
						</Card.Content>
					</Card.Root>
				</div>
			</div>
		</section>

		<!-- ======================================================================
		     5. REAL APPLICATION SCREENS SHOWCASE (#screens)
		     ====================================================================== -->
		<section id="screens" class="py-16 sm:py-20 border-b border-border bg-muted/20">
			<div class="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
				<div class="max-w-3xl mb-10 text-left">
					<Badge variant="outline" class="mb-3 font-mono text-[11px] uppercase tracking-wider">
						Platform Tour
					</Badge>
					<h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-foreground mb-4">
						Production Interface &amp; Integrated Modules.
					</h2>
					<p class="text-muted-foreground text-base sm:text-lg leading-relaxed">
						Inspect the 9 production interfaces powering Perceptra’s content-based image retrieval platform—from telemetry dashboards and similarity studios to non-destructive transforms.
					</p>
				</div>

				<!-- Screen Selector Tabs -->
				<div class="flex items-center gap-1.5 overflow-x-auto pb-3 mb-6 scrollbar-none">
					{#each appScreens as s}
						<Button
							type="button"
							variant={activeScreenId === s.id ? 'default' : 'outline'}
							size="sm"
							class="text-xs h-8 whitespace-nowrap shadow-2xs"
							onclick={() => (activeScreenId = s.id)}
						>
							<span>{s.title.split('&')[0].trim()}</span>
						</Button>
					{/each}
				</div>

				<!-- Featured Screen Card -->
				<Card.Root class="shadow-md border-border bg-card mb-8 overflow-hidden">
					<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center p-5 sm:p-6">
						<!-- Screenshot Preview Column (7 cols) -->
						<div class="lg:col-span-7">
							<button
								type="button"
								class="group relative w-full aspect-16/9 rounded-lg overflow-hidden border border-border bg-muted cursor-zoom-in block text-left"
								onclick={() => openLightbox(activeScreen.image)}
								aria-label="Inspect screenshot in full size"
							>
								<img src={activeScreen.image} alt={activeScreen.title} class="size-full object-cover group-hover:scale-[1.02] transition-transform duration-300" />
								<div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
									<Badge variant="secondary" class="gap-1.5 shadow-md">
										<Maximize2Icon class="size-3.5" />
										<span>Click to enlarge (1920×962)</span>
									</Badge>
								</div>
							</button>
						</div>

						<!-- Details Column (5 cols) -->
						<div class="lg:col-span-5 flex flex-col items-start text-left gap-4">
							<div class="flex flex-wrap items-center gap-2">
								<Badge variant="outline" class="font-mono text-[11px]">{activeScreen.path}</Badge>
								<Badge variant="secondary" class="text-[11px]">{activeScreen.badge}</Badge>
							</div>

							<h3 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground">{activeScreen.title}</h3>

							<p class="text-sm text-muted-foreground leading-relaxed">
								{activeScreen.description}
							</p>

							<div class="space-y-2 w-full pt-2">
								{#each activeScreen.highlights as hl}
									<div class="flex items-start gap-2 text-xs text-foreground">
										<CheckIcon class="size-4 text-emerald-600 dark:text-emerald-400 shrink-0 mt-0.5" />
										<span>{hl}</span>
									</div>
								{/each}
							</div>

							<div class="flex flex-wrap gap-1.5 pt-2">
								{#each activeScreen.tags as tag}
									<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-muted text-muted-foreground border border-border/60">
										{tag}
									</span>
								{/each}
							</div>

							<div class="pt-2">
								<Button href={activeScreen.path} size="sm" class="gap-1.5 shadow-xs">
									<span>Open {activeScreen.title.split('&')[0].trim()}</span>
									<ArrowRightIcon class="size-3.5" />
								</Button>
							</div>
						</div>
					</div>
				</Card.Root>

				<!-- All 9 Screenshots Quick-Switch Grid -->
				<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-3 gap-4">
					{#each appScreens as s}
						<button
							type="button"
							class="group flex flex-col gap-2 p-2.5 rounded-lg border text-left transition-all cursor-pointer bg-card hover:shadow-sm {activeScreenId === s.id ? 'border-primary ring-1 ring-primary' : 'border-border'}"
							onclick={() => (activeScreenId = s.id)}
						>
							<div class="relative aspect-16/9 w-full rounded-md overflow-hidden bg-muted border border-border/80">
								<img src={s.image} alt={s.title} loading="lazy" class="size-full object-cover group-hover:scale-105 transition-transform duration-300" />
								<span class="absolute bottom-1.5 left-1.5 font-mono text-[9px] bg-background/90 text-foreground px-1.5 py-0.5 rounded border border-border/40 backdrop-blur-xs">
									{s.path}
								</span>
							</div>
							<div class="flex flex-col px-0.5">
								<span class="text-xs font-semibold truncate text-foreground">{s.title.split('&')[0].trim()}</span>
								<span class="text-[10px] text-muted-foreground truncate">{s.badge}</span>
							</div>
						</button>
					{/each}
				</div>
			</div>
		</section>

		<!-- ======================================================================
		     6. VISUAL GALLERY SHOWCASE (#gallery)
		     ====================================================================== -->
		<section id="gallery" class="py-16 sm:py-20 border-b border-border">
			<div class="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
				<div class="max-w-3xl mb-10 text-left">
					<Badge variant="outline" class="mb-3 font-mono text-[11px] uppercase tracking-wider">
						GHIM-10K Visual Archive
					</Badge>
					<h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight text-foreground mb-4">
						Explore indexed photography and pivot into similarity search.
					</h2>
					<p class="text-muted-foreground text-base sm:text-lg leading-relaxed">
						Filter by visual class or density, inspect dominant color signatures, and click <strong>Find Similar</strong> on any frame to load it directly into the Live Visual Query Workbench.
					</p>
				</div>

				<!-- Toolbar -->
				<div class="flex flex-wrap items-center justify-between gap-4 mb-8">
					<div class="flex flex-wrap items-center gap-1.5">
						<Button
							type="button"
							variant={activeCategory === 'all' ? 'default' : 'outline'}
							size="sm"
							class="text-xs h-7"
							onclick={() => (activeCategory = 'all')}
						>
							All
						</Button>
						<Button
							type="button"
							variant={activeCategory === 'Landscapes' ? 'default' : 'outline'}
							size="sm"
							class="text-xs h-7"
							onclick={() => (activeCategory = 'Landscapes')}
						>
							Landscapes
						</Button>
						<Button
							type="button"
							variant={activeCategory === 'Architecture' ? 'default' : 'outline'}
							size="sm"
							class="text-xs h-7"
							onclick={() => (activeCategory = 'Architecture')}
						>
							Architecture
						</Button>
						<Button
							type="button"
							variant={activeCategory === 'Autumn' ? 'default' : 'outline'}
							size="sm"
							class="text-xs h-7"
							onclick={() => (activeCategory = 'Autumn')}
						>
							Autumn
						</Button>
						<Button
							type="button"
							variant={activeCategory === 'Maritime' ? 'default' : 'outline'}
							size="sm"
							class="text-xs h-7"
							onclick={() => (activeCategory = 'Maritime')}
						>
							Maritime
						</Button>
					</div>

					<div class="flex items-center gap-1 p-0.5 rounded-lg bg-muted/60 border border-border">
						<Button
							type="button"
							variant={galleryDensity === 'comfortable' ? 'secondary' : 'ghost'}
							size="sm"
							class="h-6 text-xs px-2.5"
							onclick={() => (galleryDensity = 'comfortable')}
						>
							Comfortable
						</Button>
						<Button
							type="button"
							variant={galleryDensity === 'compact' ? 'secondary' : 'ghost'}
							size="sm"
							class="h-6 text-xs px-2.5"
							onclick={() => (galleryDensity = 'compact')}
						>
							Compact
						</Button>
					</div>
				</div>

				<!-- Photo Grid -->
				<div class="grid gap-4 {galleryDensity === 'compact' ? 'grid-cols-2 sm:grid-cols-4 lg:grid-cols-6' : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'}">
					{#each filteredGallery as item}
						<div class="group relative aspect-4/3 rounded-lg overflow-hidden border border-border bg-muted">
							<img src={item.url} alt={item.title} loading="lazy" class="size-full object-cover group-hover:scale-105 transition-transform duration-300" />
							<!-- Scrim Overlay -->
							<div class="absolute inset-0 bg-gradient-to-t from-black/85 via-black/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity p-3 flex flex-col justify-end gap-2 text-white text-left">
								<div class="flex items-center justify-between text-xs font-mono">
									<span class="truncate">{item.filename}</span>
									<span class="size-3 rounded-full border border-white/50 shrink-0" style="background-color:{item.dominantHex};"></span>
								</div>
								<div class="text-[10px] font-mono text-white/70">{item.resolution} · {item.category}</div>
								<Button
									type="button"
									size="sm"
									class="h-7 text-xs w-full mt-1 gap-1"
									onclick={() => loadPhotoIntoWorkbench(item)}
								>
									<span>Find Similar</span>
									<ArrowRightIcon class="size-3" />
								</Button>
							</div>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- ======================================================================
		     7. CLOSING BAND
		     ====================================================================== -->
		<section class="py-16 sm:py-20 border-b border-border">
			<div class="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
				<Card.Root class="shadow-md border-border bg-card p-6 sm:p-10">
					<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
						<div class="lg:col-span-7 flex flex-col items-start text-left">
							<Badge variant="outline" class="mb-3 font-mono text-[11px] uppercase tracking-wider">
								Batch Ingestion · Auto-On Extraction
							</Badge>
							<h2 class="text-2xl sm:text-3xl font-bold tracking-tight text-foreground mb-3">
								Index your visual archive.
							</h2>
							<p class="text-muted-foreground text-sm sm:text-base leading-relaxed max-w-xl mb-6">
								Upload JPG, PNG, or WEBP collections to compute HSV, Color Moments, MiniBatchKMeans, GLCM, and LBP vectors automatically on ingest.
							</p>
							<div class="flex flex-wrap items-center gap-3">
								<Button onclick={() => fileInputEl?.click()} class="gap-2 shadow-xs">
									<UploadCloudIcon class="size-4" />
									<span>Upload Images</span>
								</Button>
								<Button href="#workbench" variant="outline" class="shadow-2xs">
									Open Query Studio
								</Button>
							</div>
						</div>

						<!-- Drag & Drop Drop-Zone -->
						<div class="lg:col-span-5">
							<div
								role="button"
								tabindex="0"
								class="flex flex-col items-center justify-center p-8 rounded-xl border-2 border-dashed transition-all cursor-pointer text-center gap-2.5 {isDragOver ? 'border-primary bg-primary/5' : 'border-border/80 bg-muted/30 hover:border-primary/50'}"
								onclick={() => fileInputEl?.click()}
								onkeydown={(e) => e.key === 'Enter' && fileInputEl?.click()}
								ondragover={(e) => {
									e.preventDefault();
									isDragOver = true;
								}}
								ondragleave={() => (isDragOver = false)}
								ondrop={onDrop}
							>
								<input
									bind:this={fileInputEl}
									type="file"
									accept="image/*"
									class="hidden"
									onchange={onFileInputChange}
								/>
								<div class="size-11 rounded-full bg-primary/10 text-primary flex items-center justify-center mb-1">
									<UploadCloudIcon class="size-5" />
								</div>
								<span class="text-sm font-semibold text-foreground">Drop a reference image here</span>
								<span class="text-xs font-mono text-muted-foreground max-w-xs">
									Instant local preview in Query Workbench · JPG, PNG, WEBP
								</span>
							</div>
						</div>
					</div>
				</Card.Root>
			</div>
		</section>
	</main>

	<!-- ========================================================================
	     8. MINIMAL SINGLE-ROW FOOTER
	     ======================================================================== -->
	<footer class="border-t border-border bg-background py-6 text-xs text-muted-foreground">
		<div class="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4">
			<div class="flex items-center gap-3">
				<a href="#workbench" class="flex items-center gap-2 text-foreground font-semibold">
					<svg class="size-4 shrink-0 text-primary" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
						<rect x="33" y="13" width="13.5" height="13.5" rx="3.2" fill="currentColor" />
						<rect x="44" y="30" width="14.5" height="14.5" rx="3.4" fill="currentColor" />
						<rect x="28" y="44" width="13.5" height="13.5" rx="3.2" fill="currentColor" />
						<rect x="13" y="57" width="13.5" height="13.5" rx="3.2" fill="currentColor" />
						<path
							d="M60.5 13H74.5C87.8 13 96 22.8 96 36.5C96 50.2 87.2 60.5 73.5 60.5H59.5C56.5 60.5 54.5 62.5 54.5 65.5V72.5C54.5 81.2 47.2 88.5 38.5 88.5H37.8C36.2 88.5 35 87.3 35 85.7V75.5H29.8C27.8 75.5 26.5 74.2 26.5 72.2V70.3C26.5 68.3 27.8 67 29.8 67H35V60.2C35 56.8 37.5 54.5 41 54.5H48.5C50.4 54.5 51.8 53.1 51.8 51.2V49.2C51.8 46.8 53.7 45 56.2 45H70.8C76.2 45 79.8 41.4 79.8 36.5C79.8 31.6 76.2 28 70.8 28H60.5C57.5 28 55.5 26 55.5 23V18C55.5 15 57.5 13 60.5 13Z"
							fill="currentColor"
						/>
					</svg>
					<span>Perceptra</span>
				</a>
				<Badge variant="outline" class="font-mono text-[10px] py-0 px-2">v2.4</Badge>
			</div>

			<div class="flex flex-wrap items-center gap-6">
				<a href="#descriptors" class="hover:text-foreground transition-colors">Descriptors</a>
				<a href="#studio" class="hover:text-foreground transition-colors">FRE Studio</a>
				<a href="#transform" class="hover:text-foreground transition-colors">Transform</a>
				<a href="#screens" class="hover:text-foreground transition-colors">Screens</a>
				<a href="#gallery" class="hover:text-foreground transition-colors">Gallery</a>
				<span class="font-mono text-[11px] text-muted-foreground/80">GHIM-10K · 768-D HSV</span>
			</div>
		</div>
	</footer>

	<!-- Floating Feedback Toast -->
	{#if isToastVisible}
		<div class="fixed bottom-5 right-5 z-50 px-4 py-2.5 rounded-lg bg-card text-card-foreground border border-border shadow-lg text-xs font-medium font-mono animate-in fade-in slide-in-from-bottom-2 duration-200">
			{toastMessage}
		</div>
	{/if}

	<!-- Fullscreen Screenshot Lightbox Modal using shadcn Dialog -->
	<Dialog.Root bind:open={isLightboxOpen}>
		<Dialog.Content class="max-w-6xl p-2 bg-card border-border shadow-2xl">
			<Dialog.Header class="p-3 pb-1 flex flex-row items-center justify-between">
				<Dialog.Title class="text-xs font-mono text-muted-foreground truncate">{zoomedImage}</Dialog.Title>
			</Dialog.Header>
			<div class="relative w-full rounded-md overflow-hidden bg-muted flex items-center justify-center p-1">
				{#if zoomedImage}
					<img src={zoomedImage} alt="Enlarged screenshot" class="max-w-full max-h-[82vh] object-contain rounded" />
				{/if}
			</div>
		</Dialog.Content>
	</Dialog.Root>
</div>
