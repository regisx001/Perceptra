<script lang="ts">
	import type { LayoutProps } from "./$types";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import AppSidebar from "#lib/components/app-sidebar.svelte";
	import SiteHeader from "#lib/components/site-header.svelte";
	import { auth } from "#lib/auth.js";
	import { goto } from "$app/navigation";
	import { page } from "$app/state";
	import { onMount } from "svelte";
	import { createHeaderPortal } from "#lib/header-portal.svelte.js";

	let { children }: LayoutProps = $props();
	let isChecking = $state(true);
	let isSidebarOpen = $state(true);

	const isTransformPage = $derived(page.url.pathname.startsWith("/dashboard/transform"));

	createHeaderPortal();

	onMount(async () => {
		if (!auth.isAuthenticated()) {
			await goto("/login", { replaceState: true });
			return;
		}

		// Validate current session & auto-refresh token if expired
		const user = await auth.fetchCurrentUser();
		if (!user) {
			await goto("/login", { replaceState: true });
			return;
		}

		isChecking = false;
	});
</script>

{#if !isChecking}
	<Sidebar.Provider
		bind:open={isSidebarOpen}
		style="--sidebar-width: calc(var(--spacing) * 72); --header-height: calc(var(--spacing) * 14);"
		class="h-svh overflow-hidden"
	>
		<AppSidebar variant="inset" />
		<Sidebar.Inset class="h-full max-h-svh flex flex-col overflow-hidden">
			<SiteHeader />
			<div class="flex-1 min-h-0 flex flex-col overflow-x-hidden {isTransformPage ? 'h-full overflow-y-auto lg:overflow-hidden' : 'overflow-y-auto'}">
				<div
					class="w-full h-full flex-1 min-h-0 flex flex-col mx-auto transition-[max-width] duration-300 ease-in-out {isTransformPage
						? 'max-w-full'
						: !isSidebarOpen
							? 'max-w-[90%]'
							: 'max-w-full'}"
				>
					{@render children()}
				</div>
			</div>
		</Sidebar.Inset>
	</Sidebar.Provider>
{:else}
	<div class="flex min-h-screen items-center justify-center">
		<div class="flex items-center gap-3 text-muted-foreground text-sm">
			<div class="size-4 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
			<span>Loading Perceptra...</span>
		</div>
	</div>
{/if}
