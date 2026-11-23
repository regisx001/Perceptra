<script lang="ts">
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as m from "#lib/paraglide/messages.js";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";

	let {
		isExtracting = false,
		onExtract
	}: {
		isExtracting?: boolean;
		onExtract: () => void;
	} = $props();
</script>

<Card.Root class="border-dashed border-2 bg-card/60 p-8 text-center backdrop-blur-sm">
	<div class="mx-auto flex max-w-lg flex-col items-center">
		{#if isExtracting}
			<div class="mb-4 flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary ring-8 ring-primary/5">
				<Loader2Icon class="size-6 animate-spin" />
			</div>
		{/if}

		<h3 class="text-xl font-semibold tracking-tight text-foreground">
			{isExtracting ? m.image_detail_extracting() : m.image_detail_unindexed_title()}
		</h3>

		<p class="mt-2 text-sm text-muted-foreground leading-relaxed">
			{m.image_detail_unindexed_desc()}
		</p>

		<!-- Feature badges preview -->
		<div class="mt-6 flex flex-wrap items-center justify-center gap-2">
			<span class="rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				{m.query_settings_feat_dominant_colors()}
			</span>
			<span class="rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				{m.query_settings_feat_color_hist()}
			</span>
			<span class="rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				{m.query_settings_feat_color_moments()}
			</span>
			<span class="rounded-full border border-border bg-muted/50 px-2.5 py-1 text-xs text-muted-foreground">
				{m.query_settings_group_texture()}
			</span>
		</div>

		<div class="mt-7">
			<Button
				variant="default"
				size="lg"
				disabled={isExtracting}
				onclick={onExtract}
				class="gap-2 shadow-sm"
			>
				{#if isExtracting}
					<Loader2Icon class="size-4 animate-spin" />
					<span>{m.image_detail_extracting()}</span>
				{:else}
					<span>{m.image_detail_unindexed_btn()}</span>
				{/if}
			</Button>
		</div>
	</div>
</Card.Root>
