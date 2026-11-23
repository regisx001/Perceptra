<script lang="ts">
	import { Button } from "#lib/components/ui/button/index.js";
	import XIcon from "@lucide/svelte/icons/x";
	import FolderInputIcon from "@lucide/svelte/icons/folder-input";
	import Trash2Icon from "@lucide/svelte/icons/trash-2";
	import CheckSquareIcon from "@lucide/svelte/icons/check-square";
	import * as m from "#lib/paraglide/messages.js";

	let {
		selectedCount = 0,
		totalCount = 0,
		allSelected = false,
		onSelectAll,
		onDeselectAll,
		onMove,
		onDelete,
	}: {
		selectedCount: number;
		totalCount: number;
		allSelected?: boolean;
		onSelectAll: () => void;
		onDeselectAll: () => void;
		onMove: () => void;
		onDelete: () => void;
	} = $props();
</script>

{#if selectedCount > 0}
	<div
		class="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 sm:gap-3 px-3.5 sm:px-4 py-2 sm:py-2.5 rounded-full bg-card/95 text-foreground border border-border/80 shadow-2xl backdrop-blur-xl animate-in fade-in slide-in-from-bottom-5 duration-200"
		role="toolbar"
		aria-label={m.batch_toolbar_aria()}
	>
		<!-- Deselect All / Close button -->
		<button
			type="button"
			class="size-7 rounded-full hover:bg-muted/80 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
			onclick={onDeselectAll}
			title={m.batch_deselect_all_tooltip()}
			aria-label={m.batch_deselect_all()}
		>
			<XIcon class="size-4" />
		</button>

		<!-- Selected count counter badge -->
		<div class="flex items-center gap-1.5 pl-0.5 pr-1 font-medium text-xs sm:text-sm">
			<span class="font-bold text-foreground font-mono">{selectedCount}</span>
			<span class="text-muted-foreground">{selectedCount === 1 ? m.batch_selected_singular() : m.batch_selected_plural()}</span>
		</div>

		<div class="h-4 w-px bg-border/80" aria-hidden="true"></div>

		<!-- Select All / Deselect Toggle -->
		<Button
			variant="ghost"
			size="sm"
			class="h-8 gap-1.5 px-2.5 text-xs font-semibold cursor-pointer text-muted-foreground hover:text-foreground hover:bg-muted/70 rounded-full"
			onclick={allSelected ? onDeselectAll : onSelectAll}
			title={allSelected ? m.batch_deselect_all() : `${m.batch_select_all()} (${totalCount})`}
		>
			<CheckSquareIcon class="size-3.5" />
			<span class="hidden sm:inline">{allSelected ? m.batch_clear() : m.batch_select_all()}</span>
		</Button>

		<!-- Move to Collection Button -->
		<Button
			variant="outline"
			size="sm"
			class="h-8 gap-1.5 px-3 text-xs font-semibold cursor-pointer shadow-2xs rounded-full hover:bg-primary hover:text-primary-foreground hover:border-primary transition-all"
			onclick={onMove}
			title={m.batch_move_tooltip()}
		>
			<FolderInputIcon class="size-3.5" />
			<span>{m.batch_move()}</span>
		</Button>

		<!-- Delete Button -->
		<Button
			variant="destructive"
			size="sm"
			class="h-8 gap-1.5 px-3 text-xs font-semibold cursor-pointer shadow-2xs rounded-full transition-all"
			onclick={onDelete}
			title={m.batch_delete_tooltip()}
		>
			<Trash2Icon class="size-3.5" />
			<span>{m.batch_delete()}</span>
		</Button>
	</div>
{/if}
