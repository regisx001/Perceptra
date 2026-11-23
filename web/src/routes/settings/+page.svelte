<script lang="ts">
	import UserIcon from "@tabler/icons-svelte/icons/user";
	import PaletteIcon from "@tabler/icons-svelte/icons/palette";
	import BellIcon from "@tabler/icons-svelte/icons/bell";
	import LockIcon from "@tabler/icons-svelte/icons/lock";
	import KeyIcon from "@tabler/icons-svelte/icons/key";
	import CloudIcon from "@tabler/icons-svelte/icons/cloud";
	import DeviceDesktopIcon from "@tabler/icons-svelte/icons/device-desktop";
	import SettingsIcon from "@tabler/icons-svelte/icons/settings";
	import CheckIcon from "@tabler/icons-svelte/icons/check";
	import ArrowLeftIcon from "@tabler/icons-svelte/icons/arrow-left";
	import SunIcon from "@tabler/icons-svelte/icons/sun";
	import MoonIcon from "@tabler/icons-svelte/icons/moon";
	import GlobeIcon from "@lucide/svelte/icons/globe";
	import ThemeToggle from "#lib/components/theme-toggle.svelte";
	import { setMode, resetMode, mode } from "mode-watcher";
	import { useLocale } from "#lib/i18n.svelte.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Input } from "#lib/components/ui/input/index.js";
	import { Separator } from "#lib/components/ui/separator/index.js";
	import { auth } from "#lib/auth.js";
	import * as m from "#lib/paraglide/messages.js";
	import { goto } from "$app/navigation";
	import { page } from "$app/state";

	const currentUser = auth.getUser();
	const locale = useLocale();

	const validTabs = [
		"profile",
		"appearance",
		"notifications",
		"security",
		"tokens",
		"limits",
		"descriptors",
		"maintenance",
	];

	let activeTab = $derived(
		validTabs.includes(page.url.searchParams.get("tab") || "")
			? (page.url.searchParams.get("tab") as string)
			: "profile"
	);

	function setTab(tabId: string) {
		goto(`?tab=${tabId}`, { reset: false });
	}

	// Form field states matching screenshot
	let displayName = $state("Ezzoubair ZARQI");
	let username = $state("regisx001");
	let email = $state(currentUser?.email || "zarqi.ezzoubair@gmail.com");
	let defaultCategory = $state("Uncategorized (Default)");

	let isSaving = $state(false);
	let isSaved = $state(false);

	function handleSave() {
		isSaving = true;
		setTimeout(() => {
			isSaving = false;
			isSaved = true;
			setTimeout(() => {
				isSaved = false;
			}, 2500);
		}, 400);
	}

	let navSections = $derived([
		{
			title: m.settings_section_account(),
			items: [
				{ id: "profile", title: m.settings_profile_title(), icon: UserIcon },
				{ id: "appearance", title: m.settings_appearance_title(), icon: PaletteIcon },
				{ id: "notifications", title: m.settings_notifications_title(), icon: BellIcon },
			],
		},
		{
			title: m.settings_section_access(),
			items: [
				{ id: "security", title: m.settings_security_title(), icon: LockIcon },
				{ id: "tokens", title: m.settings_tokens_title(), icon: KeyIcon },
				{ id: "limits", title: m.settings_limits_title(), icon: CloudIcon },
			],
		},
		{
			title: m.settings_section_engine(),
			items: [
				{ id: "descriptors", title: m.settings_descriptors_title(), icon: DeviceDesktopIcon },
				{ id: "maintenance", title: m.settings_maintenance_title(), icon: SettingsIcon },
			],
		},
	]);
</script>

<svelte:head>
	<title>Settings • Perceptra</title>
</svelte:head>

