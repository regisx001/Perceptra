<script lang="ts">
	import { onMount } from "svelte";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Dialog from "#lib/components/ui/dialog/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import { Skeleton } from "#lib/components/ui/skeleton/index.js";
	import { Separator } from "#lib/components/ui/separator/index.js";
	import {
		analyticsClient,
		type RetrievalQueryDetail,
		type HistoryListResponse,
	} from "#lib/analytics.js";
	import HistoryIcon from "@tabler/icons-svelte/icons/history";
	import TrashIcon from "@tabler/icons-svelte/icons/trash";
	import RefreshDotIcon from "@tabler/icons-svelte/icons/refresh-dot";
	import PhotoIcon from "@tabler/icons-svelte/icons/photo";
	import ArrowRightIcon from "@tabler/icons-svelte/icons/arrow-right";
	import CheckIcon from "@tabler/icons-svelte/icons/check";
	import XIcon from "@tabler/icons-svelte/icons/x";

	let historyData = $state<HistoryListResponse | null>(null);
	let isLoading = $state(true);
	let selectedQueryDetail = $state<RetrievalQueryDetail | null>(null);
	let isDetailOpen = $state(false);
	let isDeletingId = $state<string | null>(null);

	async function loadHistory(page = 1) {
		isLoading = true;
		try {
			historyData = await analyticsClient.listHistory(page, 10);
		} catch (e) {
			console.error("Failed to fetch retrieval history:", e);
		} finally {
			isLoading = false;
		}
	}

	async function openDetail(queryId: string) {
		try {
			selectedQueryDetail = await analyticsClient.getHistoryDetail(queryId);
			isDetailOpen = true;
		} catch (e) {
			console.error("Failed to load search detail:", e);
		}
	}

	async function handleDelete(queryId: string, event: MouseEvent) {
		event.stopPropagation();
		if (!confirm("Are you sure you want to delete this search and all its iterations?")) return;
		isDeletingId = queryId;
		try {
			const success = await analyticsClient.deleteHistory(queryId);
			if (success) {
				await loadHistory(historyData?.pagination.page || 1);
			}
		} catch (e) {
			console.error("Failed to delete search:", e);
		} finally {
			isDeletingId = null;
		}
	}

	onMount(() => {
		loadHistory();
	});
</script>

