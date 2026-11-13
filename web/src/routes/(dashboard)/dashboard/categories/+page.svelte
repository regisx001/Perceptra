<script lang="ts">
	import { onMount } from "svelte";
	import * as m from "#lib/paraglide/messages.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Input } from "#lib/components/ui/input/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import * as Dialog from "#lib/components/ui/dialog/index.js";
	import * as AlertDialog from "#lib/components/ui/alert-dialog/index.js";
	import * as Field from "#lib/components/ui/field/index.js";
	import * as FileTree from "#lib/components/ui/file-tree/index.js";
	import * as DropdownMenu from "#lib/components/ui/dropdown-menu/index.js";
	import { categoryService, type CategoryItem } from "#lib/categories.js";
	import FolderIcon from "@lucide/svelte/icons/folder";
	import FolderTreeIcon from "@lucide/svelte/icons/folder-tree";
	import SearchIcon from "@lucide/svelte/icons/search";
	import PlusIcon from "@lucide/svelte/icons/plus";
	import Edit3Icon from "@lucide/svelte/icons/edit-3";
	import ArrowLeftRightIcon from "@lucide/svelte/icons/arrow-left-right";
	import Trash2Icon from "@lucide/svelte/icons/trash-2";
	import ImageIcon from "@lucide/svelte/icons/image";
	import ImagesIcon from "@lucide/svelte/icons/images";
	import HelpCircleIcon from "@lucide/svelte/icons/help-circle";
	import FoldVerticalIcon from "@lucide/svelte/icons/fold-vertical";
	import MoveIcon from "@lucide/svelte/icons/move";
	import BanIcon from "@lucide/svelte/icons/ban";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import TrendingUpIcon from "@lucide/svelte/icons/trending-up";
	import MoreHorizontalIcon from "@lucide/svelte/icons/more-horizontal";

	interface CategoryNode {
		id: string;
		name: string;
		count: number;
		children?: CategoryNode[];
		parentId?: string | null;
	}

	interface AssignedImage {
		id: string;
		filename: string;
		url: string;
		resolution?: string;
	}

	// Dynamic API category data with initial fallback
	let categoryTree = $state<CategoryNode[]>([
		{
			id: "nature",
			name: "Nature",
			count: 4210,
			children: [
				{
					id: "nature-landscapes",
					name: "Landscapes",
					count: 2410,
					parentId: "nature",
					children: [
						{
							id: "nature-landscapes-mountains",
							name: "Mountains",
							count: 850,
							parentId: "nature-landscapes"
						},
						{
							id: "nature-landscapes-lakes",
							name: "Lakes",
							count: 620,
							parentId: "nature-landscapes"
						},
						{
							id: "nature-landscapes-forests",
							name: "Forests",
							count: 940,
							parentId: "nature-landscapes"
						}
					]
				},
				{
					id: "nature-wildlife",
					name: "Wildlife",
					count: 1800,
					parentId: "nature",
					children: [
						{
							id: "nature-wildlife-mammals",
							name: "Mammals",
							count: 980,
							parentId: "nature-wildlife"
						},
						{
							id: "nature-wildlife-birds",
							name: "Birds",
							count: 820,
							parentId: "nature-wildlife"
						}
					]
				}
			]
		},
		{
			id: "architecture",
			name: "Architecture",
			count: 2340,
			children: [
				{
					id: "architecture-buildings",
					name: "Buildings",
					count: 1420,
					parentId: "architecture"
				},
				{
					id: "architecture-bridges",
					name: "Bridges",
					count: 920,
					parentId: "architecture"
				}
			]
		},
		{
			id: "historical",
			name: "Historical",
			count: 1871,
			children: [
				{
					id: "historical-monuments",
					name: "Monuments",
					count: 1100,
					parentId: "historical"
				},
				{
					id: "historical-artifacts",
					name: "Artifacts",
					count: 771,
					parentId: "historical"
				}
			]
		}
	]);

	let isLoading = $state(false);
	let errorMessage = $state<string | null>(null);

	// Convert API categories into CategoryNodes
	function mapApiItemToNode(item: CategoryItem): CategoryNode {
		return {
			id: item.id,
			name: item.name,
			count: item.image_count ?? 0,
			parentId: item.parent_id,
			children: item.children ? item.children.map(mapApiItemToNode) : []
		};
	}

	async function loadCategories() {
		try {
			isLoading = true;
			errorMessage = null;
			const data = await categoryService.getCategories({ tree: true, include_counts: true });
			if (data && data.length > 0) {
				categoryTree = data.map(mapApiItemToNode);
				if (!selectedCategoryId || selectedCategoryId === "nature-landscapes-mountains") {
					selectedCategoryId = categoryTree[0]?.id ?? "uncategorized";
				}
			}
		} catch (err: any) {
			console.warn("Categories API unavailable, falling back to local dataset:", err.message);
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		loadCategories();
	});

	// Flat lookup helper for categories
	function getAllCategories(nodes: CategoryNode[]): { id: string; name: string; path: string }[] {
		const result: { id: string; name: string; path: string }[] = [];
		function walk(list: CategoryNode[], parentPath: string) {
			for (const node of list) {
				const currentPath = parentPath ? `${parentPath} > ${node.name}` : node.name;
				result.push({ id: node.id, name: node.name, path: currentPath });
				if (node.children) {
					walk(node.children, currentPath);
				}
			}
		}
		walk(nodes, "");
		return result;
	}

	// State for search and navigation
	let categorySearch = $state("");
	let selectedCategoryId = $state<string>("nature-landscapes-mountains");
	let expandedNodes = $state<Record<string, boolean>>({
		nature: true,
		"nature-landscapes": true,
		architecture: false,
		historical: false
	});

	// Dialogs state
	let isNewCategoryDialogOpen = $state(false);
	let isEditCategoryDialogOpen = $state(false);
	let isMoveDialogOpen = $state(false);
	let isSubCategoryDialogOpen = $state(false);
	let isDeleteDialogOpen = $state(false);
	let categoryToDelete = $state<CategoryNode | null>(null);

	let newCategoryName = $state("");
	let newCategoryParentId = $state<string>("root");
	let editingCategoryName = $state("");
	let targetParentId = $state<string>("root");
	let isSubmitting = $state(false);

	// Unassigned and image counts
	let uncategorizedCount = $state(1579);
	let imageSearchQuery = $state("");

	// Mock placeholder images for the selected folder
	let placeholderImages = $state<AssignedImage[]>([
		{
			id: "img-1",
			filename: "ghim_nature_peak.jpg",
			url: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&auto=format&fit=crop&q=80"
		},
		{
			id: "img-2",
			filename: "ghim_nature_peak.jpg",
			url: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=400&auto=format&fit=crop&q=80"
		},
		{
			id: "img-3",
			filename: "ghim_nature_peak.jpg",
			url: "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=400&auto=format&fit=crop&q=80"
		},
		{
			id: "img-4",
			filename: "ghim_snow_cap.jpg",
			url: "https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?w=400&auto=format&fit=crop&q=80"
		},
		{
			id: "img-5",
			filename: "ghim_snow_cap.jpg",
			url: "https://images.unsplash.com/photo-1542332213-31f87348057f?w=400&auto=format&fit=crop&q=80"
		},
		{
			id: "img-6",
			filename: "ghim_mountain_fog.jpg",
			url: "https://images.unsplash.com/photo-1483728642387-6c3bdd6c93e5?w=400&auto=format&fit=crop&q=80"
		},
		{
			id: "img-7",
			filename: "ghim_summit_dawn.jpg",
			url: "https://images.unsplash.com/photo-1517824806704-9040b037703b?w=400&auto=format&fit=crop&q=80"
		},
		{
			id: "img-8",
			filename: "ghim_ridge_trail.jpg",
			url: "https://images.unsplash.com/photo-1454447299186-c3445e99e7bb?w=400&auto=format&fit=crop&q=80"
		}
	]);

	let filteredImages = $derived(
		imageSearchQuery.trim() === ""
			? placeholderImages
			: placeholderImages.filter((img) =>
					img.filename.toLowerCase().includes(imageSearchQuery.toLowerCase())
				)
	);

	// Find node details and ancestry path
	function findNodeAndPath(
		id: string,
		nodes: CategoryNode[],
		path: CategoryNode[] = []
	): { node: CategoryNode; path: CategoryNode[] } | null {
		for (const n of nodes) {
			if (n.id === id) return { node: n, path: [...path, n] };
			if (n.children) {
				const res = findNodeAndPath(id, n.children, [...path, n]);
				if (res) return res;
			}
		}
		return null;
	}

	let currentSelected = $derived(findNodeAndPath(selectedCategoryId, categoryTree));
	let breadcrumbs = $derived(currentSelected ? currentSelected.path : []);
	let activeNode = $derived(currentSelected ? currentSelected.node : null);

	// Real subcategories of the active category
	let currentSubcategories = $derived(
		activeNode && activeNode.children ? activeNode.children : []
	);

	function collapseAll() {
		const newMap: Record<string, boolean> = {};
		for (const key of Object.keys(expandedNodes)) {
			newMap[key] = false;
		}
		expandedNodes = newMap;
	}

	function expandAll() {
		const newMap: Record<string, boolean> = {};
		function walk(nodes: CategoryNode[]) {
			for (const node of nodes) {
				if (node.children && node.children.length > 0) {
					newMap[node.id] = true;
					walk(node.children);
				}
			}
		}
		walk(categoryTree);
		expandedNodes = newMap;
	}

	function selectCategory(id: string) {
		selectedCategoryId = id;
	}

	// KPI calculations
	let totalFolders = $derived(getAllCategories(categoryTree).length);
	let rootFoldersCount = $derived(categoryTree.length);
	let categorizedImagesCount = 8421;
	let totalImagesCount = $derived(categorizedImagesCount + uncategorizedCount);
	let categorizedPercentage = $derived(Math.round((categorizedImagesCount / totalImagesCount) * 100));
	let uncategorizedPercentage = $derived(100 - categorizedPercentage);

	// Add Category logic with API consumption
	async function handleCreateCategory() {
		if (!newCategoryName.trim()) return;
		try {
			isSubmitting = true;
			const parent = newCategoryParentId === "root" ? null : newCategoryParentId;
			const created = await categoryService.createCategory({
				name: newCategoryName.trim(),
				parent_id: parent
			});

			const newNode: CategoryNode = {
				id: created.id,
				name: created.name,
				count: 0,
				children: [],
				parentId: created.parent_id
			};

			if (!parent) {
				categoryTree.push(newNode);
			} else {
				const target = findNodeAndPath(parent, categoryTree);
				if (target) {
					target.node.children = target.node.children || [];
					target.node.children.push(newNode);
					expandedNodes[target.node.id] = true;
				}
			}
			selectedCategoryId = created.id;
		} catch (err: any) {
			// Fallback local mutation
			const fallbackId = newCategoryName.toLowerCase().replace(/[^a-z0-9]+/g, "-") + "-" + Date.now().toString().slice(-4);
			const newNode: CategoryNode = {
				id: fallbackId,
				name: newCategoryName.trim(),
				count: 0,
				children: [],
				parentId: newCategoryParentId === "root" ? null : newCategoryParentId
			};

			if (newCategoryParentId === "root") {
				categoryTree.push(newNode);
			} else {
				const target = findNodeAndPath(newCategoryParentId, categoryTree);
				if (target) {
					target.node.children = target.node.children || [];
					target.node.children.push(newNode);
					expandedNodes[target.node.id] = true;
				}
			}
			selectedCategoryId = fallbackId;
		} finally {
			isSubmitting = false;
			newCategoryName = "";
			newCategoryParentId = "root";
			isNewCategoryDialogOpen = false;
			isSubCategoryDialogOpen = false;
		}
	}

	// Edit category name with API consumption
	function openEditDialog(node: CategoryNode, e?: MouseEvent) {
		e?.stopPropagation();
		editingCategoryName = node.name;
		isEditCategoryDialogOpen = true;
	}

	async function handleSaveEdit() {
		if (!editingCategoryName.trim() || !activeNode) return;
		try {
			isSubmitting = true;
			await categoryService.updateCategory(activeNode.id, {
				name: editingCategoryName.trim()
			});
			activeNode.name = editingCategoryName.trim();
		} catch (err: any) {
			activeNode.name = editingCategoryName.trim();
		} finally {
			isSubmitting = false;
			isEditCategoryDialogOpen = false;
		}
	}

	// Move category parent with API consumption
	async function handleMoveCategory() {
		if (!activeNode) return;
		try {
			isSubmitting = true;
			const newParent = targetParentId === "root" ? null : targetParentId;
			await categoryService.updateCategory(activeNode.id, {
				parent_id: newParent
			});
			await loadCategories();
		} catch (err: any) {
			console.warn("Failed to move category via API:", err.message);
		} finally {
			isSubmitting = false;
			isMoveDialogOpen = false;
		}
	}

	// Trigger shadcn AlertDialog for deleting category
	function promptDeleteCategory(node: CategoryNode, e?: MouseEvent) {
		e?.stopPropagation();
		categoryToDelete = node;
		isDeleteDialogOpen = true;
	}

	async function confirmDeleteCategory() {
		if (!categoryToDelete) return;
		const id = categoryToDelete.id;

		try {
			isSubmitting = true;
			await categoryService.deleteCategory(id);
		} catch (err: any) {
			console.warn("Delete category API warning:", err.message);
		} finally {
			isSubmitting = false;
			isDeleteDialogOpen = false;
		}

		function removeNode(nodes: CategoryNode[]): boolean {
			const index = nodes.findIndex((n) => n.id === id);
			if (index !== -1) {
				nodes.splice(index, 1);
				return true;
			}
			for (const n of nodes) {
				if (n.children && removeNode(n.children)) return true;
			}
			return false;
		}

		removeNode(categoryTree);
		if (selectedCategoryId === id && categoryTree[0]) {
			selectedCategoryId = categoryTree[0].id;
		}
		categoryToDelete = null;
	}

	function openAddSubcategoryDialog(parentId: string, e?: MouseEvent) {
		e?.stopPropagation();
		newCategoryParentId = parentId;
		newCategoryName = "";
		isSubCategoryDialogOpen = true;
	}
