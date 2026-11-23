<script lang="ts">
	import DotsIcon from "@tabler/icons-svelte/icons/dots";
	import FolderIcon from "@tabler/icons-svelte/icons/folder";
	import Share3Icon from "@tabler/icons-svelte/icons/share-3";
	import TrashIcon from "@tabler/icons-svelte/icons/trash";
	import * as DropdownMenu from "#lib/components/ui/dropdown-menu/index.js";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import * as m from "#lib/paraglide/messages.js";
	import type { Icon } from "@tabler/icons-svelte";

	let { items }: { items: { name: string; url: string; icon: Icon }[] } = $props();

	const sidebar = Sidebar.useSidebar();
</script>

<Sidebar.Group class="group-data-[collapsible=icon]:hidden">
	<Sidebar.GroupLabel class="text-xs font-medium text-muted-foreground">
		{m.nav_doc_shards()}
	</Sidebar.GroupLabel>
	<Sidebar.Menu>
		{#each items as item (item.name)}
			<Sidebar.MenuItem>
				<Sidebar.MenuButton>
					{#snippet child({ props })}
						<a {...props} href={item.url}>
							<item.icon />
							<span>{item.name}</span>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
				<DropdownMenu.Root>
					<DropdownMenu.Trigger>
						{#snippet child({ props })}
							<Sidebar.MenuAction
								{...props}
								showOnHover
								class="rounded-sm data-[state=open]:bg-accent"
							>
								<DotsIcon />
								<span class="sr-only">{m.nav_more()}</span>
							</Sidebar.MenuAction>
						{/snippet}
					</DropdownMenu.Trigger>
					<DropdownMenu.Content
						class="w-32 rounded-lg"
						side={sidebar.isMobile ? "bottom" : "right"}
						align={sidebar.isMobile ? "end" : "start"}
					>
						<DropdownMenu.Item>
							<FolderIcon />
							<span>{m.nav_inspect_vectors()}</span>
						</DropdownMenu.Item>
						<DropdownMenu.Item>
							<Share3Icon />
							<span>{m.nav_export_hdf5()}</span>
						</DropdownMenu.Item>
						<DropdownMenu.Separator />
						<DropdownMenu.Item variant="destructive">
							<TrashIcon />
							<span>{m.nav_rebuild_index()}</span>
						</DropdownMenu.Item>
					</DropdownMenu.Content>
				</DropdownMenu.Root>
			</Sidebar.MenuItem>
		{/each}
	</Sidebar.Menu>
</Sidebar.Group>
