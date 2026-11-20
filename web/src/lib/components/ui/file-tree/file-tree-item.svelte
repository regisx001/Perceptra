<script lang="ts">
	import { getContext, type Snippet } from "svelte";
	import FolderIcon from "@lucide/svelte/icons/folder";
	import { cn } from "#lib/utils.js";

	let {
		id,
		name,
		count,
		class: className,
		icon,
		actions,
		...restProps
	}: {
		id: string;
		name: string;
		count?: number;
		class?: string;
		icon?: Snippet;
		actions?: Snippet;
		[key: string]: any;
	} = $props();

	const tree = getContext<{
		getSelectedId: () => string;
		select: (id: string) => void;
	}>("file-tree");

	let isSelected = $derived(tree?.getSelectedId() === id);
</script>

<div
	role="treeitem"
	aria-selected={isSelected}
	class={cn(
		"group/item relative flex items-center justify-between rounded-lg px-2 py-1.5 transition-colors cursor-pointer",
		isSelected
			? "bg-muted font-medium text-foreground ring-1 ring-border"
			: "hover:bg-muted/50 text-muted-foreground hover:text-foreground",
		className
	)}
	onclick={() => tree?.select(id)}
	{...restProps}
>
	<div class="flex items-center gap-1.5 truncate">
		<span class="size-3 shrink-0"></span>

		{#if icon}
			{@render icon()}
		{:else}
			<FolderIcon class="size-3.5 text-foreground/70 shrink-0" />
		{/if}

		<span class="truncate">{name}</span>
	</div>

	<div class="flex items-center gap-2">
		{#if count !== undefined}
			<span class="text-[11px] tabular-nums text-muted-foreground/80">
				{count.toLocaleString()} images
			</span>
		{/if}

		{#if actions}
			<!-- svelte-ignore a11y_click_events_have_key_events -->
			<!-- svelte-ignore a11y_no_static_element_interactions -->
			<div role="presentation" class="flex items-center" onclick={(e) => e.stopPropagation()}>
				{@render actions()}
			</div>
		{/if}
	</div>
</div>