<div class="px-4 lg:px-6">
	<Card.Root>
		<Card.Header class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
			<div>
				<Card.Title class="flex items-center gap-2 text-base font-semibold">
					<HistoryIcon class="size-4 text-primary" />
					Visual Retrieval History Log
				</Card.Title>
				<Card.Description>
					Chronological record of past visual queries, scope configurations, and relevance feedback refinements
				</Card.Description>
			</div>
			<Button
				variant="outline"
				size="sm"
				class="h-8 gap-1.5 text-xs self-start sm:self-auto"
				onclick={() => loadHistory(historyData?.pagination.page || 1)}
			>
				<RefreshDotIcon class="size-3.5" />
				<span>Refresh</span>
			</Button>
		</Card.Header>
		<Card.Content>
			{#if isLoading}
				<div class="flex flex-col gap-3 py-4">
					{#each Array(4) as _}
						<Skeleton class="h-16 w-full rounded-lg" />
					{/each}
				</div>
			{:else if !historyData?.items || historyData.items.length === 0}
				<div class="flex flex-col items-center justify-center py-12 text-center text-sm text-muted-foreground">
					<PhotoIcon class="size-10 stroke-1 text-muted-foreground/60 mb-2" />
					<p class="font-medium text-foreground">No visual searches recorded yet</p>
					<p class="text-xs">Run a query from the Visual Query Studio to record search and feedback iterations.</p>
					<Button href="/dashboard/query" size="sm" class="mt-4 text-xs">
						Launch Visual Query
					</Button>
				</div>
			{:else}
				<div class="flex flex-col divide-y divide-border/40">
					{#each historyData.items as item (item.id)}
						<!-- History Row Item -->
						<div
							role="button"
							tabindex="0"
							onclick={() => openDetail(item.id)}
							onkeydown={(e) => e.key === "Enter" && openDetail(item.id)}
							class="flex flex-col gap-3 py-3.5 sm:flex-row sm:items-center sm:justify-between transition-colors hover:bg-muted/30 px-2 rounded-lg cursor-pointer"
						>
							<div class="flex items-center gap-3">
								<!-- Thumbnail / Source Indicator -->
								<div class="size-11 shrink-0 overflow-hidden rounded-md border border-border/60 bg-muted/50 flex items-center justify-center">
									{#if item.query_source === "upload" && item.query_storage_key}
										<img
											src={`/api/v1/retrieval-history/${item.id}/file`}
											alt="Query Upload"
											class="size-full object-cover"
										/>
									{:else if item.query_image_id}
										<img
											src={`/api/v1/images/${item.query_image_id}/file?preview=true`}
											alt="Gallery Query"
											class="size-full object-cover"
										/>
									{:else}
										<PhotoIcon class="size-5 text-muted-foreground" />
									{/if}
								</div>

								<div class="flex flex-col gap-1">
									<div class="flex items-center gap-2">
										<span class="font-medium text-sm text-foreground">
											{item.query_image?.filename || (item.query_source === "upload" ? "Uploaded Image Query" : "Reference Query")}
										</span>
										<Badge variant="outline" class="text-[10px] uppercase font-mono tracking-wider">
											{item.query_source}
										</Badge>
										<Badge variant="secondary" class="text-[10px] font-mono">
											Scope: {item.search_scope}
										</Badge>
									</div>
									<div class="flex items-center gap-2 text-xs text-muted-foreground">
										<span>
											{item.created_at ? new Date(item.created_at).toLocaleString() : "Recent"}
										</span>
										<span>&bull;</span>
										<span class="font-medium text-foreground">
											Top-K: {item.configuration?.top_k ?? 12}
										</span>
										<span>&bull;</span>
										<span>
											Metric: {item.configuration?.metric ?? "cosine"}
										</span>
									</div>
								</div>
							</div>

							<!-- Iteration count & Action buttons -->
							<div class="flex items-center gap-2.5 sm:justify-end">
								<Badge
									variant="outline"
									class="text-xs font-semibold border-primary/30 text-primary bg-primary/5"
								>
									{item.iterations_count} {item.iterations_count === 1 ? "Iteration" : "Iterations"}
								</Badge>

								<Button
									variant="ghost"
									size="icon-sm"
									class="text-destructive/80 hover:text-destructive hover:bg-destructive/10"
									onclick={(e) => handleDelete(item.id, e)}
									disabled={isDeletingId === item.id}
									title="Delete search history"
								>
									<TrashIcon class="size-4" />
								</Button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</Card.Content>
	</Card.Root>
</div>

<!-- Modal: Comprehensive Search & Iteration Details -->
<Dialog.Root bind:open={isDetailOpen}>
	<Dialog.Content class="max-w-3xl max-h-[85vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title class="flex items-center gap-2 text-lg">
				<HistoryIcon class="size-5 text-primary" />
				Search Session Inspection
			</Dialog.Title>
			<Dialog.Description>
				Detailed breakdown of feature weights, nearest neighbors, and user feedback judgments per iteration.
			</Dialog.Description>
		</Dialog.Header>

		{#if selectedQueryDetail}
			<div class="flex flex-col gap-6 py-2">
				<!-- Header Info -->
				<div class="flex flex-col gap-2 rounded-lg border border-border/50 bg-muted/20 p-3 text-xs">
					<div class="flex items-center justify-between">
						<span class="font-semibold text-foreground">Session ID: {selectedQueryDetail.id}</span>
						<Badge variant="outline" class="font-mono">{selectedQueryDetail.status}</Badge>
					</div>
					<div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-muted-foreground pt-1">
						<div>Scope: <span class="font-medium text-foreground">{selectedQueryDetail.search_scope}</span></div>
						<div>Metric: <span class="font-medium text-foreground">{selectedQueryDetail.configuration?.metric ?? "cosine"}</span></div>
						<div>Top-K: <span class="font-medium text-foreground">{selectedQueryDetail.configuration?.top_k ?? 12}</span></div>
						<div>Date: <span class="font-medium text-foreground">{new Date(selectedQueryDetail.created_at).toLocaleDateString()}</span></div>
					</div>
				</div>

				<!-- Iterations Accordion / List -->
				<div class="flex flex-col gap-4">
					<h4 class="text-sm font-semibold text-foreground">
						Retrieval Iterations ({selectedQueryDetail.iterations?.length ?? 0})
					</h4>

					{#each selectedQueryDetail.iterations || [] as iter (iter.id)}
						<div class="flex flex-col gap-3 rounded-lg border border-border/60 p-4 bg-card">
							<!-- Iteration Header -->
							<div class="flex items-center justify-between">
								<div class="flex items-center gap-2">
									<Badge class="font-semibold text-xs">
										Iteration #{iter.iteration_number}
									</Badge>
									<span class="text-xs text-muted-foreground">
										Method: <strong class="text-foreground uppercase">{iter.retrieval_method}</strong>
									</span>
									<span class="text-xs text-muted-foreground">
										({iter.execution_time_ms} ms)
									</span>
								</div>
								<span class="text-xs text-muted-foreground">
									{iter.results_count} returned / {iter.total_candidates} candidates
								</span>
							</div>

							<!-- Feature Weights for this iteration -->
							{#if iter.feature_weights}
								<div class="flex flex-col gap-1.5 pt-1">
									<span class="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
										Feature Relevance Weights
									</span>
									<div class="flex flex-wrap gap-1.5">
										{#each Object.entries(iter.feature_weights) as [feat, weight]}
											<Badge variant="outline" class="text-xs font-mono">
												{feat}: <span class="font-bold text-primary ml-1">{weight}</span>
											</Badge>
										{/each}
									</div>
								</div>
							{/if}

							<!-- User Judgments if any on this iteration -->
							{#if iter.feedback && iter.feedback.length > 0}
								<div class="flex flex-col gap-1.5 pt-1">
									<span class="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
										User Judgments on this Iteration ({iter.feedback.length})
									</span>
									<div class="flex flex-wrap gap-2">
										{#each iter.feedback as fb}
											<div class="flex items-center gap-1 rounded-md border border-border px-2 py-0.5 text-xs">
												{#if fb.judgment === "relevant"}
													<CheckIcon class="size-3 text-emerald-500" />
													<span class="font-medium text-emerald-600 dark:text-emerald-400">Relevant</span>
												{:else}
													<XIcon class="size-3 text-rose-500" />
													<span class="font-medium text-rose-600 dark:text-rose-400">Irrelevant</span>
												{/if}
												<span class="font-mono text-[10px] text-muted-foreground ml-1">
													{fb.image?.filename || fb.image_id.slice(0, 8)}
												</span>
											</div>
										{/each}
									</div>
								</div>
							{/if}

							<!-- Top Ranked Results Thumbnails -->
							{#if iter.results && iter.results.length > 0}
								<div class="flex flex-col gap-1.5 pt-2">
									<span class="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">
										Top Ranked Results Preview
									</span>
									<div class="grid grid-cols-4 sm:grid-cols-6 gap-2">
										{#each iter.results.slice(0, 6) as res}
											<div class="group relative aspect-square overflow-hidden rounded-md border border-border/60 bg-muted/30">
												<img
													src={`/api/v1/images/${res.image_id}/file?preview=true`}
													alt={res.image?.filename || "Result"}
													class="size-full object-cover"
												/>
												<div class="absolute inset-x-0 bottom-0 bg-background/90 backdrop-blur-xs px-1 py-0.5 text-[10px] font-mono text-center truncate">
													#{res.rank} ({res.similarity_score.toFixed(3)})
												</div>
											</div>
										{/each}
									</div>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		{/if}
	</Dialog.Content>
</Dialog.Root>
