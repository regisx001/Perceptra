<script lang="ts">
	import { onMount } from "svelte";
	import * as m from "#lib/paraglide/messages.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Popover from "#lib/components/ui/popover/index.js";
	import * as Command from "#lib/components/ui/command/index.js";
	import { Switch } from "#lib/components/ui/switch/index.js";
	import { Progress } from "#lib/components/ui/progress/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import * as Table from "#lib/components/ui/table/index.js";
	import { categoryService, type CategoryItem } from "#lib/categories.js";
	import { imageService, type ImageItem } from "#lib/images.js";
	import UploadCloudIcon from "@lucide/svelte/icons/upload-cloud";
	import PlayIcon from "@lucide/svelte/icons/play";
	import XIcon from "@lucide/svelte/icons/x";
	import ImageIcon from "@lucide/svelte/icons/image";
	import CheckIcon from "@lucide/svelte/icons/check";
	import ChevronsUpDownIcon from "@lucide/svelte/icons/chevrons-up-down";
	import PlusIcon from "@lucide/svelte/icons/plus";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import AlertCircleIcon from "@lucide/svelte/icons/alert-circle";
	import FolderIcon from "@lucide/svelte/icons/folder";

	interface UploadQueueItem {
		id: string;
		file: File;
		name: string;
		sizeStr: string;
		status: "Pending" | "Uploading" | "Completed" | "Error";
		progress: number;
		thumbnailUrl?: string;
		error?: string;
		uploadedImage?: ImageItem;
	}

	interface FlatCategoryOption {
		id: string;
		name: string;
		path: string;
	}

	// State
	let categories = $state<CategoryItem[]>([]);
	let flatCategoryOptions = $state<FlatCategoryOption[]>([]);
	let selectedCategoryId = $state<string>("uncategorized");
	let categoryOpen = $state(false);
	let categorySearch = $state("");
	let processAfterUpload = $state(true);
	let isDragging = $state(false);
	let isUploading = $state(false);
	let fileInputRef = $state<HTMLInputElement | null>(null);
	let queue = $state<UploadQueueItem[]>([]);
	let isCreatingCategory = $state(false);

	// Load categories from API
	async function loadCategories() {
		try {
			const res = await categoryService.getCategories({ tree: true });
			categories = res;
			flatCategoryOptions = flattenCategories(res);
		} catch (err: any) {
			console.warn("Could not load categories:", err.message);
		}
	}

	function flattenCategories(
		items: CategoryItem[],
		prefix = ""
	): FlatCategoryOption[] {
		const list: FlatCategoryOption[] = [];
		for (const item of items) {
			const path = prefix ? `${prefix} / ${item.name}` : item.name;
			list.push({ id: item.id, name: item.name, path });
			if (item.children && item.children.length > 0) {
				list.push(...flattenCategories(item.children, path));
			}
		}
		return list;
	}

	onMount(() => {
		loadCategories();
	});

	let selectedCategoryLabel = $derived(() => {
		if (selectedCategoryId === "uncategorized") {
			return m.upload_uncategorized();
		}
		const found = flatCategoryOptions.find((c) => c.id === selectedCategoryId);
		return found ? found.path : m.upload_uncategorized();
	});

	async function handleCreateNewCategory(name: string) {
		const trimmed = name.trim();
		if (!trimmed) return;
		try {
			isCreatingCategory = true;
			const created = await categoryService.createCategory({ name: trimmed });
			await loadCategories();
			selectedCategoryId = created.id;
			categorySearch = "";
			categoryOpen = false;
		} catch (err: any) {
			console.error("Failed to create category:", err.message);
		} finally {
			isCreatingCategory = false;
		}
	}

	function formatBytes(bytes: number) {
		if (bytes === 0) return "0 Bytes";
		const k = 1024;
		const sizes = ["Bytes", "KB", "MB", "GB"];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
	}

	function handleFiles(files: FileList | null) {
		if (!files || files.length === 0) return;
		for (let i = 0; i < files.length; i++) {
			const file = files[i];
			if (!file.type.startsWith("image/")) continue;
			const newItem: UploadQueueItem = {
				id: Math.random().toString(36).substring(2, 9),
				file,
				name: file.name,
				sizeStr: formatBytes(file.size),
				status: "Pending",
				progress: 0,
				thumbnailUrl: URL.createObjectURL(file)
			};
			queue.push(newItem);
		}
	}

	function removeQueueItem(id: string) {
		const item = queue.find((i) => i.id === id);
		if (item?.thumbnailUrl) {
			URL.revokeObjectURL(item.thumbnailUrl);
		}
		queue = queue.filter((i) => i.id !== id);
	}

	function clearQueue() {
		for (const item of queue) {
			if (item.thumbnailUrl) URL.revokeObjectURL(item.thumbnailUrl);
		}
		queue = [];
	}

	async function startUpload() {
		if (isUploading) return;
		isUploading = true;

		const targetCat =
			selectedCategoryId === "uncategorized" ? null : selectedCategoryId;

		for (const item of queue) {
			if (item.status === "Completed") continue;

			item.status = "Uploading";
			item.progress = 10;
			item.error = undefined;

			try {
				const uploaded = await imageService.uploadImage(
					item.file,
					targetCat,
					(percent) => {
						item.progress = Math.max(10, Math.min(95, percent));
					}
				);
				item.progress = 100;
				item.status = "Completed";
				item.uploadedImage = uploaded;
			} catch (err: any) {
				item.status = "Error";
				item.progress = 0;
				item.error = err.message || "Upload failed";
			}
		}

		isUploading = false;
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		isDragging = true;
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDragging = false;
		if (e.dataTransfer && e.dataTransfer.files) {
			handleFiles(e.dataTransfer.files);
		}
	}
