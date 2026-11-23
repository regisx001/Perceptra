<script lang="ts">
	import { onMount } from "svelte";
	import DatabaseIcon from "@tabler/icons-svelte/icons/database";
	import BoltIcon from "@tabler/icons-svelte/icons/bolt";
	import TargetIcon from "@tabler/icons-svelte/icons/target";
	import RefreshDotIcon from "@tabler/icons-svelte/icons/refresh-dot";
	import TrendingUpIcon from "@tabler/icons-svelte/icons/trending-up";
	import ThumbUpIcon from "@tabler/icons-svelte/icons/thumb-up";
	import SearchIcon from "@tabler/icons-svelte/icons/search";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Skeleton } from "#lib/components/ui/skeleton/index.js";
	import { analyticsClient, type AnalyticsOverview } from "#lib/analytics.js";
	import { cn } from "#lib/utils.js";

	interface Props {
		class?: string;
	}

	let { class: className = "" }: Props = $props();

	let overview = $state<AnalyticsOverview | null>(null);
	let isLoading = $state(true);

	onMount(async () => {
		try {
			const data = await analyticsClient.getOverview();
			overview = data;
		} catch (e) {
			console.error("Failed to load analytics overview:", e);
		} finally {
			isLoading = false;
		}
	});
</script>

<div
	class={cn("grid grid-cols-1 gap-4 sm:grid-cols-2 sm:grid-rows-2", className)}
>
	<!-- Card 1: Total Visual Searches -->
	<Card.Root class="@container/card justify-between">
		<Card.Header>
			<Card.Description class="flex items-center gap-1.5 font-medium">
				<SearchIcon class="size-4 text-primary" />
				Total Visual Searches
			</Card.Description>
			<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
				{#if isLoading}
					<Skeleton class="h-8 w-24" />
				{:else}
					{overview?.total_searches ?? 0}
				{/if}
			</Card.Title>
			<Card.Action>
				<Badge variant="outline" class="gap-1 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-950/20">
					<TrendingUpIcon class="size-3" />
					Recorded
				</Badge>
			</Card.Action>
		</Card.Header>
		<Card.Footer class="flex-col items-start gap-1 text-xs">
			<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
				Persisted Query Sessions
			</div>
			<div class="text-muted-foreground">Historical visual search activities across scopes</div>
		</Card.Footer>
	</Card.Root>

	<!-- Card 2: Feedback & FRE Iterations -->
	<Card.Root class="@container/card justify-between">
		<Card.Header>
			<Card.Description class="flex items-center gap-1.5 font-medium">
				<ThumbUpIcon class="size-4 text-primary" />
				Relevance Feedback Sessions
			</Card.Description>
			<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
				{#if isLoading}
					<Skeleton class="h-8 w-20" />
				{:else}
					{overview?.feedback_sessions ?? 0}
				{/if}
			</Card.Title>
			<Card.Action>
				<Badge variant="outline" class="gap-1 border-primary/20 text-primary bg-primary/5">
					FRE Group 13
				</Badge>
			</Card.Action>
		</Card.Header>
		<Card.Footer class="flex-col items-start gap-1 text-xs">
			<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
				{overview?.total_feedback_judgments ?? 0} total judgments
			</div>
			<div class="text-muted-foreground">
				{overview?.relevant_judgments ?? 0} relevant · {overview?.irrelevant_judgments ?? 0} irrelevant
			</div>
		</Card.Footer>
	</Card.Root>

	<!-- Card 3: Average Iterations per Search -->
	<Card.Root class="@container/card justify-between">
		<Card.Header>
			<Card.Description class="flex items-center gap-1.5 font-medium">
				<TargetIcon class="size-4 text-primary" />
				Avg Iterations / Search
			</Card.Description>
			<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
				{#if isLoading}
					<Skeleton class="h-8 w-16" />
				{:else}
					{overview?.average_iterations ?? 1.0}x
				{/if}
			</Card.Title>
			<Card.Action>
				<Badge variant="outline" class="gap-1 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-950/20">
					Interactive
				</Badge>
			</Card.Action>
		</Card.Header>
		<Card.Footer class="flex-col items-start gap-1 text-xs">
			<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
				Refinement Depth
			</div>
			<div class="text-muted-foreground">Initial retrieval + multi-round FRE re-ranking</div>
		</Card.Footer>
	</Card.Root>

	<!-- Card 4: Mean Retrieval Latency -->
	<Card.Root class="@container/card justify-between">
		<Card.Header>
			<Card.Description class="flex items-center gap-1.5 font-medium">
				<RefreshDotIcon class="size-4 text-primary" />
				Avg Retrieval Time
			</Card.Description>
			<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
				{#if isLoading}
					<Skeleton class="h-8 w-20" />
				{:else}
					{overview?.average_retrieval_time_ms ?? 0} ms
				{/if}
			</Card.Title>
			<Card.Action>
				<Badge variant="outline" class="gap-1 text-blue-600 dark:text-blue-400 border-blue-500/20 bg-blue-50/50 dark:bg-blue-950/20">
					Sub-second
				</Badge>
			</Card.Action>
		</Card.Header>
		<Card.Footer class="flex-col items-start gap-1 text-xs">
			<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
				Feature extraction + FRE ranking
			</div>
			<div class="text-muted-foreground">Measured across candidate search spaces</div>
		</Card.Footer>
	</Card.Root>
</div>
