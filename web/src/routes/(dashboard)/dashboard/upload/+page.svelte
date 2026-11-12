<script lang="ts">
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Popover from "#lib/components/ui/popover/index.js";
	import * as Command from "#lib/components/ui/command/index.js";
	import { Switch } from "#lib/components/ui/switch/index.js";
	import { Progress } from "#lib/components/ui/progress/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import * as Table from "#lib/components/ui/table/index.js";
	import UploadCloudIcon from "@lucide/svelte/icons/upload-cloud";
	import PlayIcon from "@lucide/svelte/icons/play";
	import XIcon from "@lucide/svelte/icons/x";
	import Trash2Icon from "@lucide/svelte/icons/trash-2";
	import ImageIcon from "@lucide/svelte/icons/image";
	import CheckCircle2Icon from "@lucide/svelte/icons/check-circle-2";
	import CheckIcon from "@lucide/svelte/icons/check";
	import ChevronsUpDownIcon from "@lucide/svelte/icons/chevrons-up-down";
	import PlusIcon from "@lucide/svelte/icons/plus";

	interface UploadItem {
		id: string;
		name: string;
		sizeStr: string;
		status: "Pending" | "Uploading" | "Completed" | "Error";
		progress: number;
		thumbnailUrl?: string;
	}

	let selectedCategory = $state("Nature");
	let selectedSubCategory = $state("Landscapes");
	let categoryOpen = $state(false);
	let subCategoryOpen = $state(false);
	let categorySearch = $state("");
	let subCategorySearch = $state("");
	let processAfterUpload = $state(true);
	let isDragging = $state(false);
	let fileInputRef = $state<HTMLInputElement | null>(null);

	let categoryMap = $state<Record<string, string[]>>({
		Nature: ["Landscapes", "Mountains", "Lakes & Rivers", "Forests", "Sunsets"],
		Architecture: ["Buildings", "Bridges", "Monuments", "Interiors", "Urban"],
		Animals: ["Wildlife", "Mammals", "Birds", "Marine Life", "Insects"],
		Vehicles: ["Cars", "Aircraft", "Watercraft", "Trains"],
		Texture: ["Materials", "Patterns", "Fabrics", "Surfaces"],
		Objects: ["Tools", "Art & Craft", "Technology", "General"]
	});

	let categories = $derived(Object.keys(categoryMap));
	let currentSubCategories = $derived(categoryMap[selectedCategory] || []);

	function createAndSelectCategory(name: string) {
		const trimmed = name.trim();
		if (!trimmed) return;
		if (!categoryMap[trimmed]) {
			categoryMap = { ...categoryMap, [trimmed]: ["General"] };
		}
		selectedCategory = trimmed;
		selectedSubCategory = categoryMap[trimmed][0] || "General";
		categorySearch = "";
		categoryOpen = false;
	}

	function createAndSelectSubCategory(name: string) {
		const trimmed = name.trim();
		if (!trimmed) return;
		const existing = categoryMap[selectedCategory] || [];
		if (!existing.includes(trimmed)) {
			categoryMap = {
				...categoryMap,
				[selectedCategory]: [...existing, trimmed]
			};
		}
		selectedSubCategory = trimmed;
		subCategorySearch = "";
		subCategoryOpen = false;
	}

	let queue = $state<UploadItem[]>([
		{
			id: "1",
			name: "ghim_nature_alpine_lake_01.jpg",
			sizeStr: "2.4 MB",
			status: "Uploading",
			progress: 55,
			thumbnailUrl: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=100&auto=format&fit=crop&q=60"
		},
		{
			id: "2",
			name: "forest_path_02.jpg",
			sizeStr: "3.1 MB",
			status: "Uploading",
			progress: 28,
			thumbnailUrl: "https://images.unsplash.com/photo-1448375240586-882707db888b?w=100&auto=format&fit=crop&q=60"
		},
		{
			id: "3",
			name: "mountain_snow_03.jpg",
			sizeStr: "1.9 MB",
			status: "Pending",
			progress: 0,
			thumbnailUrl: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=100&auto=format&fit=crop&q=60"
		},
		{
			id: "4",
			name: "lake_sunset_04.png",
			sizeStr: "2.8 MB",
			status: "Pending",
			progress: 0,
			thumbnailUrl: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=100&auto=format&fit=crop&q=60"
		},
		{
			id: "5",
			name: "waterfall_05.jpg",
			sizeStr: "3.6 MB",
			status: "Pending",
			progress: 0,
			thumbnailUrl: "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?w=100&auto=format&fit=crop&q=60"
		}
	]);

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
			const newItem: UploadItem = {
				id: Math.random().toString(36).substring(2, 9),
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
		queue = queue.filter((item) => item.id !== id);
	}

	function clearQueue() {
		queue = [];
	}

	let uploadInterval: any = null;
	function startUpload() {
		if (uploadInterval) return;
		uploadInterval = setInterval(() => {
			let allDone = true;
			queue = queue.map((item) => {
				if (item.status === "Pending") {
					allDone = false;
					return { ...item, status: "Uploading", progress: 10 };
				} else if (item.status === "Uploading") {
					const nextProgress = Math.min(100, item.progress + Math.floor(Math.random() * 18 + 5));
					if (nextProgress < 100) {
						allDone = false;
						return { ...item, progress: nextProgress };
					} else {
						return { ...item, progress: 100, status: "Completed" };
					}
				}
				return item;
			});

			if (allDone) {
				clearInterval(uploadInterval);
				uploadInterval = null;
			}
		}, 600);
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
	<title>Upload Images - Perceptra</title>
</svelte:head>

<div class="flex flex-1 flex-col p-4 md:p-6 lg:p-8 space-y-6">
	<!-- Page Header -->
	<header class="flex flex-col gap-1">
		<h1 class="text-2xl font-bold tracking-tight text-foreground">Upload Images</h1>
		<p class="text-sm text-muted-foreground">
			Add images to the system for indexing, descriptor extraction, and similarity retrieval.
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
							Drag and drop images here
						</h3>
						<p class="mt-1 text-xs sm:text-sm text-muted-foreground">
							or select files from your device
						</p>

						<Button
							type="button"
							variant="outline"
							size="sm"
							class="mt-4 h-9 px-4 rounded-md font-medium text-xs sm:text-sm shadow-xs"
							onclick={(e) => {
								e.stopPropagation();
								fileInputRef?.click();
							}}
						>
							Select Files
						</Button>

						<p class="mt-4 text-[11px] sm:text-xs text-muted-foreground/80">
							Supported formats: JPG, JPEG, PNG, BMP, WEBP &nbsp;•&nbsp; Max size: 20 MB per file
						</p>
					</div>
				</Card.Content>
			</Card.Root>
		</div>

		<!-- Upload Options Card -->
		<div class="lg:col-span-4">
			<Card.Root class="h-full border border-border/80 bg-card/60 backdrop-blur-xs shadow-xs flex flex-col justify-between">
				<Card.Header class="pb-4">
					<Card.Title class="text-base font-semibold tracking-tight">Upload Options</Card.Title>
				</Card.Header>

				<Card.Content class="space-y-6 flex-1">
					<!-- Category Combobox / Creatable Select -->
					<div class="space-y-2">
						<label for="category-combobox" class="text-xs sm:text-sm font-medium text-foreground">
							Category
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
										<span class="truncate">{selectedCategory}</span>
										<ChevronsUpDownIcon class="size-3.5 shrink-0 opacity-50" />
									</Button>
								{/snippet}
							</Popover.Trigger>
							<Popover.Content class="w-[--bits-popover-anchor-width] p-0" align="start">
								<Command.Root>
									<Command.Input
										placeholder="Search or create category..."
										bind:value={categorySearch}
										class="h-9 text-xs sm:text-sm"
									/>
									<Command.List class="max-h-56 overflow-y-auto">
										<Command.Empty class="py-2 px-3 text-xs text-muted-foreground">
											{#if categorySearch.trim()}
												<button
													type="button"
													class="flex w-full items-center gap-2 rounded-md p-2 text-left text-xs sm:text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
													onclick={() => createAndSelectCategory(categorySearch)}
												>
													<PlusIcon class="size-3.5" />
													<span>Create category "<strong>{categorySearch.trim()}</strong>"</span>
												</button>
											{:else}
												No category found.
											{/if}
										</Command.Empty>
										<Command.Group>
											{#each categories as cat (cat)}
												<Command.Item
													value={cat}
													onSelect={() => {
														selectedCategory = cat;
														selectedSubCategory = categoryMap[cat]?.[0] || "General";
														categoryOpen = false;
													}}
													class="text-xs sm:text-sm cursor-pointer justify-between py-1.5 px-2.5"
												>
													<span class="truncate">{cat}</span>
													{#if selectedCategory === cat}
														<CheckIcon class="size-3.5 shrink-0 text-primary" />
													{/if}
												</Command.Item>
											{/each}
										</Command.Group>

										{#if categorySearch.trim() && !categories.some(c => c.toLowerCase() === categorySearch.trim().toLowerCase())}
											<div class="border-t border-border/60 p-1">
												<button
													type="button"
													class="flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-xs sm:text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
													onclick={() => createAndSelectCategory(categorySearch)}
												>
													<PlusIcon class="size-3.5" />
													<span>Create "<strong>{categorySearch.trim()}</strong>"</span>
												</button>
											</div>
										{/if}
									</Command.List>
								</Command.Root>
							</Popover.Content>
						</Popover.Root>
					</div>

					<!-- Sub-Category Combobox / Creatable Select -->
					<div class="space-y-2">
						<label for="subcategory-combobox" class="text-xs sm:text-sm font-medium text-foreground">
							Sub-Category
						</label>
						<Popover.Root bind:open={subCategoryOpen}>
							<Popover.Trigger id="subcategory-combobox" class="w-full">
								{#snippet child({ props })}
									<Button
										{...props}
										variant="outline"
										role="combobox"
										aria-expanded={subCategoryOpen}
										class="w-full justify-between h-9 px-3 text-xs sm:text-sm font-normal bg-background/50 hover:bg-background/80"
									>
										<span class="truncate">{selectedSubCategory}</span>
										<ChevronsUpDownIcon class="size-3.5 shrink-0 opacity-50" />
									</Button>
								{/snippet}
							</Popover.Trigger>
							<Popover.Content class="w-[--bits-popover-anchor-width] p-0" align="start">
								<Command.Root>
									<Command.Input
										placeholder="Search or create sub-category..."
										bind:value={subCategorySearch}
										class="h-9 text-xs sm:text-sm"
									/>
									<Command.List class="max-h-56 overflow-y-auto">
										<Command.Empty class="py-2 px-3 text-xs text-muted-foreground">
											{#if subCategorySearch.trim()}
												<button
													type="button"
													class="flex w-full items-center gap-2 rounded-md p-2 text-left text-xs sm:text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
													onclick={() => createAndSelectSubCategory(subCategorySearch)}
												>
													<PlusIcon class="size-3.5" />
													<span>Create sub-category "<strong>{subCategorySearch.trim()}</strong>"</span>
												</button>
											{:else}
												No sub-category found.
											{/if}
										</Command.Empty>
										<Command.Group>
											{#each currentSubCategories as subCat (subCat)}
												<Command.Item
													value={subCat}
													onSelect={() => {
														selectedSubCategory = subCat;
														subCategoryOpen = false;
													}}
													class="text-xs sm:text-sm cursor-pointer justify-between py-1.5 px-2.5"
												>
													<span class="truncate">{subCat}</span>
													{#if selectedSubCategory === subCat}
														<CheckIcon class="size-3.5 shrink-0 text-primary" />
													{/if}
												</Command.Item>
											{/each}
										</Command.Group>

										{#if subCategorySearch.trim() && !currentSubCategories.some(c => c.toLowerCase() === subCategorySearch.trim().toLowerCase())}
											<div class="border-t border-border/60 p-1">
												<button
													type="button"
													class="flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-xs sm:text-sm font-medium text-primary hover:bg-primary/10 transition-colors"
													onclick={() => createAndSelectSubCategory(subCategorySearch)}
												>
													<PlusIcon class="size-3.5" />
													<span>Create "<strong>{subCategorySearch.trim()}</strong>"</span>
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
						<div class="text-xs sm:text-sm font-medium text-foreground">Process after upload</div>
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
								Extract visual descriptors (Color + GLCM + LBP)
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
				<Card.Title class="text-base font-semibold tracking-tight">Upload Queue</Card.Title>
				<Badge variant="secondary" class="font-normal text-xs px-2 py-0.5">
					{queue.length} {queue.length === 1 ? 'file' : 'files'}
				</Badge>
			</div>

			<div class="flex items-center gap-2">
				<Button
					variant="outline"
					size="sm"
					class="h-8 text-xs font-medium"
					onclick={clearQueue}
					disabled={queue.length === 0}
				>
					Clear Queue
				</Button>
				<Button
					size="sm"
					class="h-8 gap-1.5 text-xs font-medium shadow-xs"
					onclick={startUpload}
					disabled={queue.length === 0 || queue.every(i => i.status === 'Completed')}
				>
					<PlayIcon data-icon="inline-start" class="size-3.5 fill-current" />
					Start Upload
				</Button>
			</div>
		</Card.Header>

		<Card.Content class="p-0">
			{#if queue.length === 0}
				<div class="flex flex-col items-center justify-center p-12 text-center text-muted-foreground">
					<ImageIcon class="size-10 mb-2 stroke-1 opacity-50" />
					<p class="text-sm font-medium">Your queue is empty</p>
					<p class="text-xs mt-0.5">Drag files or click browse above to add images.</p>
				</div>
			{:else}
				<div class="overflow-x-auto">
					<Table.Root>
						<Table.Header class="bg-muted/30">
							<Table.Row class="hover:bg-transparent">
								<Table.Head class="w-[320px] font-semibold text-xs uppercase tracking-wider text-muted-foreground">
									File
								</Table.Head>
								<Table.Head class="w-[120px] font-semibold text-xs uppercase tracking-wider text-muted-foreground">
									Size
								</Table.Head>
								<Table.Head class="w-[140px] font-semibold text-xs uppercase tracking-wider text-muted-foreground">
									Status
								</Table.Head>
								<Table.Head class="w-[300px] font-semibold text-xs uppercase tracking-wider text-muted-foreground">
									Progress
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
											<span class="truncate max-w-[240px] text-xs sm:text-sm font-medium text-foreground">
												{item.name}
											</span>
										</div>
									</Table.Cell>

									<!-- Size -->
									<Table.Cell class="text-xs sm:text-sm text-muted-foreground">
										{item.sizeStr}
									</Table.Cell>

									<!-- Status Badge -->
									<Table.Cell>
										{#if item.status === "Uploading"}
											<Badge variant="secondary" class="font-medium text-xs bg-primary/10 text-primary border-primary/20">
												Uploading
											</Badge>
										{:else if item.status === "Completed"}
											<Badge variant="secondary" class="font-medium text-xs bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20">
												Completed
											</Badge>
										{:else}
											<Badge variant="outline" class="font-medium text-xs text-muted-foreground">
												Pending
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
