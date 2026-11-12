<script lang="ts">
	import type { LayoutProps } from "./$types";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import AppSidebar from "#lib/components/app-sidebar.svelte";
	import SiteHeader from "#lib/components/site-header.svelte";
	import { auth } from "#lib/auth.js";
	import { goto } from "$app/navigation";
	import { onMount } from "svelte";

	let { children }: LayoutProps = $props();
	let isChecking = $state(true);

	onMount(async () => {
		// Mock/Session auth validation: in dev mock mode we can either let user through or redirect if strict
		// If user is not authenticated, redirect to /login
		if (!auth.isAuthenticated()) {
			await goto("/login", { replaceState: true });
		} else {
			isChecking = false;
		}
	});
</script>

{#if !isChecking}
	<Sidebar.Provider
		style="--sidebar-width: calc(var(--spacing) * 72); --header-height: calc(var(--spacing) * 14);"
		class="h-svh overflow-hidden"
	>
		<AppSidebar variant="inset" />
		<Sidebar.Inset class="h-full max-h-svh flex flex-col overflow-hidden">
			<SiteHeader />
			<div class="flex-1 min-h-0 overflow-y-auto">
				{@render children()}
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
