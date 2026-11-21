<script lang="ts">
	import { onMount } from "svelte";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Progress } from "#lib/components/ui/progress/index.js";
	import { analyticsClient, type AnalyticsFeedback, type AnalyticsDescriptors, type AnalyticsPerformance } from "#lib/analytics.js";
	import SlidersIcon from "@tabler/icons-svelte/icons/adjustments";
	import ActivityIcon from "@tabler/icons-svelte/icons/activity";
	import CheckCircleIcon from "@tabler/icons-svelte/icons/circle-check";
	import ClockIcon from "@tabler/icons-svelte/icons/clock";

	let feedbackStats = $state<AnalyticsFeedback | null>(null);
	let descriptorStats = $state<AnalyticsDescriptors | null>(null);
	let performanceStats = $state<AnalyticsPerformance | null>(null);
	let isLoading = $state(true);

	onMount(async () => {
		try {
			const [fb, desc, perf] = await Promise.all([
				analyticsClient.getFeedback(),
				analyticsClient.getDescriptors(),
				analyticsClient.getPerformance(),
			]);
			feedbackStats = fb;
			descriptorStats = desc;
			performanceStats = perf;
		} catch (e) {
			console.error("Failed to load deep analytics:", e);
		} finally {
			isLoading = false;
		}
	});

	// Normalize feature weights for visualization
	const featureWeightEntries = $derived.by(() => {
		if (!feedbackStats?.feature_weight_evolution) return [];
		return Object.entries(feedbackStats.feature_weight_evolution);
	});
</script>

