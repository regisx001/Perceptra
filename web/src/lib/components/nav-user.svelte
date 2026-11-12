<script lang="ts">
	import UserCircleIcon from "@tabler/icons-svelte/icons/user-circle";
	import DotsVerticalIcon from "@tabler/icons-svelte/icons/dots-vertical";
	import LogoutIcon from "@tabler/icons-svelte/icons/logout";
	import DatabaseIcon from "@tabler/icons-svelte/icons/database";
	import SettingsIcon from "@tabler/icons-svelte/icons/settings";
	import * as Avatar from "#lib/components/ui/avatar/index.js";
	import * as DropdownMenu from "#lib/components/ui/dropdown-menu/index.js";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import { auth } from "#lib/auth.js";
	import { goto } from "$app/navigation";

	let { user }: { user: { name: string; email: string; avatar: string } } = $props();

	const sidebar = Sidebar.useSidebar();

	async function handleLogout() {
		auth.clearSession();
		await goto("/login");
	}
</script>

<Sidebar.Menu>
	<Sidebar.MenuItem>
		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				{#snippet child({ props })}
					<Sidebar.MenuButton
						{...props}
						size="lg"
						class="rounded-lg data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
					>
						<Avatar.Root class="size-8 rounded-full border">
							<Avatar.Image src={user.avatar} alt={user.name} />
							<Avatar.Fallback class="rounded-full font-semibold text-xs bg-muted">
								{user.name.substring(0, 2).toUpperCase()}
							</Avatar.Fallback>
						</Avatar.Root>
						<div class="grid flex-1 text-start text-xs leading-tight">
							<span class="truncate font-semibold text-foreground text-sm">{user.name}</span>
							<span class="truncate text-muted-foreground text-[11px]">
								{user.email}
							</span>
						</div>
						<DotsVerticalIcon class="ms-auto size-4 text-muted-foreground" />
					</Sidebar.MenuButton>
				{/snippet}
			</DropdownMenu.Trigger>
			<DropdownMenu.Content
				class="w-(--bits-dropdown-menu-anchor-width) min-w-56 rounded-lg"
				side={sidebar.isMobile ? "bottom" : "right"}
				align="end"
				sideOffset={4}
			>
				<DropdownMenu.Label class="p-0 font-normal">
					<div class="flex items-center gap-2 px-2 py-2 text-start text-sm">
						<Avatar.Root class="size-8 rounded-full border">
							<Avatar.Image src={user.avatar} alt={user.name} />
							<Avatar.Fallback class="rounded-full font-semibold text-xs">
								{user.name.substring(0, 2).toUpperCase()}
							</Avatar.Fallback>
						</Avatar.Root>
						<div class="grid flex-1 text-start text-xs leading-tight">
							<span class="truncate font-medium">{user.name}</span>
							<span class="truncate text-muted-foreground text-[11px]">
								{user.email}
							</span>
						</div>
					</div>
				</DropdownMenu.Label>
				<DropdownMenu.Separator />
				<DropdownMenu.Group>
					<DropdownMenu.Item class="rounded-md">
						<UserCircleIcon class="size-4" />
						Profile & API Keys
					</DropdownMenu.Item>
					<DropdownMenu.Item class="rounded-md">
						<DatabaseIcon class="size-4" />
						Dataset Storage
					</DropdownMenu.Item>
					<DropdownMenu.Item class="rounded-md">
						<SettingsIcon class="size-4" />
						Preferences
					</DropdownMenu.Item>
				</DropdownMenu.Group>
				<DropdownMenu.Separator />
				<DropdownMenu.Item onclick={handleLogout} class="rounded-md text-destructive focus:text-destructive">
					<LogoutIcon class="size-4" />
					Log out
				</DropdownMenu.Item>
			</DropdownMenu.Content>
		</DropdownMenu.Root>
	</Sidebar.MenuItem>
</Sidebar.Menu>