</script>

<svelte:head>
	<title>{m.upload_title()} - Perceptra</title>
</svelte:head>

<div class="flex flex-1 flex-col p-4 md:p-6 lg:p-8 space-y-6">
	<!-- Page Header -->
	<header class="flex flex-col gap-1">
		<h1 class="text-2xl font-bold tracking-tight text-foreground">{m.upload_title()}</h1>
		<p class="text-sm text-muted-foreground">
			{m.upload_subtitle()}
		</p>
	</header>

	<!-- Top Grid: Drag & Drop Zone + Upload Options -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
		<!-- Drag & Drop Box -->
		<div class="lg:col-span-8">
			<Card.Root class="h-full border border-border/80 bg-card/60 backdrop-blur-xs shadow-xs">
				<Card.Content class="p-6 h-full flex flex-col justify-center">
					<!-- svelte-ignore a11y_click_events_have_key_events -->
					<!-- svelte-ignore a11y_no_static_element_interactions -->
					<div
						class="flex flex-col items-center justify-center p-8 sm:p-10 rounded-xl border-2 border-dashed transition-all duration-200 cursor-pointer text-center {isDragging
							? 'border-primary bg-primary/5 ring-4 ring-primary/10'
							: 'border-primary/30 hover:border-primary/60 bg-primary/[0.02]'}"
						ondragover={handleDragOver}
						ondragleave={handleDragLeave}
						ondrop={handleDrop}
						onclick={() => fileInputRef?.click()}
					>
						<input
							type="file"
							multiple
							accept="image/png,image/jpeg,image/webp,image/bmp"
							class="hidden"
							bind:this={fileInputRef}
							onchange={(e) => handleFiles((e.target as HTMLInputElement).files)}
						/>

						<div class="mb-4 rounded-full bg-primary/10 p-3.5 text-primary shadow-xs">
							<UploadCloudIcon class="size-7" />
						</div>

						<h3 class="text-base sm:text-lg font-semibold tracking-tight text-foreground">
							{m.upload_drag_title()}
						</h3>
						<p class="mt-1 text-xs sm:text-sm text-muted-foreground">
							{m.upload_drag_subtitle()}
						</p>

						<Button
							type="button"
							variant="outline"
							size="sm"
							class="mt-4 h-9 px-4 rounded-md font-semibold text-xs sm:text-sm shadow-xs"
							onclick={(e) => {
								e.stopPropagation();
								fileInputRef?.click();
							}}
						>
							{m.upload_select_files()}
						</Button>

						<p class="mt-4 text-[11px] sm:text-xs text-muted-foreground/80">
							{m.upload_supported_formats()}
						</p>
					</div>
				</Card.Content>
			</Card.Root>
		</div>

		<!-- Upload Options Card -->
		<div class="lg:col-span-4">
			<Card.Root class="h-full border border-border/80 bg-card/60 backdrop-blur-xs shadow-xs flex flex-col justify-between">
				<Card.Header class="pb-4">
					<Card.Title class="text-base font-semibold tracking-tight">{m.upload_options_title()}</Card.Title>
				</Card.Header>

				<Card.Content class="space-y-6 flex-1">
					<!-- Target Category Combobox -->
					<div class="space-y-2">
						<label for="category-combobox" class="text-xs sm:text-sm font-medium text-foreground">
							{m.upload_target_category()}
						</label>
						<Popover.Root bind:open={categoryOpen}>
							<Popover.Trigger id="category-combobox" class="w-full">
								{#snippet child({ props })}
									<Button
										{...props}
										variant="outline"
										role="combobox"
										aria-expanded={categoryOpen}
										class="w-full justify-between h-9 px-3 text-xs sm:text-sm font-normal bg-background/50 hover:bg-background/80"
									>
										<span class="truncate">{selectedCategoryLabel()}</span>
										<ChevronsUpDownIcon class="size-3.5 shrink-0 opacity-50" />
									</Button>
								{/snippet}
							</Popover.Trigger>
							<Popover.Content class="w-[--bits-popover-anchor-width] p-0" align="start">
								<Command.Root>
									<Command.Input
										placeholder={m.upload_category_placeholder()}
										bind:value={categorySearch}
										class="h-9 text-xs sm:text-sm"
									/>
									<Command.List class="max-h-56 overflow-y-auto">
										<Command.Empty class="py-2 px-3 text-xs text-muted-foreground">
											{#if categorySearch.trim()}
												<button
													type="button"
													class="flex w-full items-center gap-2 rounded-md p-2 text-left text-xs sm:text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
													onclick={() => handleCreateNewCategory(categorySearch)}
													disabled={isCreatingCategory}
												>
													{#if isCreatingCategory}
														<Loader2Icon class="size-3.5 animate-spin" />
													{:else}
														<PlusIcon class="size-3.5" />
													{/if}
													<span>{m.upload_create_category({ name: categorySearch.trim() })}</span>
												</button>
											{:else}
												<span>No category found.</span>
											{/if}
										</Command.Empty>

										<Command.Group>
											<!-- Uncategorized Default Option -->
											<Command.Item
												value="uncategorized"
												onSelect={() => {
													selectedCategoryId = "uncategorized";
													categoryOpen = false;
												}}
												class="text-xs sm:text-sm cursor-pointer justify-between py-1.5 px-2.5"
											>
												<span class="truncate italic text-muted-foreground">{m.upload_uncategorized()}</span>
												{#if selectedCategoryId === "uncategorized"}
													<CheckIcon class="size-3.5 shrink-0 text-primary" />
												{/if}
											</Command.Item>

											<!-- Dynamic Loaded Categories -->
											{#each flatCategoryOptions as cat (cat.id)}
												<Command.Item
													value={cat.path}
													onSelect={() => {
														selectedCategoryId = cat.id;
														categoryOpen = false;
													}}
													class="text-xs sm:text-sm cursor-pointer justify-between py-1.5 px-2.5"
												>
													<div class="flex items-center gap-1.5 truncate">
														<FolderIcon class="size-3.5 text-muted-foreground shrink-0" />
														<span class="truncate">{cat.path}</span>
													</div>
													{#if selectedCategoryId === cat.id}
														<CheckIcon class="size-3.5 shrink-0 text-primary" />
													{/if}
												</Command.Item>
											{/each}
										</Command.Group>

										{#if categorySearch.trim() && !flatCategoryOptions.some((c) => c.name.toLowerCase() === categorySearch.trim().toLowerCase())}
											<div class="border-t border-border/60 p-1">
												<button
													type="button"
													class="flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-xs sm:text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
													onclick={() => handleCreateNewCategory(categorySearch)}
													disabled={isCreatingCategory}
												>
													{#if isCreatingCategory}
														<Loader2Icon class="size-3.5 animate-spin" />
													{:else}
														<PlusIcon class="size-3.5" />
													{/if}
													<span>{m.upload_create_category({ name: categorySearch.trim() })}</span>
												</button>
											</div>
										{/if}
									</Command.List>
								</Command.Root>
							</Popover.Content>
						</Popover.Root>
					</div>

					<!-- Processing Switch -->
					<div class="space-y-2">
						<div class="text-xs sm:text-sm font-medium text-foreground">{m.upload_process_after()}</div>
						<div class="flex items-start gap-3 rounded-lg border border-border/70 p-3 bg-muted/20">
							<Switch
								id="process-toggle"
								bind:checked={processAfterUpload}
								class="mt-0.5"
							/>
							<label
								for="process-toggle"
								class="text-xs sm:text-sm text-muted-foreground leading-snug cursor-pointer select-none"
							>
								{m.upload_process_desc()}
							</label>
						</div>
					</div>
				</Card.Content>
			</Card.Root>
		</div>
	</div>

	<!-- Upload Queue Section -->
	<Card.Root class="border border-border/80 bg-card/60 backdrop-blur-xs shadow-xs">
		<Card.Header class="flex flex-row items-center justify-between pb-3 px-6 pt-5">
			<div class="flex items-center gap-2">
				<Card.Title class="text-base font-semibold tracking-tight">{m.upload_queue_title()}</Card.Title>
				<Badge variant="secondary" class="font-normal text-xs px-2 py-0.5">
					{queue.length} {queue.length === 1 ? 'file' : 'files'}
				</Badge>
			</div>

			<div class="flex items-center gap-2">
				<Button
					variant="outline"
					size="sm"
					class="h-8 text-xs font-semibold"
					onclick={clearQueue}
					disabled={queue.length === 0 || isUploading}
				>
					{m.upload_clear_queue()}
				</Button>
				<Button
					size="sm"
					class="h-8 gap-1.5 text-xs font-semibold shadow-xs"
					onclick={startUpload}
					disabled={queue.length === 0 || isUploading || queue.every(i => i.status === 'Completed')}
				>
					{#if isUploading}
						<Loader2Icon class="size-3.5 animate-spin mr-1" />
						<span>{m.upload_uploading()}</span>
					{:else}
						<PlayIcon data-icon="inline-start" class="size-3.5 fill-current" />
						<span>{m.upload_start_upload()}</span>
					{/if}
				</Button>
			</div>
		</Card.Header>

		<Card.Content class="p-0">
			{#if queue.length === 0}
				<div class="flex flex-col items-center justify-center p-12 text-center text-muted-foreground">
					<ImageIcon class="size-10 mb-2 stroke-1 opacity-50" />
					<p class="text-sm font-medium">{m.upload_queue_empty()}</p>
					<p class="text-xs mt-0.5">{m.upload_queue_empty_desc()}</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<Table.Root>
						<Table.Header class="bg-muted/30">
							<Table.Row class="hover:bg-transparent">
								<Table.Head class="w-[320px] font-semibold text-xs uppercase tracking-wider text-muted-foreground">
									{m.upload_col_file()}
								</Table.Head>
								<Table.Head class="w-[120px] font-semibold text-xs uppercase tracking-wider text-muted-foreground">
									{m.upload_col_size()}
								</Table.Head>
								<Table.Head class="w-[140px] font-semibold text-xs uppercase tracking-wider text-muted-foreground">
									{m.upload_col_status()}
								</Table.Head>
								<Table.Head class="w-[300px] font-semibold text-xs uppercase tracking-wider text-muted-foreground">
									{m.upload_col_progress()}
								</Table.Head>
								<Table.Head class="w-[60px] text-right font-semibold text-xs uppercase tracking-wider text-muted-foreground">
								</Table.Head>
							</Table.Row>
						</Table.Header>

						<Table.Body>
							{#each queue as item (item.id)}
								<Table.Row class="transition-colors hover:bg-muted/30">
									<!-- Thumbnail & File Name -->
									<Table.Cell class="py-2.5 font-medium">
										<div class="flex items-center gap-3">
											<div class="size-10 shrink-0 overflow-hidden rounded-md border border-border/70 bg-muted/40 shadow-2xs">
												{#if item.thumbnailUrl}
													<img
														src={item.thumbnailUrl}
														alt={item.name}
														class="size-full object-cover"
													/>
												{:else}
													<div class="flex size-full items-center justify-center text-muted-foreground">
														<ImageIcon class="size-4" />
													</div>
												{/if}
											</div>
											<div class="flex flex-col min-w-0 max-w-[240px]">
												<span class="truncate text-xs sm:text-sm font-medium text-foreground" title={item.name}>
													{item.name}
												</span>
												{#if item.error}
													<span class="text-[11px] text-destructive truncate flex items-center gap-1" title={item.error}>
														<AlertCircleIcon class="size-3 shrink-0" />
														{item.error}
													</span>
												{/if}
											</div>
										</div>
									</Table.Cell>

									<!-- Size -->
									<Table.Cell class="text-xs sm:text-sm text-muted-foreground">
										{item.sizeStr}
									</Table.Cell>

									<!-- Status Badge -->
									<Table.Cell>
										{#if item.status === "Uploading"}
											<Badge variant="secondary" class="font-medium text-xs bg-primary/10 text-primary border-primary/20 gap-1">
												<Loader2Icon class="size-3 animate-spin" />
												{m.upload_status_uploading()}
											</Badge>
										{:else if item.status === "Completed"}
											<Badge variant="secondary" class="font-medium text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20">
												{m.upload_status_completed()}
											</Badge>
										{:else if item.status === "Error"}
											<Badge variant="destructive" class="font-medium text-xs">
												{m.upload_status_error()}
											</Badge>
										{:else}
											<Badge variant="outline" class="font-medium text-xs text-muted-foreground">
												{m.upload_status_pending()}
											</Badge>
										{/if}
									</Table.Cell>

									<!-- Progress Bar & Percentage -->
									<Table.Cell class="py-2.5">
										<div class="flex items-center gap-3">
											<div class="w-full max-w-[200px]">
												<Progress value={item.progress} class="h-1.5" />
											</div>
											<span class="text-xs tabular-nums text-muted-foreground font-mono min-w-[32px]">
												{item.progress}%
											</span>
										</div>
									</Table.Cell>

									<!-- Remove Action -->
									<Table.Cell class="text-right py-2.5">
										<Button
											variant="ghost"
											size="icon"
											class="size-7 rounded-md text-muted-foreground hover:text-foreground"
											onclick={() => removeQueueItem(item.id)}
											disabled={item.status === "Uploading"}
											title="Remove file"
										>
											<XIcon class="size-3.5" />
											<span class="sr-only">Remove</span>
										</Button>
									</Table.Cell>
								</Table.Row>
							{/each}
						</Table.Body>
					</Table.Root>
				</div>
			{/if}
		</Card.Content>
	</Card.Root>
</div>
