<script lang="ts">
	import SunIcon from "@tabler/icons-svelte/icons/sun";
	import MoonIcon from "@tabler/icons-svelte/icons/moon";
	import DeviceDesktopIcon from "@tabler/icons-svelte/icons/device-desktop";
	import CheckIcon from "@tabler/icons-svelte/icons/check";
	import * as DropdownMenu from "#lib/components/ui/dropdown-menu/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { setMode, resetMode, mode } from "mode-watcher";
	import * as m from "#lib/paraglide/messages.js";

	let { class: className = "" }: { class?: string } = $props();
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button
				{...props}
				variant="outline"
				size="sm"
				class="h-8 w-8 p-0 {className}"
				title={m.theme_toggle()}
				aria-label={m.theme_toggle()}
			>
				<SunIcon class="size-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 text-foreground" />
				<MoonIcon class="absolute size-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 text-foreground" />
				<span class="sr-only">{m.theme_toggle()}</span>
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="end" class="min-w-36">
		<DropdownMenu.Group>
			<DropdownMenu.Item
				onclick={() => setMode("light")}
				class="flex items-center justify-between text-xs font-semibold cursor-pointer"
			>
				<div class="flex items-center gap-2">
					<SunIcon class="size-4 text-muted-foreground" />
					<span>{m.theme_light()}</span>
				</div>
				{#if mode.current === "light"}
					<CheckIcon class="size-3.5 text-primary" />
				{/if}
			</DropdownMenu.Item>
			<DropdownMenu.Item
				onclick={() => setMode("dark")}
				class="flex items-center justify-between text-xs font-semibold cursor-pointer"
			>
				<div class="flex items-center gap-2">
					<MoonIcon class="size-4 text-muted-foreground" />
					<span>{m.theme_dark()}</span>
				</div>
				{#if mode.current === "dark"}
					<CheckIcon class="size-3.5 text-primary" />
				{/if}
			</DropdownMenu.Item>
			<DropdownMenu.Item
				onclick={() => resetMode()}
				class="flex items-center justify-between text-xs font-semibold cursor-pointer"
			>
				<div class="flex items-center gap-2">
					<DeviceDesktopIcon class="size-4 text-muted-foreground" />
					<span>{m.theme_system()}</span>
				</div>
				{#if mode.current === undefined}
					<CheckIcon class="size-3.5 text-primary" />
				{/if}
			</DropdownMenu.Item>
		</DropdownMenu.Group>
	</DropdownMenu.Content>
</DropdownMenu.Root>
