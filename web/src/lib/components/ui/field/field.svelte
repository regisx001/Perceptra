<script lang="ts" module>
	import { tv, type VariantProps } from "tailwind-variants";

	export const fieldVariants = tv({
		base: "flex w-full group/field data-[invalid=true]:text-destructive",
		variants: {
			orientation: {
				vertical: "flex-col gap-2",
				horizontal: "flex-row items-center gap-3",
				responsive: "flex-col gap-2 sm:flex-row sm:items-center sm:gap-3",
			},
		},
		defaultVariants: {
			orientation: "vertical",
		},
	});

	export type FieldOrientation = VariantProps<typeof fieldVariants>["orientation"];
</script>

<script lang="ts">
	import { cn, type WithElementRef } from "#lib/utils.js";
	import type { HTMLAttributes } from "svelte/elements";

	let {
		ref = $bindable(null),
		class: className,
		orientation = "vertical",
		children,
		...restProps
	}: WithElementRef<HTMLAttributes<HTMLDivElement>> & {
		orientation?: FieldOrientation;
	} = $props();
</script>

<div
	bind:this={ref}
	role="group"
	data-slot="field"
	data-orientation={orientation}
	class={cn(fieldVariants({ orientation }), className)}
	{...restProps}
>
	{@render children?.()}
</div>