<div class="min-h-screen bg-background text-foreground antialiased selection:bg-primary/10 selection:text-primary">
	<!-- Top Navigation Header matching user mockup -->
	<header class="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-border bg-background px-6 lg:px-8">
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
			<div class="flex flex-col leading-tight">
				<span class="text-sm font-bold tracking-tight text-foreground sm:text-base">
					{displayName} ({username})
				</span>
				<span class="text-xs font-medium text-muted-foreground">
					Your personal account &bull; Group 13
				</span>
			</div>
		</div>

		<div class="flex items-center gap-2">
			<ThemeToggle />
			<Button
				variant="outline"
				size="sm"
				href="/dashboard"
				class="h-8 gap-1.5 px-3 text-xs font-semibold shadow-xs"
			>
				<ArrowLeftIcon class="size-3.5" />
				<span>{m.settings_back_to_dashboard()}</span>
			</Button>
		</div>
	</header>

	<!-- Main Settings Content Layout -->
	<div class="mx-auto flex w-full max-w-6xl flex-col md:flex-row min-h-[calc(100vh-4rem)]">
		<!-- Left Settings Sidebar Navigation -->
		<aside class="w-full shrink-0 border-b border-border p-4 md:w-64 md:border-b-0 md:border-r md:p-6 space-y-6">
			{#each navSections as section}
				<div class="space-y-1">
					<h3 class="px-2.5 pb-1 text-xs font-semibold text-muted-foreground">
						{section.title}
					</h3>
					<nav class="space-y-0.5">
						{#each section.items as item}
							<button
								type="button"
								onclick={() => setTab(item.id)}
								class="relative flex w-full items-center gap-2.5 rounded-md px-2.5 py-1.5 text-xs font-semibold transition-colors text-left cursor-pointer {activeTab === item.id ? 'bg-accent text-foreground' : 'text-muted-foreground hover:bg-accent/60 hover:text-foreground'}"
							>
								{#if activeTab === item.id}
									<span class="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-1 rounded-full bg-primary"></span>
								{/if}
								<item.icon class="size-4 shrink-0 {activeTab === item.id ? 'text-foreground' : 'text-muted-foreground'}" />
								<span class="truncate">{item.title}</span>
							</button>
						{/each}
					</nav>
				</div>
			{/each}
		</aside>

		<!-- Right Settings Panel Slot -->
		<main class="flex-1 p-6 md:p-8 max-w-2xl">
			{#if activeTab === "profile"}
				<div class="space-y-6">
					<div>
						<h1 class="text-2xl font-bold tracking-tight text-foreground">
							{m.settings_profile_title()}
						</h1>
						<Separator class="mt-4" />
					</div>

					<form onsubmit={(e) => { e.preventDefault(); handleSave(); }} class="space-y-5">
						<!-- Display Name -->
						<div class="space-y-1.5">
							<label for="display-name" class="text-xs font-semibold text-foreground">
								{m.settings_display_name()}
							</label>
							<Input
								id="display-name"
								bind:value={displayName}
								class="max-w-md h-9 text-xs"
							/>
							<p class="text-[11px] text-muted-foreground">
								{m.settings_display_name_desc()}
							</p>
						</div>

						<!-- Username -->
						<div class="space-y-1.5">
							<label for="username" class="text-xs font-semibold text-foreground">
								{m.settings_username()}
							</label>
							<Input
								id="username"
								bind:value={username}
								class="max-w-md h-9 text-xs"
							/>
							<p class="text-[11px] text-muted-foreground">
								{m.settings_username_desc()}
							</p>
						</div>

						<!-- Email Address -->
						<div class="space-y-1.5">
							<label for="email" class="text-xs font-semibold text-foreground">
								{m.settings_email()}
							</label>
							<Input
								id="email"
								type="email"
								bind:value={email}
								class="max-w-md h-9 text-xs"
							/>
							<p class="text-[11px] text-muted-foreground">
								{m.settings_email_desc()}
							</p>
						</div>

						<!-- Default Upload Category -->
						<div class="space-y-1.5">
							<label for="default-category" class="text-xs font-semibold text-foreground">
								{m.settings_default_category()}
							</label>
							<select
								id="default-category"
								bind:value={defaultCategory}
								class="flex h-9 w-full max-w-md rounded-md border border-input bg-background px-3 py-1.5 text-xs font-medium text-foreground shadow-xs transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
							>
								<option value="Uncategorized (Default)">Uncategorized (Default)</option>
								<option value="Airplanes">Airplanes</option>
								<option value="Architecture & Buildings">Architecture & Buildings</option>
								<option value="Automotive & Cars">Automotive & Cars</option>
								<option value="Nature & Landscapes">Nature & Landscapes</option>
								<option value="Animals & Wildlife">Animals & Wildlife</option>
							</select>
						</div>

						<!-- Storage Isolation Path -->
						<div class="space-y-1.5">
							<label for="storage-path" class="text-xs font-semibold text-foreground">
								{m.settings_storage_path()}
							</label>
							<div class="relative max-w-md">
								<Input
									id="storage-path"
									readonly
									value="users/zarqi_ezzoubair/ (Atomic UUID)"
									class="h-9 pr-9 text-xs bg-muted/50 cursor-not-allowed select-none text-muted-foreground font-mono"
								/>
								<LockIcon class="absolute right-2.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground pointer-events-none" />
							</div>
						</div>

						<!-- Actions -->
						<div class="flex items-center gap-3 pt-2">
							<Button
								type="submit"
								size="sm"
								class="h-8 px-4 text-xs font-semibold shadow-xs cursor-pointer"
								disabled={isSaving}
							>
								{#if isSaving}
									{m.settings_saving()}
								{:else if isSaved}
									<CheckIcon class="size-3.5 mr-1 text-emerald-300" />
									{m.settings_saved()}
								{:else}
									{m.settings_save_changes()}
								{/if}
							</Button>
							<Button
								type="button"
								variant="ghost"
								size="sm"
								onclick={() => {
									displayName = "Ezzoubair ZARQI";
									username = "regisx001";
									email = "zarqi.ezzoubair@gmail.com";
									defaultCategory = "Uncategorized (Default)";
								}}
								class="h-8 px-3 text-xs font-semibold text-muted-foreground hover:text-foreground cursor-pointer"
							>
								{m.settings_cancel()}
							</Button>
						</div>
					</form>
				</div>

			{:else if activeTab === "appearance"}
				<div class="space-y-8">
					<div>
						<h1 class="text-2xl font-bold tracking-tight text-foreground">
							{m.settings_appearance_title()}
						</h1>
						<Separator class="mt-4" />
					</div>

					<!-- Section 1: Interface Theme -->
					<div class="space-y-3">
						<h2 class="text-sm font-semibold text-foreground">{m.settings_theme_title()}</h2>
						<p class="text-xs text-muted-foreground">
							{m.settings_theme_desc()}
						</p>
						<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-xl pt-1">
							<!-- Light Mode Card -->
							<button
								type="button"
								onclick={() => setMode("light")}
								class="rounded-lg border-2 p-3.5 bg-card text-left transition-all cursor-pointer {mode.current === 'light' ? 'border-primary ring-2 ring-primary/20' : 'border-border hover:border-border/80'}"
							>
								<div class="flex items-center justify-between mb-2">
									<div class="flex items-center gap-1.5">
										<SunIcon class="size-4 text-foreground" />
										<span class="text-xs font-semibold">{m.settings_theme_light()}</span>
									</div>
									{#if mode.current === "light"}
										<CheckIcon class="size-3.5 text-primary" />
									{/if}
								</div>
								<div class="h-14 rounded-md bg-[#ffffff] border border-[#d1d9e0] p-2 flex flex-col justify-between">
									<div class="h-2 w-12 rounded bg-[#0969da]"></div>
									<div class="h-1.5 w-16 rounded bg-[#d1d9e0]"></div>
								</div>
							</button>

							<!-- Dark Mode Card -->
							<button
								type="button"
								onclick={() => setMode("dark")}
								class="rounded-lg border-2 p-3.5 bg-card text-left transition-all cursor-pointer {mode.current === 'dark' ? 'border-primary ring-2 ring-primary/20' : 'border-border hover:border-border/80'}"
							>
								<div class="flex items-center justify-between mb-2">
									<div class="flex items-center gap-1.5">
										<MoonIcon class="size-4 text-foreground" />
										<span class="text-xs font-semibold">{m.settings_theme_dark()}</span>
									</div>
									{#if mode.current === "dark"}
										<CheckIcon class="size-3.5 text-primary" />
									{/if}
								</div>
								<div class="h-14 rounded-md bg-[#0d1117] border border-[#30363d] p-2 flex flex-col justify-between">
									<div class="h-2 w-12 rounded bg-[#1f6feb]"></div>
									<div class="h-1.5 w-16 rounded bg-[#30363d]"></div>
								</div>
							</button>

							<!-- System Preference Card -->
							<button
								type="button"
								onclick={() => resetMode()}
								class="rounded-lg border-2 p-3.5 bg-card text-left transition-all cursor-pointer {mode.current === undefined ? 'border-primary ring-2 ring-primary/20' : 'border-border hover:border-border/80'}"
							>
								<div class="flex items-center justify-between mb-2">
									<div class="flex items-center gap-1.5">
										<DeviceDesktopIcon class="size-4 text-foreground" />
										<span class="text-xs font-semibold">{m.settings_theme_system()}</span>
									</div>
									{#if mode.current === undefined}
										<CheckIcon class="size-3.5 text-primary" />
									{/if}
								</div>
								<div class="h-14 rounded-md bg-gradient-to-r from-[#ffffff] to-[#0d1117] border border-border p-2 flex flex-col justify-between">
									<div class="h-2 w-12 rounded bg-primary"></div>
									<div class="h-1.5 w-16 rounded bg-muted-foreground/30"></div>
								</div>
							</button>
						</div>
					</div>

					<Separator />

					<!-- Section 2: Language & Region -->
					<div class="space-y-3">
						<h2 class="text-sm font-semibold text-foreground">{m.settings_language_title()}</h2>
						<p class="text-xs text-muted-foreground">
							{m.settings_language_desc()}
						</p>
						<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-md pt-1">
							<!-- English Option -->
							<button
								type="button"
								onclick={() => locale.set("en")}
								class="rounded-lg border-2 p-3.5 bg-card text-left transition-all cursor-pointer flex items-center justify-between {locale.current === 'en' ? 'border-primary ring-2 ring-primary/20' : 'border-border hover:border-border/80'}"
							>
								<div class="flex items-center gap-2.5">
									<GlobeIcon class="size-4 text-muted-foreground" />
									<div>
										<p class="text-xs font-semibold text-foreground">{m.settings_lang_en()}</p>
										<p class="text-[11px] text-muted-foreground">{m.settings_lang_en_desc()}</p>
									</div>
								</div>
								{#if locale.current === "en"}
									<CheckIcon class="size-4 text-primary shrink-0" />
								{/if}
							</button>

							<!-- French Option -->
							<button
								type="button"
								onclick={() => locale.set("fr")}
								class="rounded-lg border-2 p-3.5 bg-card text-left transition-all cursor-pointer flex items-center justify-between {locale.current === 'fr' ? 'border-primary ring-2 ring-primary/20' : 'border-border hover:border-border/80'}"
							>
								<div class="flex items-center gap-2.5">
									<GlobeIcon class="size-4 text-muted-foreground" />
									<div>
										<p class="text-xs font-semibold text-foreground">{m.settings_lang_fr()}</p>
										<p class="text-[11px] text-muted-foreground">{m.settings_lang_fr_desc()}</p>
									</div>
								</div>
								{#if locale.current === "fr"}
									<CheckIcon class="size-4 text-primary shrink-0" />
								{/if}
							</button>
						</div>
					</div>
				</div>

			{:else if activeTab === "notifications"}
				<div class="space-y-6">
					<div>
						<h1 class="text-2xl font-bold tracking-tight text-foreground">
							{m.settings_notif_title()}
						</h1>
						<Separator class="mt-4" />
					</div>
					<div class="space-y-3 max-w-md text-xs">
						<label class="flex items-center gap-2">
							<input type="checkbox" checked class="rounded border-border text-primary focus:ring-primary" />
							<span>{m.settings_notif_email_indexing()}</span>
						</label>
						<label class="flex items-center gap-2">
							<input type="checkbox" checked class="rounded border-border text-primary focus:ring-primary" />
							<span>{m.settings_notif_storage_quota()}</span>
						</label>
						<label class="flex items-center gap-2">
							<input type="checkbox" class="rounded border-border text-primary focus:ring-primary" />
							<span>{m.settings_notif_weekly_digest()}</span>
						</label>
					</div>
				</div>

			{:else if activeTab === "security"}
				<div class="space-y-6">
					<div>
						<h1 class="text-2xl font-bold tracking-tight text-foreground">
							{m.settings_sec_title()}
						</h1>
						<Separator class="mt-4" />
					</div>
					<div class="space-y-4 max-w-md">
						<div class="space-y-1.5">
							<label for="old-pass" class="text-xs font-semibold">{m.settings_sec_current_pass()}</label>
							<Input id="old-pass" type="password" class="h-9 text-xs" />
						</div>
						<div class="space-y-1.5">
							<label for="new-pass" class="text-xs font-semibold">{m.settings_sec_new_pass()}</label>
							<Input id="new-pass" type="password" class="h-9 text-xs" />
						</div>
						<Button size="sm" class="h-8 text-xs font-semibold cursor-pointer">{m.settings_sec_update_btn()}</Button>
					</div>
				</div>

			{:else if activeTab === "tokens"}
				<div class="space-y-6">
					<div>
						<h1 class="text-2xl font-bold tracking-tight text-foreground">
							{m.settings_tok_title()}
						</h1>
						<Separator class="mt-4" />
					</div>
					<div class="space-y-3 max-w-md">
						<p class="text-xs text-muted-foreground">
							{m.settings_tok_desc()}
						</p>
						<div class="rounded-lg border border-border p-3 bg-muted/30 font-mono text-xs truncate">
							eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.perceptra_token_mock
						</div>
						<Button variant="outline" size="sm" class="h-8 text-xs font-semibold cursor-pointer">{m.settings_tok_generate_btn()}</Button>
					</div>
				</div>

			{:else if activeTab === "limits"}
				<div class="space-y-6">
					<div>
						<h1 class="text-2xl font-bold tracking-tight text-foreground">
							{m.settings_lim_title()}
						</h1>
						<Separator class="mt-4" />
					</div>
					<div class="space-y-4 max-w-md text-xs">
						<div class="space-y-1">
							<div class="flex justify-between font-semibold">
								<span>{m.settings_lim_indexed()}</span>
								<span>10,000 / 50,000</span>
							</div>
							<div class="h-2 rounded-full bg-muted overflow-hidden">
								<div class="h-full bg-primary w-[20%]"></div>
							</div>
						</div>
						<div class="space-y-1">
							<div class="flex justify-between font-semibold">
								<span>{m.settings_lim_quota()}</span>
								<span>1.42 GB / 10.00 GB</span>
							</div>
							<div class="h-2 rounded-full bg-muted overflow-hidden">
								<div class="h-full bg-primary w-[14%]"></div>
							</div>
						</div>
					</div>
				</div>

			{:else if activeTab === "descriptors"}
				<div class="space-y-6">
					<div>
						<h1 class="text-2xl font-bold tracking-tight text-foreground">
							{m.settings_desc_engine_title()}
						</h1>
						<Separator class="mt-4" />
					</div>
					<div class="space-y-3 max-w-md text-xs">
						<div class="flex items-center justify-between p-3 rounded-lg border border-border bg-card">
							<div>
								<p class="font-semibold">{m.settings_desc_hsv_title()}</p>
								<p class="text-muted-foreground text-[11px]">{m.settings_desc_hsv_sub()}</p>
							</div>
							<span class="text-xs font-semibold text-emerald-600 dark:text-emerald-400">{m.settings_desc_active()}</span>
						</div>
						<div class="flex items-center justify-between p-3 rounded-lg border border-border bg-card">
							<div>
								<p class="font-semibold">{m.settings_desc_gabor_title()}</p>
								<p class="text-muted-foreground text-[11px]">{m.settings_desc_gabor_sub()}</p>
							</div>
							<span class="text-xs font-semibold text-emerald-600 dark:text-emerald-400">{m.settings_desc_active()}</span>
						</div>
					</div>
				</div>

			{:else if activeTab === "maintenance"}
				<div class="space-y-6">
					<div>
						<h1 class="text-2xl font-bold tracking-tight text-foreground">
							{m.settings_maint_title()}
						</h1>
						<Separator class="mt-4" />
					</div>
					<div class="space-y-3 max-w-md">
						<p class="text-xs text-muted-foreground">
							{m.settings_maint_desc()}
						</p>
						<div class="flex gap-2">
							<Button variant="outline" size="sm" class="h-8 text-xs font-semibold cursor-pointer">{m.settings_maint_reindex_btn()}</Button>
							<Button variant="destructive" size="sm" class="h-8 text-xs font-semibold cursor-pointer">{m.settings_maint_purge_btn()}</Button>
						</div>
					</div>
				</div>
			{/if}
		</main>
	</div>
</div>
