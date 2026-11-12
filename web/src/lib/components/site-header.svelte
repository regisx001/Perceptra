<script lang="ts">
	import * as Sidebar from "#lib/components/ui/sidebar/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Separator } from "#lib/components/ui/separator/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { useLocale } from "#lib/i18n.svelte.js";
	import GlobeIcon from "@lucide/svelte/icons/globe";
	import DatabaseIcon from "@tabler/icons-svelte/icons/database";
	import SparklesIcon from "@tabler/icons-svelte/icons/sparkles";

	const locale = useLocale();
</script>

<header
	class="flex h-(--header-height) shrink-0 items-center justify-between gap-3 border-b bg-background/95 px-4 backdrop-blur-xs transition-[width,height] ease-linear lg:px-6"
>
	<div class="flex items-center gap-2">
		<Sidebar.Trigger class="-ms-1" />
		<Separator orientation="vertical" class="mx-1 h-4" />
		
		<div class="flex items-center gap-2">
			<span class="text-sm font-semibold tracking-tight text-foreground">Perceptra</span>
			<span class="text-xs text-muted-foreground">/</span>
			<span class="text-xs text-muted-foreground font-medium">Dashboard</span>
			<Badge variant="outline" class="hidden sm:inline-flex items-center gap-1 text-[11px] font-normal border-primary/20 text-primary bg-primary/5">
				<SparklesIcon class="size-3" />
				GHIM-10K Online
			</Badge>
		</div>
	</div>

	<div class="flex items-center gap-2">
		<!-- Metric quick summary pill -->
		<div class="hidden md:flex items-center gap-2 rounded-md border border-border/60 bg-muted/40 px-2.5 py-1 text-xs text-muted-foreground">
			<DatabaseIcon class="size-3.5 text-foreground/70" />
			<span>Active Index: <strong class="text-foreground font-medium">10,000 vectors</strong> (Color + GLCM + LBP)</span>
		</div>

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
