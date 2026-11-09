<script lang="ts">
	import type { LayoutProps } from "./$types";
	import * as m from "#lib/paraglide/messages.js";
	import { useLocale } from "#lib/i18n.svelte.js";
	import GalleryVerticalEndIcon from "@lucide/svelte/icons/gallery-vertical-end";
	import ArrowLeftIcon from "@lucide/svelte/icons/arrow-left";
	import GlobeIcon from "@lucide/svelte/icons/globe";

	let { children }: LayoutProps = $props();

	const locale = useLocale();
</script>

<div class="grid min-h-svh w-full lg:grid-cols-2">
	<!-- Left / Interactive Authentication Column -->
	<div class="flex flex-col justify-between p-6 sm:p-10 lg:p-12">
		<!-- Header: Brand mark, Back to Home & Language switcher -->
		<header class="flex items-center justify-between gap-4">
			<a
				href="/"
				class="group inline-flex items-center gap-2.5 font-medium tracking-tight text-foreground transition-opacity hover:opacity-85 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
			>
				<div
					class="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground shadow-xs transition-transform duration-150 ease-out group-hover:scale-[1.03] group-active:scale-[0.97]"
				>
					<GalleryVerticalEndIcon class="size-4.5" />
				</div>
				<span class="font-semibold text-sm sm:text-base"
					>CBIR Studio</span
				>
			</a>

			<div class="flex items-center gap-2">
				<button
					type="button"
					onclick={() => locale.toggle()}
					class="inline-flex h-8 items-center gap-1.5 rounded-md border border-border/80 bg-background/80 px-2.5 text-xs font-medium text-muted-foreground shadow-xs backdrop-blur-xs transition-[color,background-color] hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring active:scale-[0.97]"
					aria-label="Toggle language"
				>
					<GlobeIcon class="size-3.5" />
					<span>{locale.current.toUpperCase()}</span>
				</button>
				<a
					href="/"
					class="inline-flex h-8 items-center gap-1.5 rounded-md border border-transparent px-2.5 text-xs font-medium text-muted-foreground transition-[color,background-color] hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring active:scale-[0.97]"
				>
					<ArrowLeftIcon class="size-3.5" />
					<span class="hidden sm:inline">{m.auth_back_home()}</span>
				</a>
			</div>
		</header>

		<!-- Main Form Slot: Optically Centered with Max Width constraint -->
		<main
			class="my-auto flex w-full flex-col items-center justify-center py-8"
		>
			<div class="w-full max-w-[380px]">
				{@render children()}
			</div>
		</main>

		<!-- Footer Legal Disclaimer -->
		<footer class="pt-6 text-center text-xs text-muted-foreground">
			<p class="text-balance leading-relaxed">
				{m.auth_terms_prefix()}
				<a
					href="/terms"
					class="font-medium text-foreground underline underline-offset-4 transition-colors hover:text-primary"
				>
					{m.auth_terms_of_service()}
				</a>
				{" "}{m.auth_and()}{" "}
				<a
					href="/privacy"
					class="font-medium text-foreground underline underline-offset-4 transition-colors hover:text-primary"
				>
					{m.auth_privacy_policy()}
				</a>.
			</p>
		</footer>
	</div>

	<!-- Right / Visual Showcase Column with Hero Image Background -->
	<aside
		class="relative hidden flex-col justify-between overflow-hidden border-s border-border/60 p-10 lg:flex xl:p-14"
		aria-label="Product Showcase"
	>
		<!-- Background Image Layer -->
		<img
			src="/images/auth-hero.jpg"
			alt=""
			aria-hidden="true"
			class="pointer-events-none absolute inset-0 h-full w-full object-cover dark:brightness-[0.7] dark:contrast-[1.1]"
			loading="lazy"
		/>

		<!-- Gradient / Tint Overlays for Readability & Depth -->
		<div
			class="pointer-events-none absolute inset-0 bg-linear-to-t from-black/85 via-black/40 to-black/30 dark:from-black/90 dark:via-black/55 dark:to-black/40"
		></div>
		<div
			class="pointer-events-none absolute inset-0 bg-radial-[at_top_right] from-primary/20 via-transparent to-transparent"
		></div>

		<!-- Top Tagline Badge -->
		<div class="relative z-10 flex items-center gap-2">
			<!-- <span
				class="inline-flex items-center gap-2 rounded-full border border-white/20 bg-black/40 px-3.5 py-1.5 text-xs font-medium text-white shadow-lg backdrop-blur-md"
			>
				<span class="size-2 rounded-full bg-emerald-400 animate-pulse"
				></span>
				{m.auth_badge()}
			</span> -->
		</div>

		<!-- Bottom Quote / Credibility Statement -->
		<div class="relative z-10 max-w-lg space-y-2.5">
			<p
				class="text-base font-medium leading-relaxed text-white/95 drop-shadow-sm"
			>
				"{m.auth_quote()}"
			</p>
			<p class="text-xs text-white/70">
				High-dimensional indexing & deep feature cosine similarity
				clustering
			</p>
		</div>
	</aside>
</div>