<div class="grid grid-cols-1 gap-4 px-4 lg:px-6 md:grid-cols-2 lg:grid-cols-3">
	<!-- Panel 1: Relevance Feedback Ratio & FRE Estimation -->
	<Card.Root>
		<Card.Header>
			<div class="flex items-center justify-between">
				<Card.Title class="flex items-center gap-2 text-base">
					<CheckCircleIcon class="size-4 text-emerald-500" />
					Relevance Judgment Behavior
				</Card.Title>
				<Badge variant="outline" class="text-xs">
					Ratio: {feedbackStats?.ratio ?? 0}
				</Badge>
			</div>
			<Card.Description>
				Relevant vs. Irrelevant user judgments recorded
			</Card.Description>
		</Card.Header>
		<Card.Content class="flex flex-col gap-4">
			<div class="flex items-center justify-between text-sm">
				<div class="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400 font-medium">
					<span>Relevant</span>
					<Badge variant="outline" class="border-emerald-500/20 bg-emerald-500/10">
						{feedbackStats?.relevant_count ?? 0}
					</Badge>
				</div>
				<div class="flex items-center gap-1.5 text-rose-600 dark:text-rose-400 font-medium">
					<span>Irrelevant</span>
					<Badge variant="outline" class="border-rose-500/20 bg-rose-500/10">
						{feedbackStats?.irrelevant_count ?? 0}
					</Badge>
				</div>
			</div>

			<Progress
				value={
					(feedbackStats?.relevant_count ?? 0) + (feedbackStats?.irrelevant_count ?? 0) > 0
						? Math.round(
								((feedbackStats?.relevant_count ?? 0) /
									((feedbackStats?.relevant_count ?? 0) + (feedbackStats?.irrelevant_count ?? 0))) *
									100,
						  )
						: 50
				}
				class="h-2.5"
			/>

			<div class="rounded-lg border border-border/40 bg-muted/20 p-2.5 text-xs text-muted-foreground flex flex-col gap-1">
				<div class="font-medium text-foreground">
					Avg Feedback per Search: {feedbackStats?.average_judgments_per_search ?? 0} judgments
				</div>
				<div>Higher ratios accelerate positive feature clustering in FRE Group 13.</div>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Panel 2: Descriptor Strategy & Preferences -->
	<Card.Root>
		<Card.Header>
			<div class="flex items-center justify-between">
				<Card.Title class="flex items-center gap-2 text-base">
					<SlidersIcon class="size-4 text-primary" />
					Descriptor Combinations
				</Card.Title>
				<Badge variant="outline" class="text-xs">
					Hybrid: {descriptorStats?.categories.hybrid ?? 0}
				</Badge>
			</div>
			<Card.Description>
				Color vs. Texture vs. Hybrid visual search usage
			</Card.Description>
		</Card.Header>
		<Card.Content class="flex flex-col gap-3">
			<div class="flex flex-col gap-2">
				{#if descriptorStats?.descriptor_usage}
					{#each Object.entries(descriptorStats.descriptor_usage) as [desc, count]}
						<div class="flex items-center justify-between text-xs">
							<span class="font-mono text-muted-foreground truncate">{desc}</span>
							<Badge variant="secondary" class="font-mono text-[11px]">
								{count} queries
							</Badge>
						</div>
					{/each}
				{:else}
					<div class="text-xs text-muted-foreground">No queries recorded yet.</div>
				{/if}
			</div>

			<div class="mt-auto grid grid-cols-3 gap-1.5 pt-2 border-t border-border/40 text-center text-xs">
				<div class="rounded-md bg-muted/40 p-1.5">
					<div class="text-[10px] text-muted-foreground">Color Only</div>
					<div class="font-semibold">{descriptorStats?.categories.color_only ?? 0}</div>
				</div>
				<div class="rounded-md bg-muted/40 p-1.5">
					<div class="text-[10px] text-muted-foreground">Texture Only</div>
					<div class="font-semibold">{descriptorStats?.categories.texture_only ?? 0}</div>
				</div>
				<div class="rounded-md bg-muted/40 p-1.5">
					<div class="text-[10px] text-muted-foreground">Hybrid (Both)</div>
					<div class="font-semibold">{descriptorStats?.categories.hybrid ?? 0}</div>
				</div>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Panel 3: System Latency & Retrieval Performance -->
	<Card.Root class="md:col-span-2 lg:col-span-1">
		<Card.Header>
			<div class="flex items-center justify-between">
				<Card.Title class="flex items-center gap-2 text-base">
					<ClockIcon class="size-4 text-blue-500" />
					Retrieval Latency
				</Card.Title>
				<Badge variant="outline" class="text-xs text-blue-600 dark:text-blue-400">
					Avg: {performanceStats?.average_ms ?? 0} ms
				</Badge>
			</div>
			<Card.Description>
				Candidate distance calculation &amp; FRE re-ranking execution
			</Card.Description>
		</Card.Header>
		<Card.Content class="flex flex-col gap-3">
			<div class="grid grid-cols-3 gap-2 text-center text-xs">
				<div class="rounded-lg border border-border/50 bg-muted/30 p-2">
					<div class="text-[11px] text-muted-foreground">Min Latency</div>
					<div class="text-base font-bold tabular-nums text-foreground">
						{performanceStats?.min_ms ?? 0} <span class="text-xs font-normal">ms</span>
					</div>
				</div>
				<div class="rounded-lg border border-border/50 bg-muted/30 p-2">
					<div class="text-[11px] text-muted-foreground">Average</div>
					<div class="text-base font-bold tabular-nums text-foreground">
						{performanceStats?.average_ms ?? 0} <span class="text-xs font-normal">ms</span>
					</div>
				</div>
				<div class="rounded-lg border border-border/50 bg-muted/30 p-2">
					<div class="text-[11px] text-muted-foreground">Max Latency</div>
					<div class="text-base font-bold tabular-nums text-foreground">
						{performanceStats?.max_ms ?? 0} <span class="text-xs font-normal">ms</span>
					</div>
				</div>
			</div>

			<!-- Recent Execution Timeline Snippet -->
			<div class="flex flex-col gap-1.5 pt-1 text-xs">
				<span class="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
					Recent Iterations Latency Log
				</span>
				<div class="max-h-24 overflow-y-auto flex flex-col gap-1 pr-1 font-mono text-[11px]">
					{#if performanceStats?.recent_latencies && performanceStats.recent_latencies.length > 0}
						{#each performanceStats.recent_latencies.slice(0, 4) as item}
							<div class="flex items-center justify-between rounded bg-muted/30 px-2 py-1">
								<span>Iter #{item.iteration_number} ({item.candidates} cands)</span>
								<span class="font-semibold text-primary">{item.execution_time_ms} ms</span>
							</div>
						{/each}
					{:else}
						<div class="text-muted-foreground text-xs py-2">No queries logged yet.</div>
					{/if}
				</div>
			</div>
		</Card.Content>
	</Card.Root>
</div>
