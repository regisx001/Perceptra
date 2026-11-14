<script lang="ts">
	import PhotoIcon from "@tabler/icons-svelte/icons/photo";
	import LayoutDashboardIcon from "@tabler/icons-svelte/icons/layout-dashboard";
	import UploadIcon from "@tabler/icons-svelte/icons/upload";
	import FolderTreeIcon from "@tabler/icons-svelte/icons/folder";
	import HelpIcon from "@tabler/icons-svelte/icons/help";
	import SettingsIcon from "@tabler/icons-svelte/icons/settings";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import NavMain from "./nav-main.svelte";
	import NavSecondary from "./nav-secondary.svelte";
	import NavUser from "./nav-user.svelte";
	import { auth } from "#lib/auth.js";
	import * as m from "#lib/paraglide/messages.js";
	import type { ComponentProps } from "svelte";

	const currentUser = auth.getUser();

	let navMain = $derived([
		{
			title: m.nav_overview(),
			url: "/dashboard",
			icon: LayoutDashboardIcon,
		},
		{
			title: m.nav_images(),
			url: "/dashboard/images",
			icon: PhotoIcon,
		},
		{
			title: m.nav_upload_images(),
			url: "/dashboard/upload",
			icon: UploadIcon,
		},
		{
			title: m.nav_categories(),
			url: "/dashboard/categories",
			icon: FolderTreeIcon,
		},
	]);

	let navSecondary = $derived([
		{
			title: m.nav_settings(),
			url: "/settings",
			icon: SettingsIcon,
		},
		{
			title: m.nav_docs(),
			url: "/docs",
			icon: HelpIcon,
		},
	]);

	const sidebarData = {
		user: {
			name: currentUser?.email ? currentUser.email.split("@")[0] : "Researcher",
			email: currentUser?.email || "researcher@perceptra.local",
			avatar: "/favicon-light-32x32.png",
		},
	};

	let { ...restProps }: ComponentProps<typeof Sidebar.Root> = $props();
</script>

<Sidebar.Root collapsible="offcanvas" {...restProps}>
	<Sidebar.Header class="border-b border-sidebar-border px-3 py-3">
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton size="lg" class="h-11 rounded-lg data-[slot=sidebar-menu-button]:!p-2 hover:bg-sidebar-accent">
					{#snippet child({ props })}
						<a href="/" {...props} class="flex items-center gap-3">
							<!-- Brand Logo Image matching the Auth & Landing pages -->
							<img
								src="/logo-black.png"
								alt="Perceptra Logo"
								class="h-8 w-auto object-contain dark:hidden"
							/>
							<img
								src="/logo-beige.png"
								alt="Perceptra Logo"
								class="hidden h-8 w-auto object-contain dark:block"
							/>
							<div class="flex flex-col gap-0.5 leading-none">
								<span class="font-bold tracking-tight text-sm text-foreground">Perceptra</span>
								<span class="text-[11px] text-muted-foreground font-medium">Group 13 &bull; GHIM-10K</span>
							</div>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Header>

	<Sidebar.Content>
		<NavMain items={navMain} />
		<NavSecondary items={navSecondary} class="mt-auto" />
	</Sidebar.Content>

	<Sidebar.Footer class="border-t border-sidebar-border p-2">
		<NavUser user={sidebarData.user} />
	</Sidebar.Footer>
</Sidebar.Root>
