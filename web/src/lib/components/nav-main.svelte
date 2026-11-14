<script lang="ts">
	import PhotoPlusIcon from "@tabler/icons-svelte/icons/photo-plus";
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { page } from "$app/state";
	import type { Icon } from "@tabler/icons-svelte";
	import * as m from "#lib/paraglide/messages.js";

	let { items = [] }: { items?: { title: string; url: string; icon?: Icon }[] } = $props();

	function isCurrent(url: string) {
		return page.url.pathname === url;
	}
</script>

<Sidebar.Group class="py-2">
	<Sidebar.GroupContent class="flex flex-col gap-2">
		<!-- Primary Call to Action Button in Sidebar -->
		<div class="px-2 pb-1">
			<Button
				href="/search"
				class="w-full justify-start gap-2 rounded-lg font-semibold shadow-xs"
				size="sm"
			>
				<PhotoPlusIcon class="size-4 shrink-0" />
				<span class="truncate">{m.nav_new_visual_query()}</span>
			</Button>
		</div>

		{#if items.length > 0}
			<!-- Navigation list -->
			<Sidebar.Menu>
				{#each items as item (item.title)}
					<Sidebar.MenuItem>
						<Sidebar.MenuButton
							isActive={isCurrent(item.url)}
							tooltipContent={item.title}
						>
							{#snippet child({ props })}
								<a href={item.url} {...props}>
									{#if item.icon}
										<item.icon />
									{/if}
									<span>{item.title}</span>
								</a>
							{/snippet}
						</Sidebar.MenuButton>
					</Sidebar.MenuItem>
				{/each}
			</Sidebar.Menu>
		{/if}
	</Sidebar.GroupContent>
</Sidebar.Group>
