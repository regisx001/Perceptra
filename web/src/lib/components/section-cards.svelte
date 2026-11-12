<script lang="ts">
	import DatabaseIcon from "@tabler/icons-svelte/icons/database";
	import BoltIcon from "@tabler/icons-svelte/icons/bolt";
	import TargetIcon from "@tabler/icons-svelte/icons/target";
	import RefreshDotIcon from "@tabler/icons-svelte/icons/refresh-dot";
	import TrendingUpIcon from "@tabler/icons-svelte/icons/trending-up";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
</script>

<div
	class="grid grid-cols-1 gap-4 px-4 lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4"
>
	<!-- Card 1: Indexed Dataset Images -->
	<Card.Root class="@container/card">
		<Card.Header>
			<Card.Description class="flex items-center gap-1.5 font-medium">
				<DatabaseIcon class="size-4 text-primary" />
				Indexed Images
			</Card.Description>
			<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
				10,000
			</Card.Title>
			<Card.Action>
				<Badge variant="outline" class="gap-1 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-950/20">
					<TrendingUpIcon class="size-3" />
					100%
				</Badge>
			</Card.Action>
		</Card.Header>
		<Card.Footer class="flex-col items-start gap-1 text-xs">
			<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
				GHIM-10K Reference Dataset
			</div>
			<div class="text-muted-foreground">20 semantic categories indexed</div>
		</Card.Footer>
	</Card.Root>

	<!-- Card 2: Feature Embeddings Extracted -->
	<Card.Root class="@container/card">
		<Card.Header>
			<Card.Description class="flex items-center gap-1.5 font-medium">
				<BoltIcon class="size-4 text-primary" />
				Feature Descriptors
			</Card.Description>
			<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
				512-D
			</Card.Title>
			<Card.Action>
				<Badge variant="outline" class="gap-1 border-primary/20 text-primary bg-primary/5">
					Hybrid
				</Badge>
			</Card.Action>
		</Card.Header>
		<Card.Footer class="flex-col items-start gap-1 text-xs">
			<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
				Color Moments + GLCM + LBP
			</div>
			<div class="text-muted-foreground">Z-score normalized & calibrated</div>
		</Card.Footer>
	</Card.Root>

	<!-- Card 3: Retrieval Accuracy (mAP@20) -->
	<Card.Root class="@container/card">
		<Card.Header>
			<Card.Description class="flex items-center gap-1.5 font-medium">
				<TargetIcon class="size-4 text-primary" />
				Precision Score (mAP)
			</Card.Description>
			<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
				84.2%
			</Card.Title>
			<Card.Action>
				<Badge variant="outline" class="gap-1 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-950/20">
					<TrendingUpIcon class="size-3" />
					+6.4%
				</Badge>
			</Card.Action>
		</Card.Header>
		<Card.Footer class="flex-col items-start gap-1 text-xs">
			<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
				Top-20 Nearest Neighbors
			</div>
			<div class="text-muted-foreground">Cosine & Mahalanobis metrics</div>
		</Card.Footer>
	</Card.Root>

	<!-- Card 4: Mean Query Latency -->
	<Card.Root class="@container/card">
		<Card.Header>
			<Card.Description class="flex items-center gap-1.5 font-medium">
				<RefreshDotIcon class="size-4 text-primary" />
				Avg Query Latency
			</Card.Description>
			<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
				18.4 ms
			</Card.Title>
			<Card.Action>
				<Badge variant="outline" class="gap-1 text-blue-600 dark:text-blue-400 border-blue-500/20 bg-blue-50/50 dark:bg-blue-950/20">
					Sub-20ms
				</Badge>
			</Card.Action>
		</Card.Header>
		<Card.Footer class="flex-col items-start gap-1 text-xs">
			<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
				Real-time Similarity Ranking
			</div>
			<div class="text-muted-foreground">Descriptor extraction + vector search</div>
		</Card.Footer>
	</Card.Root>
</div>
