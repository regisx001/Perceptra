<script lang="ts">
	import ChartBarIcon from "@tabler/icons-svelte/icons/chart-bar";
	import DatabaseIcon from "@tabler/icons-svelte/icons/database";
	import AdjustmentsHorizontalIcon from "@tabler/icons-svelte/icons/adjustments-horizontal";
	import ColorSwatchIcon from "@tabler/icons-svelte/icons/color-swatch";
	import HelpIcon from "@tabler/icons-svelte/icons/help";
	import SettingsIcon from "@tabler/icons-svelte/icons/settings";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import NavDocuments from "./nav-documents.svelte";
	import NavMain from "./nav-main.svelte";
	import NavSecondary from "./nav-secondary.svelte";
	import NavUser from "./nav-user.svelte";
	import { auth } from "#lib/auth.js";
	import type { ComponentProps } from "svelte";

	const currentUser = auth.getUser();

	const sidebarData = {
		user: {
			name: currentUser?.email ? currentUser.email.split("@")[0] : "Researcher",
			email: currentUser?.email || "researcher@perceptra.local",
			avatar: "/favicon-light-32x32.png",
		},
		descriptors: [
			{
				name: "Color Descriptors",
				url: "/descriptors/color",
				icon: ColorSwatchIcon,
			},
			{
				name: "Texture (GLCM & LBP)",
				url: "/descriptors/texture",
				icon: AdjustmentsHorizontalIcon,
			},
			{
				name: "GHIM-10K Index Shards",
				url: "/descriptors/indexes",
				icon: DatabaseIcon,
			},
			{
				name: "Retrieval Benchmarks",
				url: "/descriptors/benchmarks",
				icon: ChartBarIcon,
			},
		],
		navSecondary: [
			{
				title: "System Settings",
				url: "/settings",
				icon: SettingsIcon,
			},
			{
				title: "Evaluation Documentation",
				url: "/docs",
				icon: HelpIcon,
			},
		],
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
		<NavMain />
		<NavDocuments items={sidebarData.descriptors} />
		<NavSecondary items={sidebarData.navSecondary} class="mt-auto" />
	</Sidebar.Content>

	<Sidebar.Footer class="border-t border-sidebar-border p-2">
		<NavUser user={sidebarData.user} />
	</Sidebar.Footer>
</Sidebar.Root>
