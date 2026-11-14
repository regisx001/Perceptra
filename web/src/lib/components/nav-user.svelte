<script lang="ts">
	import LogoutIcon from "@tabler/icons-svelte/icons/logout";
	import * as Avatar from "#lib/components/ui/avatar/index.js";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import { auth } from "#lib/auth.js";
	import { goto } from "$app/navigation";
	import * as m from "#lib/paraglide/messages.js";

	let { user }: { user: { name: string; email: string; avatar: string } } = $props();

	async function handleLogout() {
		auth.clearSession();
		await goto("/login");
	}
</script>

<Sidebar.Menu>
	<Sidebar.MenuItem>
		<div
			class="flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2 text-start transition-colors hover:bg-sidebar-accent/50"
		>
			<a
				href="/settings"
				class="flex flex-1 items-center gap-2.5 min-w-0 group"
				title={m.nav_settings()}
			>
				<Avatar.Root class="size-8 rounded-full border shrink-0">
					<Avatar.Image src={user.avatar} alt={user.name} />
					<Avatar.Fallback class="rounded-full font-semibold text-xs bg-muted">
						{user.name.substring(0, 2).toUpperCase()}
					</Avatar.Fallback>
				</Avatar.Root>
				<div class="grid flex-1 text-start text-xs leading-tight min-w-0">
					<span class="truncate font-semibold text-foreground text-sm group-hover:text-primary transition-colors">{user.name}</span>
					<span class="truncate text-muted-foreground text-[11px]" title={user.email}>
						{user.email}
					</span>
				</div>
			</a>
			<button
				type="button"
				onclick={handleLogout}
				title={m.auth_logout()}
				class="text-muted-foreground hover:text-destructive p-1.5 rounded-md hover:bg-destructive/10 transition-colors shrink-0 cursor-pointer"
				aria-label={m.auth_logout()}
			>
				<LogoutIcon class="size-4" />
			</button>
		</div>
	</Sidebar.MenuItem>
</Sidebar.Menu>
