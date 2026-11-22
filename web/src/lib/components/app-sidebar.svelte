<script lang="ts">
	import PhotoIcon from "@tabler/icons-svelte/icons/photo";
	import LayoutDashboardIcon from "@tabler/icons-svelte/icons/layout-dashboard";
	import UploadIcon from "@tabler/icons-svelte/icons/upload";
	import FolderTreeIcon from "@tabler/icons-svelte/icons/folder";
	import TransformIcon from "@tabler/icons-svelte/icons/transform";
	import HeartIcon from "@tabler/icons-svelte/icons/heart";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import NavMain from "./nav-main.svelte";
	import NavUser from "./nav-user.svelte";
	import { auth } from "#lib/auth.js";
	import * as m from "#lib/paraglide/messages.js";
	import type { ComponentProps } from "svelte";
	import { page } from "$app/state";

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
			title: m.nav_transform(),
			url: "/dashboard/transform",
			icon: TransformIcon,
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

	const sidebarData = {
		user: {
			name: currentUser?.email ? currentUser.email.split("@")[0] : "Researcher",
			email: currentUser?.email || "researcher@perceptra.local",
			avatarLight: "/favicon-light-32x32.png",
			avatarDark: "/favicon-dark-32x32.png",
		},
	};

	let { ...restProps }: ComponentProps<typeof Sidebar.Root> = $props();
</script>

<Sidebar.Root collapsible="icon" {...restProps}>
	<Sidebar.Header class="border-b border-sidebar-border px-3 py-2.5 group-data-[collapsible=icon]:p-1.5">
		<Sidebar.Menu>
			<Sidebar.MenuItem>
				<Sidebar.MenuButton
					size="lg"
					tooltipContent="Perceptra"
					class="h-11 rounded-lg data-[slot=sidebar-menu-button]:!p-2 hover:bg-sidebar-accent group-data-[collapsible=icon]:size-8! group-data-[collapsible=icon]:p-1!"
				>
					{#snippet child({ props })}
						<a href="/" {...props} class="flex items-center gap-3 group-data-[collapsible=icon]:justify-center">
							<!-- Brand Logo Image matching the Auth & Landing pages -->
							<img
								src="/logo-black.png"
								alt="Perceptra Logo"
								class="size-7 w-auto object-contain dark:hidden shrink-0 group-data-[collapsible=icon]:size-6"
							/>
							<img
								src="/logo-beige.png"
								alt="Perceptra Logo"
								class="hidden size-7 w-auto object-contain dark:block shrink-0 group-data-[collapsible=icon]:size-6"
							/>
							<div class="flex flex-col leading-none group-data-[collapsible=icon]:hidden">
								<span class="font-bold tracking-tight text-sm text-foreground">Perceptra</span>
							</div>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		</Sidebar.Menu>
	</Sidebar.Header>

	<Sidebar.Content>
		<NavMain items={navMain} />

		<!-- Collections / Favorites Section -->
		<div class="px-3 pt-3 pb-1 group-data-[collapsible=icon]:px-1.5 group-data-[collapsible=icon]:py-1.5">
			<div class="flex items-center gap-2">
				<span class="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/60 shrink-0 group-data-[collapsible=icon]:hidden">
					Collections
				</span>
				<div class="h-px w-full bg-sidebar-border/60"></div>
			</div>
		</div>

		<Sidebar.Group class="py-0">
			<Sidebar.GroupContent>
				<Sidebar.Menu>
					<Sidebar.MenuItem>
						<Sidebar.MenuButton
							isActive={page.url.pathname.startsWith("/dashboard/favorites")}
							tooltipContent="Favorites"
						>
							{#snippet child({ props })}
								<a href="/dashboard/favorites" {...props}>
									<HeartIcon />
									<span>Favorites</span>
								</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
				</Sidebar.Menu>
			</Sidebar.GroupContent>
		</Sidebar.Group>
	</Sidebar.Content>

	<Sidebar.Footer class="border-t border-sidebar-border p-2 group-data-[collapsible=icon]:p-1.5">
		<NavUser user={sidebarData.user} />
	</Sidebar.Footer>
	<Sidebar.Rail />
</Sidebar.Root>
