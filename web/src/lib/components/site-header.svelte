<script lang="ts">
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Separator } from "#lib/components/ui/separator/index.js";
	import { useLocale } from "#lib/i18n.svelte.js";
	import GlobeIcon from "@lucide/svelte/icons/globe";

	const locale = useLocale();
</script>

<header
	class="sticky top-0 z-20 flex h-(--header-height) shrink-0 items-center justify-between gap-3 border-b bg-background/95 px-4 backdrop-blur-xs transition-[width,height] ease-linear lg:px-6"
>
	<div class="flex items-center gap-2">
		<Sidebar.Trigger class="-ms-1" />
		<Separator orientation="vertical" class="mx-1 h-4" />
		
		<div class="flex items-center gap-2">
			<span class="text-sm font-semibold tracking-tight text-foreground">Perceptra</span>
			<span class="text-xs text-muted-foreground">/</span>
			<span class="text-xs text-muted-foreground font-medium">Dashboard</span>
		</div>
	</div>

	<div class="flex items-center gap-2">
		<!-- Language Switcher -->
		<Button
			variant="outline"
			size="sm"
			class="h-8 gap-1.5 px-2.5 text-xs font-medium"
			onclick={() => locale.set(locale.current === "en" ? "fr" : "en")}
			aria-label="Toggle language"
		>
			<GlobeIcon class="size-3.5" />
			<span class="uppercase">{locale.current}</span>
		</Button>
	</div>
</header>
