<script lang="ts">
	import { getContext, type Snippet } from "svelte";
	import * as Collapsible from "#lib/components/ui/collapsible/index.js";
	import ChevronRightIcon from "@lucide/svelte/icons/chevron-right";
	import ChevronDownIcon from "@lucide/svelte/icons/chevron-down";
	import FolderIcon from "@lucide/svelte/icons/folder";
	import FolderOpenIcon from "@lucide/svelte/icons/folder-open";
	import { cn } from "#lib/utils.js";

	let {
		id,
		name,
		open = $bindable(),
		count,
		class: className,
		children,
		actions,
		...restProps
	}: {
		id: string;
		name: string;
		open?: boolean;
		count?: number;
		class?: string;
		children?: Snippet;
		actions?: Snippet;
		[key: string]: any;
	} = $props();

	// Local state fallback if open is undefined
	let isOpen = $state(open ?? false);
	$effect(() => {
		if (open !== undefined) {
			isOpen = open;
		}
	});

	function handleOpenChange(val: boolean) {
		isOpen = val;
		open = val;
	}

	const tree = getContext<{
		getSelectedId: () => string;
		select: (id: string) => void;
	}>("file-tree");

	let isSelected = $derived(tree?.getSelectedId() === id);
</script>

<Collapsible.Root
	open={isOpen}
	onOpenChange={handleOpenChange}
	class="flex flex-col"
>
	<div
		class={cn(
			"group/folder relative flex items-center justify-between rounded-lg px-2 py-1.5 transition-colors cursor-pointer",
			isSelected
				? "bg-muted font-medium text-foreground ring-1 ring-border"
				: "hover:bg-muted/50 text-muted-foreground hover:text-foreground",
			className
		)}
		onclick={() => tree?.select(id)}
		{...restProps}
	>
		<div class="flex items-center gap-1.5 truncate">
			<Collapsible.Trigger
				class="p-0.5 rounded-sm hover:bg-muted text-muted-foreground hover:text-foreground"
				onclick={(e) => e.stopPropagation()}
			>
				{#if isOpen}
					<ChevronDownIcon class="size-3" />
				{:else}
					<ChevronRightIcon class="size-3" />
				{/if}
			</Collapsible.Trigger>

			{#if isOpen}
				<FolderOpenIcon class="size-3.5 text-foreground/80 shrink-0" />
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

	<Collapsible.Content class="pl-4 flex flex-col gap-0.5 pt-0.5">
		{@render children?.()}
	</Collapsible.Content>
</Collapsible.Root>