</script>

<svelte:head>
	<title>Category Management - Perceptra</title>
</svelte:head>

<!-- Recursive Tree Snippet using FileTree components -->
{#snippet renderTreeNode(node: CategoryNode)}
	{@const hasChildren = node.children && node.children.length > 0}

	{#snippet nodeActions()}
		<DropdownMenu.Root>
			<DropdownMenu.Trigger>
				{#snippet child({ props })}
					<Button
						{...props}
						variant="ghost"
						size="icon"
						class="size-6 p-0 text-muted-foreground hover:text-foreground opacity-70 group-hover:opacity-100"
						onclick={(e) => e.stopPropagation()}
						title="Category actions"
					>
						<MoreHorizontalIcon class="size-3.5" />
						<span class="sr-only">Actions</span>
					</Button>
				{/snippet}
			</DropdownMenu.Trigger>
			<DropdownMenu.Content align="end" class="w-40">
				<DropdownMenu.Item
					class="gap-2 text-xs"
					onclick={(e: MouseEvent) => openAddSubcategoryDialog(node.id, e)}
				>
					<PlusIcon class="size-3.5" />
					<span>{m.categories_menu_add_sub()}</span>
				</DropdownMenu.Item>
				<DropdownMenu.Item
					class="gap-2 text-xs"
					onclick={(e: MouseEvent) => openEditDialog(node, e)}
				>
					<Edit3Icon class="size-3.5" />
					<span>{m.categories_menu_rename()}</span>
				</DropdownMenu.Item>
				<DropdownMenu.Item
					class="gap-2 text-xs"
					onclick={() => {
						targetParentId = node.parentId || "root";
						isMoveDialogOpen = true;
					}}
				>
					<ArrowLeftRightIcon class="size-3.5" />
					<span>{m.categories_menu_move()}</span>
				</DropdownMenu.Item>
				<DropdownMenu.Separator />
				<DropdownMenu.Item
					class="gap-2 text-xs text-destructive focus:bg-destructive/10 focus:text-destructive"
					onclick={(e: MouseEvent) => promptDeleteCategory(node, e)}
				>
					<Trash2Icon class="size-3.5" />
					<span>{m.categories_menu_delete()}</span>
				</DropdownMenu.Item>
			</DropdownMenu.Content>
		</DropdownMenu.Root>
	{/snippet}

	{#if hasChildren}
		<FileTree.Folder
			id={node.id}
			name={node.name}
			count={node.count}
			bind:open={expandedNodes[node.id]}
			actions={nodeActions}
		>
			{#each node.children as child (child.id)}
				{@render renderTreeNode(child)}
			{/each}
		</FileTree.Folder>
	{:else}
		<FileTree.Item
			id={node.id}
			name={node.name}
			count={node.count}
			actions={nodeActions}
		/>
	{/if}
{/snippet}

<div class="@container/main flex flex-1 flex-col gap-6 p-4 sm:p-6 lg:p-8">
	<!-- Page Header with Top Actions -->
	<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
		<div>
			<div class="flex items-center gap-2">
				<h1 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
					{m.categories_title()}
				</h1>
				{#if isLoading}
					<Loader2Icon class="size-4 animate-spin text-muted-foreground" />
				{/if}
			</div>
			<p class="text-xs sm:text-sm text-muted-foreground mt-0.5">
				{m.categories_subtitle()}
			</p>
		</div>

		<div class="flex items-center gap-2">
			<Button
				variant="outline"
				size="sm"
				class="gap-1.5 font-medium shadow-2xs"
				onclick={collapseAll}
			>
				<FoldVerticalIcon class="size-3.5" />
				<span>{m.categories_collapse_all()}</span>
			</Button>

			<Button
				size="sm"
				class="gap-1.5 font-medium shadow-xs"
				onclick={() => {
					newCategoryParentId = "root";
					newCategoryName = "";
					isNewCategoryDialogOpen = true;
				}}
			>
				<PlusIcon class="size-3.5" />
				<span>{m.categories_new_category()}</span>
			</Button>
		</div>
	</div>

	<!-- Section 1: KPI Statistic Cards (Matching Main Dashboard SectionCards style) -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<!-- Card 1: Total Categories -->
		<Card.Root class="@container/card">
			<Card.Header>
				<Card.Description class="flex items-center gap-1.5 font-medium">
					<FolderIcon class="size-4 text-primary" />
					{m.categories_stat_total()}
				</Card.Description>
				<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
					{totalFolders}
				</Card.Title>
				<Card.Action>
					<Badge variant="outline" class="gap-1 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-950/20">
						<TrendingUpIcon class="size-3" />
						+2
					</Badge>
				</Card.Action>
			</Card.Header>
			<Card.Footer class="flex-col items-start gap-1 text-xs">
				<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
					{m.categories_stat_total_footer_title()}
				</div>
				<div class="text-muted-foreground">{m.categories_stat_total_footer_desc()}</div>
			</Card.Footer>
		</Card.Root>

		<!-- Card 2: Root Folders -->
		<Card.Root class="@container/card">
			<Card.Header>
				<Card.Description class="flex items-center gap-1.5 font-medium">
					<FolderTreeIcon class="size-4 text-primary" />
					{m.categories_stat_root()}
				</Card.Description>
				<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
					{rootFoldersCount}
				</Card.Title>
				<Card.Action>
					<Badge variant="outline" class="gap-1 border-primary/20 text-primary bg-primary/5">
						{m.categories_stat_root_badge()}
					</Badge>
				</Card.Action>
			</Card.Header>
			<Card.Footer class="flex-col items-start gap-1 text-xs">
				<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
					{m.categories_stat_root_footer_title()}
				</div>
				<div class="text-muted-foreground">{m.categories_stat_root_footer_desc()}</div>
			</Card.Footer>
		</Card.Root>

		<!-- Card 3: Categorized Images -->
		<Card.Root class="@container/card">
			<Card.Header>
				<Card.Description class="flex items-center gap-1.5 font-medium">
					<ImagesIcon class="size-4 text-primary" />
					{m.categories_stat_categorized()}
				</Card.Description>
				<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
					{categorizedImagesCount.toLocaleString()}
				</Card.Title>
				<Card.Action>
					<Badge variant="outline" class="gap-1 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 bg-emerald-50/50 dark:bg-emerald-950/20">
						<TrendingUpIcon class="size-3" />
						{categorizedPercentage}%
					</Badge>
				</Card.Action>
			</Card.Header>
			<Card.Footer class="flex-col items-start gap-1 text-xs">
				<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
					{m.categories_stat_categorized_footer_title()}
				</div>
				<div class="text-muted-foreground">{m.categories_stat_categorized_footer_desc()}</div>
			</Card.Footer>
		</Card.Root>

		<!-- Card 4: Uncategorized Images -->
		<Card.Root class="@container/card">
			<Card.Header>
				<Card.Description class="flex items-center gap-1.5 font-medium">
					<HelpCircleIcon class="size-4 text-primary" />
					{m.categories_stat_uncategorized()}
				</Card.Description>
				<Card.Title class="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
					{uncategorizedCount.toLocaleString()}
				</Card.Title>
				<Card.Action>
					<Badge variant="outline" class="gap-1 text-amber-600 dark:text-amber-400 border-amber-500/20 bg-amber-50/50 dark:bg-amber-950/20">
						{uncategorizedPercentage}%
					</Badge>
				</Card.Action>
			</Card.Header>
			<Card.Footer class="flex-col items-start gap-1 text-xs">
				<div class="line-clamp-1 flex gap-1.5 font-medium text-foreground">
					{m.categories_stat_uncategorized_footer_title()}
				</div>
				<div class="text-muted-foreground">{m.categories_stat_uncategorized_footer_desc()}</div>
			</Card.Footer>
		</Card.Root>
	</div>

	<!-- Main Two-Column Layout: Categories Sidebar & Details View -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
		<!-- Left Column: Category Hierarchy Tree (4 cols) -->
		<div class="lg:col-span-4">
			<Card.Root class="border border-border/80 bg-card/60 shadow-xs backdrop-blur-xs">
				<Card.Header class="pb-3 pt-5 px-4 sm:px-5">
					<Card.Title class="text-base font-semibold tracking-tight">
						{m.categories_tree_title()}
					</Card.Title>
					<div class="relative mt-2">
						<SearchIcon class="size-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
						<Input
							placeholder={m.categories_search_placeholder()}
							bind:value={categorySearch}
							class="pl-8 text-xs bg-background/50"
						/>
					</div>
				</Card.Header>

				<Card.Content class="p-2 sm:p-3 space-y-1">
					<!-- FileTree Root -->
					<div class="max-h-[500px] overflow-y-auto pr-1">
						<FileTree.Root bind:selectedId={selectedCategoryId}>
							{#each categoryTree as rootNode (rootNode.id)}
								{@render renderTreeNode(rootNode)}
							{/each}
						</FileTree.Root>
					</div>

					<!-- Bottom Uncategorized Row -->
					<div class="pt-3 border-t border-border/60 mt-2 px-2">
						<button
							type="button"
							class="flex w-full items-center justify-between rounded-lg px-2 py-2 text-xs font-medium cursor-pointer transition-colors {selectedCategoryId === 'uncategorized'
								? 'bg-muted text-foreground'
								: 'text-muted-foreground hover:bg-muted/40 hover:text-foreground'}"
							onclick={() => (selectedCategoryId = "uncategorized")}
						>
							<div class="flex items-center gap-2">
								<HelpCircleIcon class="size-3.5 text-muted-foreground" />
								<span>{m.categories_uncategorized_label()}</span>
							</div>
							<span class="text-[11px] tabular-nums text-muted-foreground">
								{uncategorizedCount.toLocaleString()} images
							</span>
						</button>
					</div>
				</Card.Content>
			</Card.Root>
		</div>

		<!-- Right Column: Details & Assigned Images (8 cols) -->
		<div class="lg:col-span-8 space-y-6">
			<!-- Selected Category Banner & Controls -->
			<Card.Root class="border border-border/80 bg-card/60 shadow-xs backdrop-blur-xs p-5 space-y-4">
				<div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
					<!-- Breadcrumb Category Path -->
					<div class="flex items-center gap-1.5 flex-wrap">
						{#if selectedCategoryId === "uncategorized"}
							<span class="text-base sm:text-lg font-bold tracking-tight text-foreground">
								{m.categories_uncategorized_collection()}
							</span>
						{:else}
							{#each breadcrumbs as crumb, i}
								<span class="text-base sm:text-lg font-bold tracking-tight {i === breadcrumbs.length - 1 ? 'text-foreground' : 'text-muted-foreground'}">
									{crumb.name}
								</span>
								{#if i < breadcrumbs.length - 1}
									<span class="text-muted-foreground text-sm font-normal">&gt;</span>
								{/if}
							{/each}

							{#if activeNode}
								<button
									type="button"
									class="p-1 text-muted-foreground hover:text-foreground transition-colors rounded"
									onclick={() => openEditDialog(activeNode)}
									title="Edit Name"
								>
									<Edit3Icon class="size-3.5" />
								</button>
							{/if}
						{/if}
					</div>

					<!-- Parent Selector & Delete Action -->
					{#if activeNode}
						<div class="flex items-center gap-2">
							<div class="text-xs text-muted-foreground flex items-center gap-1.5 border border-border/80 rounded-md px-2.5 py-1 bg-muted/20">
								<span>{m.categories_parent_label()}:</span>
								<strong class="text-foreground font-medium">
									{breadcrumbs.length > 1 ? breadcrumbs[breadcrumbs.length - 2].name : "Root"}
								</strong>
							</div>

							<Button
								variant="outline"
								size="sm"
								class="gap-1.5 text-xs text-destructive hover:bg-destructive/10 hover:text-destructive border-destructive/30"
								onclick={(e) => promptDeleteCategory(activeNode, e)}
							>
								<Trash2Icon class="size-3" />
								<span>{m.categories_delete_btn()}</span>
							</Button>
						</div>
					{/if}
				</div>

				<!-- Subcategory Pills / Quick actions -->
				{#if activeNode}
					<div class="flex items-center gap-2 flex-wrap pt-1">
						{#each currentSubcategories as sub (sub.id)}
							<button
								type="button"
								class="flex items-center gap-1.5 rounded-md border border-border/70 bg-muted/40 hover:bg-muted px-2.5 py-1 text-xs text-foreground transition-colors"
								onclick={() => selectCategory(sub.id)}
							>
								<span>{sub.name}</span>
								<span class="text-muted-foreground text-[10px] font-mono">({sub.count})</span>
							</button>
						{/each}

						<Button
							variant="outline"
							size="sm"
							class="h-8 gap-1 px-2.5 text-xs border-dashed"
							onclick={() => openAddSubcategoryDialog(activeNode.id)}
						>
							<PlusIcon class="size-3" />
							<span>{m.categories_add_subcategory_btn()}</span>
						</Button>
					</div>
				{/if}
			</Card.Root>

			<!-- Assigned Images Gallery Card -->
			<Card.Root class="border border-border/80 bg-card/60 shadow-xs backdrop-blur-xs">
				<Card.Header class="pb-3 pt-5 px-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
					<div class="flex items-center gap-2">
						<Card.Title class="text-base font-semibold tracking-tight">
							{m.categories_assigned_images_title()}
						</Card.Title>
						<span class="text-xs text-muted-foreground font-mono">
							({activeNode ? activeNode.count.toLocaleString() : uncategorizedCount.toLocaleString()})
						</span>
					</div>

					<div class="flex items-center gap-2">
						<!-- Image search box -->
						<div class="relative w-44 sm:w-56">
							<SearchIcon class="size-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground" />
							<Input
								placeholder={m.categories_search_images_placeholder()}
								bind:value={imageSearchQuery}
								class="pl-8 text-xs bg-background/50"
							/>
						</div>

						<Button variant="outline" size="sm" class="gap-1.5 text-xs">
							<MoveIcon class="size-3" />
							<span>{m.categories_move_btn()}</span>
						</Button>

						<Button variant="outline" size="sm" class="gap-1.5 text-xs text-muted-foreground hover:text-destructive">
							<BanIcon class="size-3" />
							<span>{m.categories_unassign_btn()}</span>
						</Button>
					</div>
				</Card.Header>

				<Card.Content class="p-6">
					<!-- Visual Grid of Assigned Images -->
					<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
						{#each filteredImages as img (img.id)}
							<div class="group relative flex flex-col rounded-lg border border-border/70 bg-card overflow-hidden shadow-2xs hover:shadow-xs hover:border-primary/40 transition-all">
								<div class="aspect-4/3 w-full overflow-hidden bg-muted">
									<img
										src={img.url}
										alt={img.filename}
										class="size-full object-cover group-hover:scale-105 transition-transform duration-300"
										loading="lazy"
									/>
								</div>
								<div class="p-2 bg-background/80 backdrop-blur-xs">
									<p class="truncate text-[11px] font-medium text-foreground" title={img.filename}>
										{img.filename}
									</p>
								</div>
							</div>
						{/each}
					</div>

					<!-- Placeholder Notice for Live Backend Sync -->
					<div class="mt-6 flex items-center justify-between rounded-lg border border-dashed border-border/80 p-3 bg-muted/20 text-xs text-muted-foreground">
						<div class="flex items-center gap-2">
							<ImageIcon class="size-4 opacity-60" />
							<span>Showing 8 of {activeNode ? activeNode.count.toLocaleString() : uncategorizedCount.toLocaleString()} indexed image records.</span>
						</div>
						<span class="text-[11px] font-mono opacity-80">GHIM-10K Shard A</span>
					</div>
				</Card.Content>
			</Card.Root>
		</div>
	</div>
</div>

<!-- Dialog 1: Create New Category -->
<Dialog.Root bind:open={isNewCategoryDialogOpen}>
	<Dialog.Content class="sm:max-w-[425px]">
		<Dialog.Header>
			<Dialog.Title>{m.categories_dialog_new_title()}</Dialog.Title>
			<Dialog.Description>
				{m.categories_dialog_new_desc()}
			</Dialog.Description>
		</Dialog.Header>

		<div class="space-y-4 py-3">
			<Field.Field>
				<Field.FieldLabel for="new-cat-name">{m.categories_dialog_name_label()}</Field.FieldLabel>
				<Input
					id="new-cat-name"
					placeholder={m.categories_dialog_name_placeholder()}
					bind:value={newCategoryName}
				/>
			</Field.Field>

			<Field.Field>
				<Field.FieldLabel for="parent-cat-select">{m.categories_dialog_parent_label()}</Field.FieldLabel>
				<select
					id="parent-cat-select"
					bind:value={newCategoryParentId}
					class="w-full rounded-md border border-input bg-background px-3 py-2 text-xs sm:text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
				>
					<option value="root">{m.categories_dialog_parent_root()}</option>
					{#each getAllCategories(categoryTree) as c}
						<option value={c.id}>{c.path}</option>
					{/each}
				</select>
			</Field.Field>
		</div>

		<Dialog.Footer>
			<Button variant="outline" size="sm" onclick={() => (isNewCategoryDialogOpen = false)}>
				{m.categories_dialog_cancel()}
			</Button>
			<Button size="sm" onclick={handleCreateCategory} disabled={!newCategoryName.trim() || isSubmitting}>
				{#if isSubmitting}
					<Loader2Icon class="size-3.5 animate-spin mr-1" />
				{/if}
				{m.categories_dialog_create_submit()}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Dialog 2: Edit Category Name -->
<Dialog.Root bind:open={isEditCategoryDialogOpen}>
	<Dialog.Content class="sm:max-w-[380px]">
		<Dialog.Header>
			<Dialog.Title>{m.categories_dialog_edit_title()}</Dialog.Title>
			<Dialog.Description>
				{m.categories_dialog_edit_desc()}
			</Dialog.Description>
		</Dialog.Header>

		<div class="py-3">
			<Field.Field>
				<Field.FieldLabel for="edit-cat-name">{m.categories_dialog_name_label()}</Field.FieldLabel>
				<Input id="edit-cat-name" bind:value={editingCategoryName} />
			</Field.Field>
		</div>

		<Dialog.Footer>
			<Button variant="outline" size="sm" onclick={() => (isEditCategoryDialogOpen = false)}>
				{m.categories_dialog_cancel()}
			</Button>
			<Button size="sm" onclick={handleSaveEdit} disabled={!editingCategoryName.trim() || isSubmitting}>
				{#if isSubmitting}
					<Loader2Icon class="size-3.5 animate-spin mr-1" />
				{/if}
				{m.categories_dialog_save_changes()}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Dialog 3: Add Child Subcategory Dialog -->
<Dialog.Root bind:open={isSubCategoryDialogOpen}>
	<Dialog.Content class="sm:max-w-[380px]">
		<Dialog.Header>
			<Dialog.Title>{m.categories_dialog_subcat_title()}</Dialog.Title>
			<Dialog.Description>
				{m.categories_dialog_subcat_desc({ name: activeNode?.name ?? '' })}
			</Dialog.Description>
		</Dialog.Header>

		<div class="py-3">
			<Field.Field>
				<Field.FieldLabel for="sub-cat-name">{m.categories_dialog_name_label()}</Field.FieldLabel>
				<Input
					id="sub-cat-name"
					placeholder={m.categories_dialog_subcat_placeholder()}
					bind:value={newCategoryName}
				/>
			</Field.Field>
		</div>

		<Dialog.Footer>
			<Button variant="outline" size="sm" onclick={() => (isSubCategoryDialogOpen = false)}>
				{m.categories_dialog_cancel()}
			</Button>
			<Button size="sm" onclick={handleCreateCategory} disabled={!newCategoryName.trim() || isSubmitting}>
				{#if isSubmitting}
					<Loader2Icon class="size-3.5 animate-spin mr-1" />
				{/if}
				{m.categories_dialog_create_submit()}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Dialog 4: Move Category Parent -->
<Dialog.Root bind:open={isMoveDialogOpen}>
	<Dialog.Content class="sm:max-w-[400px]">
		<Dialog.Header>
			<Dialog.Title>{m.categories_dialog_move_title()}</Dialog.Title>
			<Dialog.Description>
				{m.categories_dialog_move_desc({ name: activeNode?.name ?? '' })}
			</Dialog.Description>
		</Dialog.Header>

		<div class="py-3">
			<Field.Field>
				<Field.FieldLabel for="target-parent-select">{m.categories_dialog_parent_label()}</Field.FieldLabel>
				<select
					id="target-parent-select"
					bind:value={targetParentId}
					class="w-full rounded-md border border-input bg-background px-3 py-2 text-xs sm:text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
				>
					<option value="root">{m.categories_dialog_parent_root()}</option>
					{#each getAllCategories(categoryTree).filter(c => c.id !== activeNode?.id) as c}
						<option value={c.id}>{c.path}</option>
					{/each}
				</select>
			</Field.Field>
		</div>

		<Dialog.Footer>
			<Button variant="outline" size="sm" onclick={() => (isMoveDialogOpen = false)}>
				{m.categories_dialog_cancel()}
			</Button>
			<Button size="sm" onclick={handleMoveCategory} disabled={isSubmitting}>
				{#if isSubmitting}
					<Loader2Icon class="size-3.5 animate-spin mr-1" />
				{/if}
				{m.categories_dialog_move_submit()}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- Dialog 5: Delete Category Confirmation (shadcn AlertDialog) -->
<AlertDialog.Root bind:open={isDeleteDialogOpen}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>{m.categories_alert_delete_title({ name: categoryToDelete?.name ?? '' })}</AlertDialog.Title>
			<AlertDialog.Description>
				{m.categories_alert_delete_desc()}
			</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel onclick={() => { isDeleteDialogOpen = false; categoryToDelete = null; }}>
				{m.categories_dialog_cancel()}
			</AlertDialog.Cancel>
			<AlertDialog.Action
				class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
				onclick={confirmDeleteCategory}
				disabled={isSubmitting}
			>
				{#if isSubmitting}
					<Loader2Icon class="size-3.5 animate-spin mr-1" />
				{/if}
				{m.categories_delete_btn()}
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
