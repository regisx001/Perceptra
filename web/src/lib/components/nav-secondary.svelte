<script lang="ts">
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import type { WithoutChildren } from "#lib/utils.js";
	import type { Icon } from "@tabler/icons-svelte";
	import type { ComponentProps } from "svelte";
	import { page } from "$app/state";

	let {
		items,
		...restProps
	}: { items: { title: string; url: string; icon: Icon }[] } & WithoutChildren<
		ComponentProps<typeof Sidebar.Group>
	> = $props();

	function isCurrent(url: string) {
		return page.url.pathname.startsWith(url);
	}
</script>

<Sidebar.Group {...restProps}>
	<Sidebar.GroupContent>
		<Sidebar.Menu>
			{#each items as item (item.title)}
				<Sidebar.MenuItem>
					<Sidebar.MenuButton isActive={isCurrent(item.url)} tooltipContent={item.title}>
						{#snippet child({ props })}
							<a href={item.url} {...props}>
								<item.icon />
								<span>{item.title}</span>
							</a>
						{/snippet}
					</Sidebar.MenuButton>
				</Sidebar.MenuItem>
			{/each}
		</Sidebar.Menu>
	</Sidebar.GroupContent>
</Sidebar.Group>
