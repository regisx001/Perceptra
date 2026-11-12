<script lang="ts">
	import * as m from "#lib/paraglide/messages.js";
	import { useLocale } from "#lib/i18n.svelte.js";
	import ArrowLeftIcon from "@lucide/svelte/icons/arrow-left";
	import GlobeIcon from "@lucide/svelte/icons/globe";
	import FileTextIcon from "@lucide/svelte/icons/file-text";
	import ShieldCheckIcon from "@lucide/svelte/icons/shield-check";
	import CpuIcon from "@lucide/svelte/icons/cpu";
	import KeyRoundIcon from "@lucide/svelte/icons/key-round";
	import AlertCircleIcon from "@lucide/svelte/icons/alert-circle";

	const locale = useLocale();

	const sections = [
		{
			title: m.terms_s1_title,
			body: m.terms_s1_body,
			icon: ShieldCheckIcon,
		},
		{
			title: m.terms_s2_title,
			body: m.terms_s2_body,
			icon: CpuIcon,
		},
		{
			title: m.terms_s3_title,
			body: m.terms_s3_body,
			icon: FileTextIcon,
		},
		{
			title: m.terms_s4_title,
			body: m.terms_s4_body,
			icon: KeyRoundIcon,
		},
		{
			title: m.terms_s5_title,
			body: m.terms_s5_body,
			icon: AlertCircleIcon,
		},
	];
</script>

<svelte:head>
	<title>{m.terms_title()} | Perceptra</title>
</svelte:head>

<div class="min-h-svh bg-background text-foreground antialiased">
	<!-- Top Navigation Bar -->
	<header class="sticky top-0 z-20 border-b border-border/70 bg-background/80 backdrop-blur-md">
		<div class="mx-auto flex h-14 max-w-3xl items-center justify-between px-4 sm:px-6" style="max-width: 48rem;">
			<div class="flex items-center gap-3">
				<a
					href="/"
					class="inline-flex h-8 items-center gap-1.5 rounded-md border border-border/80 bg-background px-2.5 text-xs font-medium text-muted-foreground shadow-xs transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring active:scale-[0.97]"
					aria-label={m.auth_back_home()}
				>
					<ArrowLeftIcon class="size-3.5" />
					<span class="hidden sm:inline">{m.auth_back_home()}</span>
				</a>

				<a
					href="/"
					class="inline-flex items-center transition-opacity hover:opacity-85 focus-visible:outline-2 focus-visible:outline-ring"
					aria-label="Home"
				>
					<img
						src="/logo-black.png"
						alt="Logo"
						class="h-8 w-auto object-contain dark:hidden"
					/>
					<img
						src="/logo-beige.png"
						alt="Logo"
						class="hidden h-8 w-auto object-contain dark:block"
					/>
				</a>
			</div>

			<div class="flex items-center gap-2">
				<button
					type="button"
					onclick={() => locale.toggle()}
					class="inline-flex h-8 items-center gap-1.5 rounded-md border border-border/80 bg-background px-2.5 text-xs font-medium text-muted-foreground shadow-xs transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring active:scale-[0.97]"
					aria-label="Toggle language"
				>
					<GlobeIcon class="size-3.5" />
					<span>{locale.current.toUpperCase()}</span>
				</button>
				<a
					href="/privacy"
					class="inline-flex h-8 items-center rounded-md px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
				>
					{m.auth_privacy_policy()}
				</a>
			</div>
		</div>
	</header>

	<!-- Centered Clean Prose / Document Canvas (Option A) -->
	<main class="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:py-16" style="max-width: 48rem;">
		<!-- Article Title & Metadata -->
		<header class="mb-10 space-y-4 border-b border-border/70 pb-8">
			<div class="inline-flex items-center gap-2 rounded-full border border-border/80 bg-muted/50 px-3 py-1 text-xs font-medium text-muted-foreground">
				<FileTextIcon class="size-3.5 text-primary" />
				<span>{m.terms_last_updated()}</span>
			</div>
			<h1 class="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
				{m.terms_title()}
			</h1>
			<p class="text-base leading-relaxed text-muted-foreground sm:text-lg">
				{m.terms_intro()}
			</p>
		</header>

		<!-- Content Sections Stack -->
		<div class="space-y-6">
			{#each sections as sec}
				{@const IconComponent = sec.icon}
				<section class="rounded-xl border border-border/70 bg-card p-6 shadow-xs transition-colors sm:p-7">
					<div class="flex items-start gap-4">
						<div class="flex size-10 shrink-0 items-center justify-center rounded-lg border border-border/80 bg-muted/60 text-foreground">
							<IconComponent class="size-5" />
						</div>
						<div class="space-y-2">
							<h2 class="text-lg font-semibold tracking-tight text-foreground sm:text-xl">
								{sec.title()}
							</h2>
							<p class="text-sm leading-relaxed text-muted-foreground sm:text-base">
								{sec.body()}
							</p>
						</div>
					</div>
				</section>
			{/each}
		</div>

		<!-- Footer -->
		<footer class="mt-14 flex flex-col items-center justify-between gap-4 border-t border-border/70 pt-8 text-xs text-muted-foreground sm:flex-row">
			<p>Perceptra &bull; {m.app_title()}</p>
			<div class="flex items-center gap-4">
				<a href="/privacy" class="underline underline-offset-4 hover:text-foreground">
					{m.auth_privacy_policy()}
				</a>
				<a href="/login" class="underline underline-offset-4 hover:text-foreground">
					{m.auth_sign_in_link()}
				</a>
				<a href="/register" class="underline underline-offset-4 hover:text-foreground">
					{m.auth_sign_up_link()}
				</a>
			</div>
		</footer>
	</main>
</div>
