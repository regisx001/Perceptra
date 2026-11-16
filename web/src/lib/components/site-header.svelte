<script lang="ts">
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import { Separator } from "#lib/components/ui/separator/index.js";
	import { useHeaderPortal } from "#lib/header-portal.svelte.js";
	import ThemeToggle from "#lib/components/theme-toggle.svelte";
	import * as m from "#lib/paraglide/messages.js";
	import { page } from "$app/state";

	const portal = useHeaderPortal();

	interface BreadcrumbItem {
		label: string;
		href?: string;
		isCurrent?: boolean;
	}

	const defaultBreadcrumbs = $derived.by<BreadcrumbItem[]>(() => {
		const pathname = page.url.pathname;
		const items: BreadcrumbItem[] = [
			{ label: "Perceptra", href: "/dashboard" }
		];

		if (pathname === "/dashboard" || pathname === "/dashboard/") {
			items.push({ label: m.nav_overview(), isCurrent: true });
			return items;
		}

		if (pathname.startsWith("/dashboard/images")) {
			const isRoot = pathname === "/dashboard/images" || pathname === "/dashboard/images/";
			items.push({
				label: m.nav_images ? m.nav_images() : "Images",
				href: isRoot ? undefined : "/dashboard/images",
				isCurrent: isRoot
			});
			return items;
		}

		if (pathname.startsWith("/dashboard/transform")) {
			const isRoot = pathname === "/dashboard/transform" || pathname === "/dashboard/transform/";
			items.push({
				label: m.nav_transform ? m.nav_transform() : "Image Transform",
				href: isRoot ? undefined : "/dashboard/transform",
				isCurrent: isRoot
			});
			return items;
		}

		if (pathname.startsWith("/dashboard/upload")) {
			items.push({
				label: m.nav_upload_images ? m.nav_upload_images() : "Upload Images",
				isCurrent: true
			});
			return items;
		}

		if (pathname.startsWith("/dashboard/categories")) {
			items.push({
				label: m.nav_categories ? m.nav_categories() : "Categories",
				isCurrent: true
			});
			return items;
		}

		if (pathname.startsWith("/settings")) {
			items.push({
				label: m.nav_settings ? m.nav_settings() : "System Settings",
				isCurrent: true
			});
			return items;
		}

		if (pathname.startsWith("/docs")) {
			items.push({
				label: m.nav_docs ? m.nav_docs() : "Documentation",
				isCurrent: true
			});
			return items;
		}

		// Fallback for any other path segments
		const segments = pathname.split("/").filter(Boolean);
		for (let i = 0; i < segments.length; i++) {
			const seg = segments[i];
			if (seg === "dashboard" && i === 0) continue;
			const label = seg.charAt(0).toUpperCase() + seg.slice(1).replace(/[-_]/g, " ");
			const isLast = i === segments.length - 1;
			const href = "/" + segments.slice(0, i + 1).join("/");
			items.push({
				label,
				href: isLast ? undefined : href,
				isCurrent: isLast
			});
		}

		return items;
	});
</script>

<header
	class="sticky top-0 z-20 flex h-(--header-height) shrink-0 items-center justify-between gap-3 border-b bg-background/95 px-4 backdrop-blur-xs transition-[width,height] ease-linear lg:px-6"
>
	<div class="flex items-center gap-2 min-w-0">
		<Sidebar.Trigger class="-ms-1 shrink-0" />
		<Separator orientation="vertical" class="mx-1 h-4 shrink-0" />
		
		{#if portal?.breadcrumb}
			{@render portal.breadcrumb()}
		{:else}
			<nav class="flex items-center gap-2 text-xs text-muted-foreground min-w-0" aria-label="Breadcrumb">
				{#each defaultBreadcrumbs as item, i}
					{#if i > 0}
						<span class="text-xs text-muted-foreground/60 shrink-0">/</span>
					{/if}

					{#if item.isCurrent || !item.href}
						<span
							class="truncate max-w-[120px] sm:max-w-[180px] md:max-w-[220px] {i === 0 ? 'text-sm font-semibold tracking-tight text-foreground' : 'text-xs text-muted-foreground font-medium'}"
							title={item.label}
						>
							{item.label}
						</span>
					{:else}
						<a
							href={item.href}
							class="truncate max-w-[100px] sm:max-w-[140px] md:max-w-[180px] transition-colors hover:text-foreground {i === 0 ? 'text-sm font-semibold tracking-tight text-foreground' : 'text-xs text-muted-foreground'}"
							title={item.label}
						>
							{item.label}
						</a>
					{/if}
				{/each}
			</nav>
		{/if}
	</div>

	<!-- Injected Controls from Active Page (Search, Filters, Actions) + Global Theme Toggle -->
	<div class="flex items-center gap-2.5 ms-auto shrink-0">
		{#if portal?.content}
			{@render portal.content()}
		{/if}
		<ThemeToggle />
	</div>
</header>
