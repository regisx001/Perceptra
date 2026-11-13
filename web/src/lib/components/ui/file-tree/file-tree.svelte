<script lang="ts">
	import { setContext, type Snippet } from "svelte";
	import { cn } from "#lib/utils.js";

	let {
		class: className,
		selectedId = $bindable(""),
		onSelect,
		children,
		...restProps
	}: {
		class?: string;
		selectedId?: string;
		onSelect?: (id: string) => void;
		children?: Snippet;
		[key: string]: any;
	} = $props();

	setContext("file-tree", {
		getSelectedId: () => selectedId,
		select: (id: string) => {
			selectedId = id;
			onSelect?.(id);
		}
	});
</script>

<div
	role="tree"
	class={cn("flex flex-col gap-0.5 text-xs select-none", className)}
	{...restProps}
>
	{@render children?.()}
</div>
