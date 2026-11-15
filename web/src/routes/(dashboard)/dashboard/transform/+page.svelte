<script lang="ts">
	import { onMount, onDestroy } from "svelte";
	import { page } from "$app/state";
	import * as m from "#lib/paraglide/messages.js";
	import { auth } from "#lib/auth.js";
	import { imageService, type ImageItem } from "#lib/images.js";
	import { categoryService, type CategoryItem } from "#lib/categories.js";
	import { Button } from "#lib/components/ui/button/index.js";
	import * as Card from "#lib/components/ui/card/index.js";
	import { Input } from "#lib/components/ui/input/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import * as Dialog from "#lib/components/ui/dialog/index.js";

	// Icons
	import RotateCcwIcon from "@lucide/svelte/icons/rotate-ccw";
	import RotateCwIcon from "@lucide/svelte/icons/rotate-cw";
	import Columns2Icon from "@lucide/svelte/icons/columns-2";
	import SparklesIcon from "@lucide/svelte/icons/sparkles";
	import PencilIcon from "@lucide/svelte/icons/pencil";
	import ScanIcon from "@lucide/svelte/icons/scan";
	import CropIcon from "@lucide/svelte/icons/crop";
	import ZoomInIcon from "@lucide/svelte/icons/zoom-in";
	import ZoomOutIcon from "@lucide/svelte/icons/zoom-out";
	import Maximize2Icon from "@lucide/svelte/icons/maximize-2";
	import FlipHorizontalIcon from "@lucide/svelte/icons/flip-horizontal";
	import FlipVerticalIcon from "@lucide/svelte/icons/flip-vertical";
	import CheckIcon from "@lucide/svelte/icons/check";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import ImageIcon from "@lucide/svelte/icons/image";
	import ExternalLinkIcon from "@lucide/svelte/icons/external-link";
	import CodeIcon from "@lucide/svelte/icons/code";
	import SlidersIcon from "@lucide/svelte/icons/sliders";
	import DownloadIcon from "@lucide/svelte/icons/download";
	import EyeIcon from "@lucide/svelte/icons/eye";
	import MoveIcon from "@lucide/svelte/icons/move";
	import CrosshairIcon from "@lucide/svelte/icons/crosshair";

	// State
	let user = $state(auth.getUser());
	let isLoading = $state(true);
	let isSaving = $state(false);
	let isDownloading = $state(false);
	let saveSuccessImage = $state<ImageItem | null>(null);
	let errorMessage = $state<string | null>(null);

	// User Images & Categories
	let userImages = $state<ImageItem[]>([]);
	let categories = $state<CategoryItem[]>([]);
	let isImagePickerOpen = $state(false);
	let showParamsDialog = $state(false);

	// Currently Active Image
	let currentImage = $state<ImageItem | null>(null);
	let currentImageUrl = $state<string>("/images/auth-hero.jpg");
	let originalWidth = $state<number>(1920);
	let originalHeight = $state<number>(1080);
	let originalFilename = $state<string>("ghim_nature_peak.jpg");
	let imageEl = $state<HTMLImageElement | null>(null);

	// Active Transform Operation (NO OPERATION SELECTED BY DEFAULT)
	type TransformOp = "crop" | "resize" | "rotate" | "flip" | "shear";
	let activeTab = $state<TransformOp | null>(null);

	// Preview & Comparison Controls
	let isComparing = $state(false);
	let zoomLevel = $state<number>(74);
	let activePreset = $state<string>("Free");

	// 1. Interactive Crop Parameters (iLoveIMG Style)
	let cropX = $state<number>(120);
	let cropY = $state<number>(100);
	let cropWidth = $state<number>(600);
	let cropHeight = $state<number>(450);
	let showRuleOfThirds = $state<boolean>(true);

	// Interactive Crop Drag State
	let activeCropDrag = $state<string | null>(null);
	let dragStartPointer = { x: 0, y: 0 };
	let dragStartCrop = { x: 0, y: 0, w: 0, h: 0 };

	// 2. Shear Parameters
	let shearX = $state<number>(0.25);
	let shearY = $state<number>(0.0);
	let shearExpand = $state<boolean>(true);
	let shearBgColor = $state<string>("#FFFFFF");

	// 3. Resize Parameters
	let resizeScale = $state<number>(1.0);
	let resizeWidth = $state<number>(1280);
	let resizeHeight = $state<number>(960);
	let keepAspectRatio = $state<boolean>(true);

	// 4. Rotate Parameters
	let rotateAngle = $state<number>(0);
	let rotateExpand = $state<boolean>(true);
	let rotateBgColor = $state<string>("#FFFFFF");

	// 5. Flip Parameters
	let flipDirection = $state<"horizontal" | "vertical">("horizontal");

	// Saved Info
	let derivedFilename = $state<string>("ghim_nature_peak_transformed.jpg");
	let selectedCategoryId = $state<string>("");

	// Helpers
	function clamp(val: number, min: number, max: number): number {
		return Math.max(min, Math.min(max, val));
	}

	// Computed dynamic output dimensions
	let computedOutputWidth = $derived.by(() => {
		if (!activeTab) return originalWidth;
		if (activeTab === "shear") {
			if (!shearExpand) return originalWidth;
			const corners = [
				[0, 0],
				[originalWidth, 0],
				[0, originalHeight],
				[originalWidth, originalHeight]
			];
			const transX = corners.map(([x, y]) => x + shearX * y);
			return Math.max(1, Math.round(Math.max(...transX) - Math.min(...transX)));
		} else if (activeTab === "crop") {
			return Math.min(originalWidth, Math.max(1, Math.round(cropWidth)));
		} else if (activeTab === "resize") {
			return Math.max(1, Math.round(resizeWidth));
		} else if (activeTab === "rotate") {
			if (!rotateExpand || rotateAngle === 0) return originalWidth;
			const rad = Math.abs(rotateAngle) * (Math.PI / 180);
			return Math.max(1, Math.round(originalWidth * Math.abs(Math.cos(rad)) + originalHeight * Math.abs(Math.sin(rad))));
		} else {
			return originalWidth;
		}
	});

	let computedOutputHeight = $derived.by(() => {
		if (!activeTab) return originalHeight;
		if (activeTab === "shear") {
			if (!shearExpand) return originalHeight;
			const corners = [
				[0, 0],
				[originalWidth, 0],
				[0, originalHeight],
				[originalWidth, originalHeight]
			];
			const transY = corners.map(([x, y]) => shearY * x + y);
			return Math.max(1, Math.round(Math.max(...transY) - Math.min(...transY)));
		} else if (activeTab === "crop") {
			return Math.min(originalHeight, Math.max(1, Math.round(cropHeight)));
		} else if (activeTab === "resize") {
			return Math.max(1, Math.round(resizeHeight));
		} else if (activeTab === "rotate") {
			if (!rotateExpand || rotateAngle === 0) return originalHeight;
			const rad = Math.abs(rotateAngle) * (Math.PI / 180);
			return Math.max(1, Math.round(originalWidth * Math.abs(Math.sin(rad)) + originalHeight * Math.abs(Math.cos(rad))));
		} else {
			return originalHeight;
		}
	});

	// Dynamic derived filename generator
	$effect(() => {
		const stem = originalFilename.replace(/\.[^/.]+$/, "");
		const ext = originalFilename.includes(".") ? "." + originalFilename.split(".").pop() : ".jpg";
		if (!activeTab) {
			derivedFilename = `${stem}_transformed${ext}`;
		} else if (activeTab === "shear") {
			derivedFilename = `${stem}_sheared${ext}`;
		} else if (activeTab === "crop") {
			derivedFilename = `${stem}_cropped${ext}`;
		} else if (activeTab === "resize") {
			derivedFilename = `${stem}_resized${ext}`;
		} else if (activeTab === "rotate") {
			derivedFilename = `${stem}_rotated${ext}`;
		} else if (activeTab === "flip") {
			derivedFilename = `${stem}_flipped_${flipDirection}${ext}`;
		}
	});

	// Active Params Object for API payload
	let activeParamsJson = $derived.by(() => {
		if (!activeTab) {
			return {};
		} else if (activeTab === "shear") {
			return {
				shear_x: Number(shearX),
				shear_y: Number(shearY),
				expand: shearExpand,
				bg_color: shearBgColor
			};
		} else if (activeTab === "crop") {
			return {
				x: Math.max(0, Math.floor(cropX)),
				y: Math.max(0, Math.floor(cropY)),
				width: Math.max(1, Math.floor(cropWidth)),
				height: Math.max(1, Math.floor(cropHeight))
			};
		} else if (activeTab === "resize") {
			return {
				width: Math.max(1, Math.floor(resizeWidth)),
				height: Math.max(1, Math.floor(resizeHeight)),
				keep_aspect_ratio: keepAspectRatio
			};
		} else if (activeTab === "rotate") {
			return {
				angle: Number(rotateAngle),
				expand: rotateExpand,
				bg_color: rotateBgColor
			};
		} else {
			return {
				direction: flipDirection
			};
		}
	});

	onMount(async () => {
		try {
			const [imgList, catList] = await Promise.allSettled([
				imageService.listImages({ per_page: 50 }),
				categoryService.getCategories({ tree: true })
			]);

			if (catList.status === "fulfilled") {
				categories = catList.value;
			}

			if (imgList.status === "fulfilled" && imgList.value.images.length > 0) {
				userImages = imgList.value.images;
				const queryImageId = page.url.searchParams.get("image_id");
				const found = queryImageId
					? userImages.find((img) => img.id === queryImageId)
					: userImages[0];

				if (found) {
					selectImage(found);
				}
			} else {
				originalFilename = "ghim_nature_peak.jpg";
				originalWidth = 1920;
				originalHeight = 1080;
				currentImageUrl = "/images/auth-hero.jpg";
				resetCropToCenter();
			}
		} catch (err: any) {
			console.error("Failed to load initial studio data:", err);
		} finally {
			isLoading = false;
		}
	});

	onDestroy(() => {
		if (typeof window !== "undefined") {
			window.removeEventListener("pointermove", handleCropPointerMove);
			window.removeEventListener("pointerup", handleCropPointerUp);
		}
		if (typeof document !== "undefined") {
			document.body.style.cursor = "";
			document.body.style.userSelect = "";
		}
	});

	function selectImage(img: ImageItem) {
		currentImage = img;
		originalFilename = img.filename;
		originalWidth = img.width || 1920;
		originalHeight = img.height || 1080;
		currentImageUrl = imageService.getImageFileUrl(img.id);
		resetCropToCenter();
		resizeWidth = originalWidth;
		resizeHeight = originalHeight;
		if (img.category_id) {
			selectedCategoryId = String(img.category_id);
		}
		isImagePickerOpen = false;
	}

	function resetCropToCenter() {
		cropWidth = Math.min(originalWidth, Math.max(100, Math.floor(originalWidth * 0.6)));
		cropHeight = Math.min(originalHeight, Math.max(100, Math.floor(originalHeight * 0.6)));
		cropX = Math.floor((originalWidth - cropWidth) / 2);
		cropY = Math.floor((originalHeight - cropHeight) / 2);
	}

	function handleImageLoad(e: Event) {
		const target = e.currentTarget as HTMLImageElement;
		if (target && target.naturalWidth && target.naturalHeight) {
			originalWidth = target.naturalWidth;
			originalHeight = target.naturalHeight;
			if (cropWidth > originalWidth || cropHeight > originalHeight) {
				resetCropToCenter();
			}
		}
	}

	// -------------------------------------------------------------------------
	// INTERACTIVE CROP BOX DRAG & RESIZE ENGINE (iLoveIMG 8-Point Control)
	// -------------------------------------------------------------------------
	interface CropHandleDef {
		id: string;
		label: string;
		cursor: string;
		positionStyle: string;
	}

	const cropHandles: CropHandleDef[] = [
		{ id: "nw", label: "Top-Left (NW)", cursor: "nw-resize", positionStyle: "top: 0; left: 0; transform: translate(-50%, -50%);" },
		{ id: "n", label: "Top-Center (N)", cursor: "n-resize", positionStyle: "top: 0; left: 50%; transform: translate(-50%, -50%);" },
		{ id: "ne", label: "Top-Right (NE)", cursor: "ne-resize", positionStyle: "top: 0; right: 0; transform: translate(50%, -50%);" },
		{ id: "e", label: "Middle-Right (E)", cursor: "e-resize", positionStyle: "top: 50%; right: 0; transform: translate(50%, -50%);" },
		{ id: "se", label: "Bottom-Right (SE)", cursor: "se-resize", positionStyle: "bottom: 0; right: 0; transform: translate(50%, 50%);" },
		{ id: "s", label: "Bottom-Center (S)", cursor: "s-resize", positionStyle: "bottom: 0; left: 50%; transform: translate(-50%, 50%);" },
		{ id: "sw", label: "Bottom-Left (SW)", cursor: "sw-resize", positionStyle: "bottom: 0; left: 0; transform: translate(-50%, 50%);" },
		{ id: "w", label: "Middle-Left (W)", cursor: "w-resize", positionStyle: "top: 50%; left: 0; transform: translate(-50%, -50%);" }
	];

	const cropCursorMap: Record<string, string> = {
		nw: "nw-resize",
		n: "n-resize",
		ne: "ne-resize",
		e: "e-resize",
		se: "se-resize",
		s: "s-resize",
		sw: "sw-resize",
		w: "w-resize",
		move: "move"
	};

	function handleCropPointerDown(handle: string, e: PointerEvent) {
		e.preventDefault();
		e.stopPropagation();
		activeCropDrag = handle;
		dragStartPointer = { x: e.clientX, y: e.clientY };
		dragStartCrop = { x: cropX, y: cropY, w: cropWidth, h: cropHeight };

		// Keep cursor locked during dragging across the whole document
		if (typeof document !== "undefined") {
			document.body.style.cursor = cropCursorMap[handle] || "move";
			document.body.style.userSelect = "none";
		}

		window.addEventListener("pointermove", handleCropPointerMove);
		window.addEventListener("pointerup", handleCropPointerUp);
	}

	function handleCropPointerMove(e: PointerEvent) {
		if (!activeCropDrag || !imageEl) return;
		const rect = imageEl.getBoundingClientRect();
		const displayW = rect.width;
		const displayH = rect.height;
		if (displayW <= 0 || displayH <= 0) return;

		const scaleX = originalWidth / displayW;
		const scaleY = originalHeight / displayH;

		const deltaX = Math.round((e.clientX - dragStartPointer.x) * scaleX);
		const deltaY = Math.round((e.clientY - dragStartPointer.y) * scaleY);

		if (activeCropDrag === "move") {
			cropX = clamp(dragStartCrop.x + deltaX, 0, originalWidth - cropWidth);
			cropY = clamp(dragStartCrop.y + deltaY, 0, originalHeight - cropHeight);
		} else if (activeCropDrag === "se") {
			cropWidth = clamp(dragStartCrop.w + deltaX, 20, originalWidth - dragStartCrop.x);
			cropHeight = clamp(dragStartCrop.h + deltaY, 20, originalHeight - dragStartCrop.y);
		} else if (activeCropDrag === "e") {
			cropWidth = clamp(dragStartCrop.w + deltaX, 20, originalWidth - dragStartCrop.x);
		} else if (activeCropDrag === "s") {
			cropHeight = clamp(dragStartCrop.h + deltaY, 20, originalHeight - dragStartCrop.y);
		} else if (activeCropDrag === "nw") {
			const newX = clamp(dragStartCrop.x + deltaX, 0, dragStartCrop.x + dragStartCrop.w - 20);
			const newY = clamp(dragStartCrop.y + deltaY, 0, dragStartCrop.y + dragStartCrop.h - 20);
			cropWidth = dragStartCrop.w + (dragStartCrop.x - newX);
			cropHeight = dragStartCrop.h + (dragStartCrop.y - newY);
			cropX = newX;
			cropY = newY;
		} else if (activeCropDrag === "ne") {
			const newY = clamp(dragStartCrop.y + deltaY, 0, dragStartCrop.y + dragStartCrop.h - 20);
			cropWidth = clamp(dragStartCrop.w + deltaX, 20, originalWidth - dragStartCrop.x);
			cropHeight = dragStartCrop.h + (dragStartCrop.y - newY);
			cropY = newY;
		} else if (activeCropDrag === "sw") {
			const newX = clamp(dragStartCrop.x + deltaX, 0, dragStartCrop.x + dragStartCrop.w - 20);
			cropWidth = dragStartCrop.w + (dragStartCrop.x - newX);
			cropHeight = clamp(dragStartCrop.h + deltaY, 20, originalHeight - dragStartCrop.y);
			cropX = newX;
		} else if (activeCropDrag === "n") {
			const newY = clamp(dragStartCrop.y + deltaY, 0, dragStartCrop.y + dragStartCrop.h - 20);
			cropHeight = dragStartCrop.h + (dragStartCrop.y - newY);
			cropY = newY;
		} else if (activeCropDrag === "w") {
			const newX = clamp(dragStartCrop.x + deltaX, 0, dragStartCrop.x + dragStartCrop.w - 20);
			cropWidth = dragStartCrop.w + (dragStartCrop.x - newX);
			cropX = newX;
		}
	}

	function handleCropPointerUp() {
		activeCropDrag = null;
		if (typeof document !== "undefined") {
			document.body.style.cursor = "";
			document.body.style.userSelect = "";
		}
		window.removeEventListener("pointermove", handleCropPointerMove);
		window.removeEventListener("pointerup", handleCropPointerUp);
	}

	function resetCanvas() {
		activeTab = null;
		shearX = 0.25;
		shearY = 0.0;
		shearExpand = true;
		shearBgColor = "#FFFFFF";
		resetCropToCenter();
		resizeScale = 1.0;
		resizeWidth = originalWidth;
		resizeHeight = originalHeight;
		rotateAngle = 0;
		rotateExpand = true;
		rotateBgColor = "#FFFFFF";
		flipDirection = "horizontal";
		zoomLevel = 74;
		activePreset = "Free";
	}

	async function handleSaveDerivedImage() {
		if (!activeTab) {
			errorMessage = "Please select a transformation operation (Crop, Resize, Rotate, Flip, or Shear) from the top bar before saving.";
			return;
		}

		isSaving = true;
		errorMessage = null;
		saveSuccessImage = null;

		try {
			if (!currentImage) {
				const mockDerived: ImageItem = {
					id: "mock-" + Math.random().toString(36).substring(2, 9),
					owner_id: user?.email || "zarqi_ezzoubair",
					parent_image_id: "ghim_nature_peak",
					filename: derivedFilename,
					storage_key: `derived/${user?.email || "zarqi_ezzoubair"}/${derivedFilename}`,
					source_type: "derived",
					processing_status: "completed",
					mime_type: "image/jpeg",
					file_size: 1420580,
					width: computedOutputWidth,
					height: computedOutputHeight,
					created_at: new Date().toISOString(),
					transformation_params: {
						operation: activeTab,
						params: activeParamsJson
					}
				};
				saveSuccessImage = mockDerived;
				return;
			}

			const derived = await imageService.transformImage(currentImage.id, {
				operation: activeTab,
				params: activeParamsJson,
				filename: derivedFilename,
				category_id: selectedCategoryId ? Number(selectedCategoryId) : null
			});

			saveSuccessImage = derived;
		} catch (err: any) {
			errorMessage = err.message || "Failed to create derived transformed image.";
		} finally {
			isSaving = false;
		}
	}

	async function handleDownloadImage() {
		isDownloading = true;
		errorMessage = null;
		try {
			const canvas = document.createElement("canvas");
			const ctx = canvas.getContext("2d");
			if (!ctx) throw new Error("Could not initialize 2D rendering canvas context.");

			const img = new Image();
			img.crossOrigin = "anonymous";
			img.src = currentImageUrl;

			await new Promise((resolve, reject) => {
				img.onload = resolve;
				img.onerror = () => reject(new Error("Failed to load source image for download."));
			});

			const w = img.naturalWidth || originalWidth;
			const h = img.naturalHeight || originalHeight;

			if (!activeTab) {
				canvas.width = w;
				canvas.height = h;
				ctx.drawImage(img, 0, 0);
			} else if (activeTab === "shear") {
				const corners = [
					[0, 0],
					[w, 0],
					[0, h],
					[w, h]
				];
				const trans = corners.map(([x, y]) => [x + shearX * y, shearY * x + y]);
				const minX = Math.min(...trans.map((pt) => pt[0]));
				const maxX = Math.max(...trans.map((pt) => pt[0]));
				const minY = Math.min(...trans.map((pt) => pt[1]));
				const maxY = Math.max(...trans.map((pt) => pt[1]));

				if (shearExpand) {
					canvas.width = Math.max(1, Math.ceil(maxX - minX));
					canvas.height = Math.max(1, Math.ceil(maxY - minY));
					ctx.fillStyle = shearBgColor;
					ctx.fillRect(0, 0, canvas.width, canvas.height);
					ctx.setTransform(1, shearY, shearX, 1, -minX, -minY);
				} else {
					canvas.width = w;
					canvas.height = h;
					ctx.fillStyle = shearBgColor;
					ctx.fillRect(0, 0, canvas.width, canvas.height);
					ctx.setTransform(1, shearY, shearX, 1, 0, 0);
				}
				ctx.drawImage(img, 0, 0);
			} else if (activeTab === "crop") {
				const clampedX = clamp(cropX, 0, w - 1);
				const clampedY = clamp(cropY, 0, h - 1);
				const clampedW = clamp(cropWidth, 1, w - clampedX);
				const clampedH = clamp(cropHeight, 1, h - clampedY);
				canvas.width = clampedW;
				canvas.height = clampedH;
				ctx.drawImage(img, clampedX, clampedY, clampedW, clampedH, 0, 0, clampedW, clampedH);
			} else if (activeTab === "resize") {
				canvas.width = Math.max(1, resizeWidth);
				canvas.height = Math.max(1, resizeHeight);
				ctx.drawImage(img, 0, 0, resizeWidth, resizeHeight);
			} else if (activeTab === "rotate") {
				if (rotateExpand && rotateAngle !== 0) {
					const rad = Math.abs(rotateAngle) * (Math.PI / 180);
					canvas.width = Math.max(1, Math.round(w * Math.abs(Math.cos(rad)) + h * Math.abs(Math.sin(rad))));
					canvas.height = Math.max(1, Math.round(w * Math.abs(Math.sin(rad)) + h * Math.abs(Math.cos(rad))));
				} else {
					canvas.width = w;
					canvas.height = h;
				}
				ctx.fillStyle = rotateBgColor;
				ctx.fillRect(0, 0, canvas.width, canvas.height);
				ctx.translate(canvas.width / 2, canvas.height / 2);
				ctx.rotate(rotateAngle * (Math.PI / 180));
				ctx.drawImage(img, -w / 2, -h / 2);
			} else if (activeTab === "flip") {
				canvas.width = w;
				canvas.height = h;
				ctx.translate(flipDirection === "horizontal" ? w : 0, flipDirection === "vertical" ? h : 0);
				ctx.scale(flipDirection === "horizontal" ? -1 : 1, flipDirection === "vertical" ? -1 : 1);
				ctx.drawImage(img, 0, 0);
			}

			const dataUrl = canvas.toDataURL("image/jpeg", 0.95);
			const link = document.createElement("a");
			link.download = derivedFilename || "transformed_image.jpg";
			link.href = dataUrl;
			link.click();
		} catch (err: any) {
			errorMessage = "Download error: " + (err.message || String(err));
		} finally {
			isDownloading = false;
		}
	}
</script>

<svelte:head>
	<title>Image Transformation Studio • Perceptra</title>
</svelte:head>

<div class="@container/main flex flex-1 flex-col gap-6 p-4 sm:p-6 lg:p-8">
	<!-- ========================================================================= -->
	<!-- 1. STUDIO HEADER ROW                                                      -->
	<!-- ========================================================================= -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<h1 class="text-xl sm:text-2xl font-bold tracking-tight text-foreground">
				Image Transformation Studio
			</h1>
			<p class="text-xs sm:text-sm text-muted-foreground mt-0.5">
				Create non-destructive derived images via crop, scaling, rotation, flip, and affine shear.
			</p>
		</div>

		<!-- Action Buttons -->
		<div class="flex items-center gap-2.5 flex-wrap">
			<!-- Select Image Modal Trigger -->
			<Button
				variant="outline"
				size="sm"
				class="h-9 px-3 text-xs font-semibold gap-1.5 cursor-pointer shadow-xs"
				onclick={() => (isImagePickerOpen = true)}
			>
				<ImageIcon class="size-3.5 text-muted-foreground" />
				<span class="max-w-[120px] truncate">{originalFilename}</span>
			</Button>

			<!-- Reset Canvas -->
			<Button
				variant="outline"
				size="sm"
				class="h-9 px-3.5 text-xs font-semibold gap-1.5 cursor-pointer shadow-xs"
				onclick={resetCanvas}
				title="Reset all transformation parameters"
			>
				<RotateCcwIcon class="size-3.5" />
				<span>Reset Canvas</span>
			</Button>

			<!-- Compare Original -->
			<Button
				variant={isComparing ? "secondary" : "outline"}
				size="sm"
				class="h-9 px-3.5 text-xs font-semibold gap-1.5 cursor-pointer shadow-xs {isComparing ? 'ring-2 ring-primary/40' : ''}"
				onclick={() => (isComparing = !isComparing)}
				onpointerdown={() => (isComparing = true)}
				onpointerup={() => (isComparing = false)}
				title="Hold or click to toggle original image preview"
			>
				<Columns2Icon class="size-3.5" />
				<span>{isComparing ? "Showing Original" : "Compare Original"}</span>
			</Button>

			<!-- Download Transformed Image Button -->
			<Button
				variant="outline"
				size="sm"
				class="h-9 px-3.5 text-xs font-semibold gap-1.5 cursor-pointer shadow-xs hover:border-primary/50"
				disabled={isDownloading}
				onclick={handleDownloadImage}
				title="Download image directly to your computer"
			>
				{#if isDownloading}
					<Loader2Icon class="size-3.5 animate-spin" />
					<span>Preparing...</span>
				{:else}
					<DownloadIcon class="size-3.5 text-primary" />
					<span>Download Image</span>
				{/if}
			</Button>

			<!-- Save Derived Image Button (GitHub Blue Accent) -->
			<Button
				size="sm"
				class="h-9 px-4 text-xs font-semibold gap-1.5 cursor-pointer shadow-xs"
				disabled={isSaving}
				onclick={handleSaveDerivedImage}
				title="Save as non-destructive derived image into your dataset"
			>
				{#if isSaving}
					<Loader2Icon class="size-3.5 animate-spin" />
					<span>Saving...</span>
				{:else}
					<PencilIcon class="size-3.5" />
					<span>Save Derived Image</span>
				{/if}
			</Button>
		</div>
	</div>

	<!-- Alert Messages -->
	{#if errorMessage}
		<div class="p-3.5 rounded-lg border border-destructive/30 bg-destructive/10 text-destructive text-xs flex items-center justify-between">
			<span>{errorMessage}</span>
			<button type="button" class="underline font-bold" onclick={() => (errorMessage = null)}>Dismiss</button>
		</div>
	{/if}

	{#if saveSuccessImage}
		<div class="p-4 rounded-xl border border-primary/30 bg-primary/10 text-foreground text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs">
			<div class="flex items-center gap-2.5">
				<div class="size-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold">✓</div>
				<div>
					<p class="font-bold">Derived Image Successfully Saved!</p>
					<p class="text-muted-foreground font-mono text-[11px]">
						{saveSuccessImage.filename} ({saveSuccessImage.width}×{saveSuccessImage.height} px) &bull; Non-destructive child record created.
					</p>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<Button
					variant="outline"
					size="xs"
					class="h-8 px-3 text-xs gap-1"
					onclick={handleDownloadImage}
				>
					<DownloadIcon class="size-3" />
					<span>Download</span>
				</Button>
				<Button href="/dashboard/images" variant="outline" size="xs" class="h-8 px-3 text-xs">
					View in Gallery
					<ExternalLinkIcon class="size-3 ml-1" />
				</Button>
				<Button variant="ghost" size="xs" class="h-8 px-2 text-xs" onclick={() => (saveSuccessImage = null)}>
					Dismiss
				</Button>
			</div>
		</div>
	{/if}

	<!-- ========================================================================= -->
	<!-- 2. MAIN WORKSPACE (2-COLUMN GRID)                                         -->
	<!-- ========================================================================= -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
		<!-- --------------------------------------------------------------------- -->
		<!-- LEFT: Interactive Transformation Canvas & Top Operations Toolbar      -->
		<!-- --------------------------------------------------------------------- -->
		<div class="lg:col-span-8 flex flex-col gap-3">
			<Card.Root class="overflow-hidden border border-border shadow-xs flex flex-col">
				<!-- CARD HEADER: Title on left, Horizontal Operation Toolbar on Top -->
				<Card.Header class="py-2.5 px-4 border-b border-border bg-card/60 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
					<div class="flex items-center gap-2">
						<Card.Title class="text-sm font-bold tracking-tight text-foreground whitespace-nowrap">
							Interactive Transformation Canvas
						</Card.Title>
						{#if activeTab}
							<Badge variant="outline" class="text-[10px] font-mono capitalize hidden sm:inline-flex">
								{activeTab} mode
							</Badge>
						{/if}
					</div>

					<!-- HORIZONTAL OPERATIONS TOOLBAR ON TOP OF CANVAS -->
					<div class="flex items-center gap-1 overflow-x-auto py-0.5">
						<!-- None / Original (Default) -->
						<button
							type="button"
							class="h-7 px-2.5 rounded-md text-xs font-semibold inline-flex items-center gap-1.5 transition-all cursor-pointer {activeTab === null ? 'bg-primary text-primary-foreground shadow-xs font-bold' : 'bg-muted/70 text-muted-foreground hover:text-foreground'}"
							onclick={() => (activeTab = null)}
							title="View original image with no transformation"
						>
							<EyeIcon class="size-3" />
							<span>None</span>
						</button>

						<!-- Crop (Interactive iLoveIMG Style) -->
						<button
							type="button"
							class="h-7 px-2.5 rounded-md text-xs font-semibold inline-flex items-center gap-1.5 transition-all cursor-pointer {activeTab === 'crop' ? 'bg-primary text-primary-foreground shadow-xs font-bold' : 'bg-muted/70 text-muted-foreground hover:text-foreground'}"
							onclick={() => {
								activeTab = "crop";
								if (cropWidth > originalWidth || cropHeight > originalHeight) {
									resetCropToCenter();
								}
							}}
							title="Interactive crop box over image"
						>
							<CropIcon class="size-3" />
							<span>Crop</span>
						</button>

						<!-- Resize -->
						<button
							type="button"
							class="h-7 px-2.5 rounded-md text-xs font-semibold inline-flex items-center gap-1.5 transition-all cursor-pointer {activeTab === 'resize' ? 'bg-primary text-primary-foreground shadow-xs font-bold' : 'bg-muted/70 text-muted-foreground hover:text-foreground'}"
							onclick={() => (activeTab = "resize")}
							title="Scale and resize dimensions"
						>
							<Maximize2Icon class="size-3" />
							<span>Resize</span>
						</button>

						<!-- Rotate -->
						<button
							type="button"
							class="h-7 px-2.5 rounded-md text-xs font-semibold inline-flex items-center gap-1.5 transition-all cursor-pointer {activeTab === 'rotate' ? 'bg-primary text-primary-foreground shadow-xs font-bold' : 'bg-muted/70 text-muted-foreground hover:text-foreground'}"
							onclick={() => (activeTab = "rotate")}
							title="Rotate image orientation"
						>
							<RotateCwIcon class="size-3" />
							<span>Rotate</span>
						</button>

						<!-- Flip -->
						<button
							type="button"
							class="h-7 px-2.5 rounded-md text-xs font-semibold inline-flex items-center gap-1.5 transition-all cursor-pointer {activeTab === 'flip' ? 'bg-primary text-primary-foreground shadow-xs font-bold' : 'bg-muted/70 text-muted-foreground hover:text-foreground'}"
							onclick={() => (activeTab = "flip")}
							title="Mirror reflection horizontally or vertically"
						>
							<FlipHorizontalIcon class="size-3" />
							<span>Flip</span>
						</button>

						<!-- Shear -->
						<button
							type="button"
							class="h-7 px-2.5 rounded-md text-xs font-semibold inline-flex items-center gap-1.5 transition-all cursor-pointer {activeTab === 'shear' ? 'bg-primary text-primary-foreground shadow-xs font-bold' : 'bg-muted/70 text-muted-foreground hover:text-foreground'}"
							onclick={() => (activeTab = "shear")}
							title="Affine shear deformation"
						>
							<SparklesIcon class="size-3" />
							<span>Shear</span>
						</button>
					</div>
				</Card.Header>

				<!-- CANVAS VIEWPORT (Checkerboard Background) -->
				<Card.Content class="p-4 sm:p-6 bg-muted/20 flex-1">
					<div
						class="relative w-full h-[380px] sm:h-[460px] md:h-[520px] xl:h-[580px] rounded-xl border border-border overflow-hidden flex items-center justify-center p-6 select-none bg-[linear-gradient(45deg,#e5e7eb_25%,transparent_25%),linear-gradient(-45deg,#e5e7eb_25%,transparent_25%),linear-gradient(45deg,transparent_75%,#e5e7eb_75%),linear-gradient(-45deg,transparent_75%,#e5e7eb_75%)] bg-[size:16px_16px] bg-[position:0_0,0_8px,8px_-8px,-8px_0px] dark:bg-[linear-gradient(45deg,#161b22_25%,transparent_25%),linear-gradient(-45deg,#161b22_25%,transparent_25%),linear-gradient(45deg,transparent_75%,#161b22_75%),linear-gradient(-45deg,transparent_75%,#161b22_75%)]"
					>
						<!-- Background Fill Layer when expand or shear is applied -->
						<div
							class="absolute inset-0 transition-colors pointer-events-none"
							style="background-color: {activeTab === 'shear' || activeTab === 'rotate' ? shearBgColor + '20' : 'transparent'};"
						></div>

						<!-- Zoom Scaler Container -->
						<div
							class="relative max-w-full max-h-full transition-all duration-150 ease-out origin-center flex items-center justify-center"
							style="transform: scale({zoomLevel / 100});"
						>
							<!-- Image Wrapper -->
							<div
								class="relative overflow-hidden shadow-2xl transition-transform duration-100 ease-out select-none"
								style="
									{isComparing || !activeTab || activeTab === 'crop'
										? 'transform: none;'
										: activeTab === 'shear'
											? `transform: matrix(1, ${shearY}, ${shearX}, 1, 0, 0);`
											: activeTab === 'rotate'
												? `transform: rotate(${rotateAngle}deg);`
												: activeTab === 'flip'
													? `transform: scale(${flipDirection === 'horizontal' ? -1 : 1}, ${flipDirection === 'vertical' ? -1 : 1});`
													: ''}
								"
							>
								<!-- The Source Image Element -->
								<img
									bind:this={imageEl}
									src={currentImageUrl}
									alt={originalFilename}
									onload={handleImageLoad}
									class="max-w-[680px] max-h-[400px] object-contain rounded-xs border border-white/20 select-none pointer-events-none block"
								/>

								<!-- ========================================================= -->
								<!-- INTERACTIVE CROP BOX OVERLAY (iLoveIMG Style with 8 Points) -->
								<!-- ========================================================= -->
								{#if activeTab === "crop" && !isComparing}
									<div
										role="region"
										aria-label="Interactive crop selection box"
										class="absolute border-2 border-[#0969da] cursor-move select-none shadow-[0_0_0_9999px_rgba(0,0,0,0.55)] transition-shadow z-30"
										style="
											left: {(cropX / originalWidth) * 100}%;
											top: {(cropY / originalHeight) * 100}%;
											width: {(cropWidth / originalWidth) * 100}%;
											height: {(cropHeight / originalHeight) * 100}%;
											cursor: move;
										"
										onpointerdown={(e) => handleCropPointerDown("move", e)}
									>
										<!-- Rule of Thirds Guide Lines -->
										{#if showRuleOfThirds}
											<div class="absolute inset-0 pointer-events-none">
												<div class="absolute top-0 bottom-0 left-1/3 w-px border-l border-white/60 border-dashed"></div>
												<div class="absolute top-0 bottom-0 left-2/3 w-px border-l border-white/60 border-dashed"></div>
												<div class="absolute left-0 right-0 top-1/3 h-px border-t border-white/60 border-dashed"></div>
												<div class="absolute left-0 right-0 top-2/3 h-px border-t border-white/60 border-dashed"></div>
											</div>
										{/if}

										<!-- Center Subtle Crosshair Mark (iLoveIMG Style) -->
										<div class="absolute inset-0 flex items-center justify-center pointer-events-none">
											<div class="relative w-3.5 h-3.5 opacity-60">
												<div class="absolute left-1/2 top-0 bottom-0 w-px -translate-x-1/2 bg-[#0969da]"></div>
												<div class="absolute top-1/2 left-0 right-0 h-px -translate-y-1/2 bg-[#0969da]"></div>
											</div>
										</div>

										<!-- 8 Precise Control Points (Corners & Midpoint Edges) with Native Directional Cursors -->
										{#each cropHandles as handle (handle.id)}
											<div
												role="button"
												tabindex="0"
												aria-label="Resize {handle.label}"
												class="absolute size-2.5 sm:size-3 bg-[#0969da] border border-white shadow-xs rounded-[1.5px] z-40 transition-transform hover:scale-125 focus:outline-hidden after:absolute after:-inset-2 after:content-['']"
												style="{handle.positionStyle}; cursor: {handle.cursor};"
												onpointerdown={(e) => handleCropPointerDown(handle.id, e)}
											></div>
										{/each}
									</div>

								<!-- General Visual Grid Overlay for Other Transformations -->
								{:else if activeTab && activeTab !== "crop"}
									<div class="absolute inset-0 pointer-events-none border border-white/40">
										<div class="absolute top-0 bottom-0 left-1/3 w-px bg-white/30 shadow-[0_0_1px_rgba(0,0,0,0.8)]"></div>
										<div class="absolute top-0 bottom-0 left-2/3 w-px bg-white/30 shadow-[0_0_1px_rgba(0,0,0,0.8)]"></div>
										<div class="absolute left-0 right-0 top-1/3 h-px bg-white/30 shadow-[0_0_1px_rgba(0,0,0,0.8)]"></div>
										<div class="absolute left-0 right-0 top-2/3 h-px bg-white/30 shadow-[0_0_1px_rgba(0,0,0,0.8)]"></div>
									</div>
								{/if}
							</div>
						</div>
					</div>
				</Card.Content>

				<!-- DOCKED BOTTOM STATUS BAR (Card Footer) -->
				<Card.Footer class="py-2.5 px-4 border-t border-border bg-card/60 flex flex-wrap items-center justify-between gap-3 text-[11px] font-mono text-muted-foreground">
					<div class="flex items-center gap-2 text-foreground font-medium">
						<span>Zoom: Fit ({zoomLevel}%)</span>
						<div class="flex items-center gap-0.5 ml-1">
							<button
								type="button"
								class="p-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
								onclick={() => (zoomLevel = Math.max(30, zoomLevel - 10))}
								title="Zoom out"
							>
								<ZoomOutIcon class="size-3" />
							</button>
							<button
								type="button"
								class="p-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
								onclick={() => (zoomLevel = Math.min(150, zoomLevel + 10))}
								title="Zoom in"
							>
								<ZoomInIcon class="size-3" />
							</button>
						</div>
					</div>

					<div class="flex items-center gap-3 sm:gap-4 flex-wrap">
						<span>Original: <strong class="text-foreground">{originalWidth}×{originalHeight} px</strong></span>
						<span class="text-border">|</span>
						<span>Output: <strong class="text-foreground">{computedOutputWidth}×{computedOutputHeight} px (JPEG)</strong></span>
						<span class="text-border">|</span>
						<span>Preset: <strong class="text-foreground">{activePreset}</strong></span>
					</div>
				</Card.Footer>
			</Card.Root>
		</div>

		<!-- --------------------------------------------------------------------- -->
		<!-- RIGHT: Operation Configuration Inspector & Saved Info                 -->
		<!-- --------------------------------------------------------------------- -->
		<div class="lg:col-span-4 flex flex-col gap-6">
			<!-- CARD 1: Operation Configuration Inspector -->
			<Card.Root class="border border-border shadow-xs">
				<Card.Header class="py-3 px-4 border-b border-border bg-card/60 flex items-center justify-between">
					<Card.Title class="text-sm font-bold tracking-tight text-foreground">
						{activeTab === "crop" ? "Crop Options" : "Operation & Parameters Inspector"}
					</Card.Title>
					{#if activeTab}
						<Badge variant="secondary" class="text-[10px] font-mono uppercase">
							{activeTab}
						</Badge>
					{/if}
				</Card.Header>

				<Card.Content class="p-4 space-y-5">
					<!-- NO OPERATION SELECTED IDLE STATE -->
					{#if activeTab === null}
						<div class="py-10 px-4 text-center space-y-3">
							<div class="size-12 rounded-full bg-muted/80 border border-border flex items-center justify-center mx-auto text-muted-foreground shadow-2xs">
								<SlidersIcon class="size-6" />
							</div>
							<div class="space-y-1">
								<h4 class="text-sm font-semibold text-foreground">No Operation Selected</h4>
								<p class="text-xs text-muted-foreground leading-relaxed">
									Select a tool from the top toolbar above the canvas to customize parameters:
								</p>
							</div>
							<div class="grid grid-cols-2 gap-2 pt-2 text-left">
								<button
									type="button"
									class="p-2.5 rounded-lg border border-border bg-muted/30 hover:bg-muted/80 transition-colors text-xs flex items-center gap-2 cursor-pointer"
									onclick={() => {
										activeTab = "crop";
										resetCropToCenter();
									}}
								>
									<CropIcon class="size-4 text-primary" />
									<div>
										<div class="font-bold text-foreground">Crop</div>
										<div class="text-[10px] text-muted-foreground">Interactive box</div>
									</div>
								</button>
								<button
									type="button"
									class="p-2.5 rounded-lg border border-border bg-muted/30 hover:bg-muted/80 transition-colors text-xs flex items-center gap-2 cursor-pointer"
									onclick={() => (activeTab = "shear")}
								>
									<SparklesIcon class="size-4 text-primary" />
									<div>
										<div class="font-bold text-foreground">Shear</div>
										<div class="text-[10px] text-muted-foreground">Affine distortion</div>
									</div>
								</button>
								<button
									type="button"
									class="p-2.5 rounded-lg border border-border bg-muted/30 hover:bg-muted/80 transition-colors text-xs flex items-center gap-2 cursor-pointer"
									onclick={() => (activeTab = "resize")}
								>
									<Maximize2Icon class="size-4 text-primary" />
									<div>
										<div class="font-bold text-foreground">Resize</div>
										<div class="text-[10px] text-muted-foreground">Scale & dimensions</div>
									</div>
								</button>
								<button
									type="button"
									class="p-2.5 rounded-lg border border-border bg-muted/30 hover:bg-muted/80 transition-colors text-xs flex items-center gap-2 cursor-pointer"
									onclick={() => (activeTab = "rotate")}
								>
									<RotateCwIcon class="size-4 text-primary" />
									<div>
										<div class="font-bold text-foreground">Rotate</div>
										<div class="text-[10px] text-muted-foreground">Orientation</div>
									</div>
								</button>
							</div>
						</div>

					<!-- TAB PANEL: CROP (Exact iLoveIMG Options Layout) -->
					{:else if activeTab === "crop"}
						<div class="space-y-4 pt-1">
							<!-- Dimensions Inputs (Matching iLoveIMG Screenshot) -->
							<div class="space-y-3">
								<div class="flex items-center justify-between gap-4">
									<label for="crop-width" class="text-xs font-semibold text-foreground">Width (px)</label>
									<Input
										id="crop-width"
										type="number"
										min="10"
										max={originalWidth}
										bind:value={cropWidth}
										oninput={() => {
											cropWidth = clamp(cropWidth, 10, originalWidth);
											if (cropX + cropWidth > originalWidth) {
												cropX = originalWidth - cropWidth;
											}
										}}
										class="h-8 w-28 text-right font-mono text-xs"
									/>
								</div>

								<div class="flex items-center justify-between gap-4">
									<label for="crop-height" class="text-xs font-semibold text-foreground">Height (px)</label>
									<Input
										id="crop-height"
										type="number"
										min="10"
										max={originalHeight}
										bind:value={cropHeight}
										oninput={() => {
											cropHeight = clamp(cropHeight, 10, originalHeight);
											if (cropY + cropHeight > originalHeight) {
												cropY = originalHeight - cropHeight;
											}
										}}
										class="h-8 w-28 text-right font-mono text-xs"
									/>
								</div>

								<div class="flex items-center justify-between gap-4">
									<label for="crop-pos-x" class="text-xs font-semibold text-foreground">Position X (px)</label>
									<Input
										id="crop-pos-x"
										type="number"
										min="0"
										max={Math.max(0, originalWidth - cropWidth)}
										bind:value={cropX}
										oninput={() => {
											cropX = clamp(cropX, 0, Math.max(0, originalWidth - cropWidth));
										}}
										class="h-8 w-28 text-right font-mono text-xs"
									/>
								</div>

								<div class="flex items-center justify-between gap-4">
									<label for="crop-pos-y" class="text-xs font-semibold text-foreground">Position Y (px)</label>
									<Input
										id="crop-pos-y"
										type="number"
										min="0"
										max={Math.max(0, originalHeight - cropHeight)}
										bind:value={cropY}
										oninput={() => {
											cropY = clamp(cropY, 0, Math.max(0, originalHeight - cropHeight));
										}}
										class="h-8 w-28 text-right font-mono text-xs"
									/>
								</div>
							</div>

							<!-- Aspect Ratio Presets -->
							<div class="space-y-1.5 pt-2 border-t border-border/70">
								<span class="text-xs font-semibold text-foreground">Aspect Presets</span>
								<div class="grid grid-cols-4 gap-1.5">
									{#each ["Free", "1:1", "4:3", "16:9"] as preset}
										<button
											type="button"
											class="py-1 px-2 rounded-md border text-xs font-medium cursor-pointer transition-colors {activePreset === preset ? 'border-primary bg-primary/10 text-primary font-bold' : 'border-border bg-card text-muted-foreground hover:bg-muted'}"
											onclick={() => {
												activePreset = preset;
												if (preset === "1:1") {
													const side = Math.min(originalWidth, originalHeight, cropWidth);
													cropWidth = side;
													cropHeight = side;
												} else if (preset === "4:3") {
													cropWidth = Math.min(originalWidth, Math.floor((originalHeight * 4) / 3));
													cropHeight = Math.floor((cropWidth * 3) / 4);
												} else if (preset === "16:9") {
													cropWidth = Math.min(originalWidth, Math.floor((originalHeight * 16) / 9));
													cropHeight = Math.floor((cropWidth * 9) / 16);
												}
												cropX = clamp(cropX, 0, originalWidth - cropWidth);
												cropY = clamp(cropY, 0, originalHeight - cropHeight);
											}}
										>
											{preset}
										</button>
									{/each}
								</div>
							</div>

							<!-- Quick Centering & Reset Actions -->
							<div class="flex items-center gap-2 pt-1">
								<Button
									variant="outline"
									size="xs"
									class="flex-1 text-xs gap-1"
									onclick={resetCropToCenter}
								>
									<CrosshairIcon class="size-3" />
									<span>Center Box</span>
								</Button>
								<Button
									variant="outline"
									size="xs"
									class="flex-1 text-xs"
									onclick={() => {
										cropX = 0;
										cropY = 0;
										cropWidth = originalWidth;
										cropHeight = originalHeight;
										activePreset = "Free";
									}}
								>
									<span>Fit Whole Image</span>
								</Button>
							</div>

							<!-- Grid Overlay Toggle -->
							<div class="flex items-center gap-2 pt-2 border-t border-border/70">
								<input
									id="crop-grid"
									type="checkbox"
									bind:checked={showRuleOfThirds}
									class="size-4 rounded-xs border-input text-primary accent-primary cursor-pointer"
								/>
								<label for="crop-grid" class="text-xs font-semibold text-foreground cursor-pointer select-none">
									Rule of Thirds Overlay
								</label>
							</div>
						</div>

					<!-- TAB PANEL: SHEAR (Mockup Match) -->
					{:else if activeTab === "shear"}
						<div class="space-y-4 pt-1">
							<div class="flex items-center justify-between">
								<h3 class="text-xs font-bold uppercase tracking-wider text-foreground">
									Shear (Affine transform)
								</h3>
							</div>

							<!-- Horizontal Shear X -->
							<div class="space-y-1.5">
								<div class="flex items-center justify-between text-xs">
									<label for="shear-x" class="font-semibold text-foreground">Horizontal Shear X</label>
									<span class="font-mono text-xs font-bold px-2 py-0.5 rounded-md border border-border bg-muted/40">
										{shearX.toFixed(2)}
									</span>
								</div>
								<input
									id="shear-x"
									type="range"
									min="-2.0"
									max="2.0"
									step="0.05"
									bind:value={shearX}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
								<div class="flex justify-between text-[10px] text-muted-foreground font-mono">
									<span>-2.0</span>
									<span>2.0</span>
								</div>
							</div>

							<!-- Vertical Shear Y -->
							<div class="space-y-1.5">
								<div class="flex items-center justify-between text-xs">
									<label for="shear-y" class="font-semibold text-foreground">Vertical Shear Y</label>
									<span class="font-mono text-xs font-bold px-2 py-0.5 rounded-md border border-border bg-muted/40">
										{shearY.toFixed(2)}
									</span>
								</div>
								<input
									id="shear-y"
									type="range"
									min="-2.0"
									max="2.0"
									step="0.05"
									bind:value={shearY}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
								<div class="flex justify-between text-[10px] text-muted-foreground font-mono">
									<span>-2.0</span>
									<span>2.0</span>
								</div>
							</div>

							<!-- Expand Canvas Checkbox -->
							<div class="flex items-center gap-2 pt-1">
								<input
									id="shear-expand"
									type="checkbox"
									bind:checked={shearExpand}
									class="size-4 rounded-xs border-input text-primary accent-primary cursor-pointer"
								/>
								<label for="shear-expand" class="text-xs font-semibold text-foreground cursor-pointer select-none">
									Expand Canvas
								</label>
							</div>

							<!-- Background Fill Color -->
							<div class="flex items-center justify-between pt-1">
								<span class="text-xs font-semibold text-foreground">Background Fill Color</span>
								<div class="flex items-center gap-2">
									<input
										type="color"
										bind:value={shearBgColor}
										class="size-6 rounded-md border border-border p-0 cursor-pointer overflow-hidden"
									/>
									<span class="text-xs font-mono text-muted-foreground uppercase">{shearBgColor}</span>
								</div>
							</div>

							<!-- View Transformation Params Button -->
							<button
								type="button"
								class="w-full py-2 flex items-center justify-between text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors border-t border-border/70 pt-3 cursor-pointer"
								onclick={() => (showParamsDialog = true)}
							>
								<span>Transformation Params</span>
								<ScanIcon class="size-3.5" />
							</button>
						</div>

					<!-- TAB PANEL: RESIZE -->
					{:else if activeTab === "resize"}
						<div class="space-y-4 pt-1">
							<h3 class="text-xs font-bold uppercase tracking-wider text-foreground">
								Scaling & Dimensions
							</h3>

							<div class="space-y-1.5">
								<div class="flex items-center justify-between text-xs">
									<label for="resize-scale" class="font-semibold text-foreground">Scale Multiplier</label>
									<span class="font-mono text-xs font-bold px-2 py-0.5 rounded-md border border-border bg-muted/40">
										{(resizeScale * 100).toFixed(0)}%
									</span>
								</div>
								<input
									id="resize-scale"
									type="range"
									min="0.1"
									max="2.0"
									step="0.05"
									bind:value={resizeScale}
									oninput={() => {
										resizeWidth = Math.round(originalWidth * resizeScale);
										resizeHeight = Math.round(originalHeight * resizeScale);
									}}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<div class="grid grid-cols-2 gap-3">
								<div class="space-y-1">
									<label for="resize-w" class="text-xs text-muted-foreground">Width (px)</label>
									<Input
										id="resize-w"
										type="number"
										bind:value={resizeWidth}
										oninput={() => {
											if (keepAspectRatio) {
												resizeHeight = Math.round((resizeWidth / originalWidth) * originalHeight);
											}
										}}
										class="h-8 text-xs font-mono"
									/>
								</div>
								<div class="space-y-1">
									<label for="resize-h" class="text-xs text-muted-foreground">Height (px)</label>
									<Input
										id="resize-h"
										type="number"
										bind:value={resizeHeight}
										oninput={() => {
											if (keepAspectRatio) {
												resizeWidth = Math.round((resizeHeight / originalHeight) * originalWidth);
											}
										}}
										class="h-8 text-xs font-mono"
									/>
								</div>
							</div>

							<div class="flex items-center gap-2 pt-1">
								<input
									id="resize-aspect"
									type="checkbox"
									bind:checked={keepAspectRatio}
									class="size-4 rounded-xs border-input text-primary accent-primary cursor-pointer"
								/>
								<label for="resize-aspect" class="text-xs font-semibold text-foreground cursor-pointer select-none">
									Lock Aspect Ratio ({originalWidth}:{originalHeight})
								</label>
							</div>
						</div>

					<!-- TAB PANEL: ROTATE -->
					{:else if activeTab === "rotate"}
						<div class="space-y-4 pt-1">
							<h3 class="text-xs font-bold uppercase tracking-wider text-foreground">
								Rotation & Orientation
							</h3>

							<div class="grid grid-cols-4 gap-2">
								{#each [-90, 90, 180, 0] as deg}
									<Button
										variant="outline"
										size="xs"
										class="h-8 text-xs font-mono"
										onclick={() => (rotateAngle = deg)}
									>
										{deg > 0 ? `+${deg}°` : `${deg}°`}
									</Button>
								{/each}
							</div>

							<div class="space-y-1.5">
								<div class="flex items-center justify-between text-xs">
									<label for="rotate-slider" class="font-semibold text-foreground">Custom Angle</label>
									<span class="font-mono text-xs font-bold px-2 py-0.5 rounded-md border border-border bg-muted/40">
										{rotateAngle}°
									</span>
								</div>
								<input
									id="rotate-slider"
									type="range"
									min="-180"
									max="180"
									step="1"
									bind:value={rotateAngle}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
								<div class="flex justify-between text-[10px] text-muted-foreground font-mono">
									<span>-180°</span>
									<span>0°</span>
									<span>+180°</span>
								</div>
							</div>

							<div class="flex items-center gap-2 pt-1">
								<input
									id="rotate-expand"
									type="checkbox"
									bind:checked={rotateExpand}
									class="size-4 rounded-xs border-input text-primary accent-primary cursor-pointer"
								/>
								<label for="rotate-expand" class="text-xs font-semibold text-foreground cursor-pointer select-none">
									Expand Canvas to Fit Rotation
								</label>
							</div>
						</div>

					<!-- TAB PANEL: FLIP -->
					{:else if activeTab === "flip"}
						<div class="space-y-4 pt-1">
							<h3 class="text-xs font-bold uppercase tracking-wider text-foreground">
								Mirror & Reflection
							</h3>

							<div class="grid grid-cols-2 gap-3">
								<button
									type="button"
									class="p-4 rounded-xl border flex flex-col items-center gap-2 transition-all cursor-pointer {flipDirection === 'horizontal' ? 'border-primary bg-primary/10 text-primary font-bold' : 'border-border bg-card text-muted-foreground hover:bg-muted'}"
									onclick={() => (flipDirection = "horizontal")}
								>
									<FlipHorizontalIcon class="size-6" />
									<span class="text-xs">Flip Horizontal</span>
								</button>

								<button
									type="button"
									class="p-4 rounded-xl border flex flex-col items-center gap-2 transition-all cursor-pointer {flipDirection === 'vertical' ? 'border-primary bg-primary/10 text-primary font-bold' : 'border-border bg-card text-muted-foreground hover:bg-muted'}"
									onclick={() => (flipDirection = "vertical")}
								>
									<FlipVerticalIcon class="size-6" />
									<span class="text-xs">Flip Vertical</span>
								</button>
							</div>
						</div>
					{/if}
				</Card.Content>
			</Card.Root>

			<!-- CARD 2: Saved Info (Mockup Bottom Right Card) -->
			<Card.Root class="border border-border shadow-xs">
				<Card.Header class="py-3 px-4 border-b border-border bg-card/60">
					<Card.Title class="text-sm font-bold tracking-tight text-foreground">
						Saved Info
					</Card.Title>
				</Card.Header>

				<Card.Content class="p-4 space-y-4">
					<!-- Derived Filename -->
					<div class="space-y-1.5">
						<label for="derived-name" class="text-xs font-semibold text-foreground flex items-center justify-between">
							<span>Derived Filename</span>
							<PencilIcon class="size-3 text-muted-foreground" />
						</label>
						<Input
							id="derived-name"
							type="text"
							bind:value={derivedFilename}
							placeholder="ghim_nature_peak_transformed.jpg"
							class="h-9 text-xs font-mono"
						/>
					</div>

					<!-- Target Category -->
					<div class="space-y-1.5">
						<label for="category-select" class="text-xs font-semibold text-foreground">
							Target Category
						</label>
						<select
							id="category-select"
							bind:value={selectedCategoryId}
							class="w-full h-9 rounded-md border border-input bg-card px-3 text-xs text-foreground shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
						>
							<option value="">Nature &gt; Landscapes &gt; Mountains</option>
							{#each categories as cat}
								<option value={cat.id}>{cat.name}</option>
							{/each}
						</select>
					</div>

					<!-- Lineage & Non-destructive Info (Exact Mockup Match) -->
					<div class="pt-2 border-t border-border/80">
						<p class="text-[11px] text-muted-foreground leading-relaxed">
							<strong class="text-foreground font-semibold">Lineage:</strong>
							Derived from <span class="font-mono text-foreground">{originalFilename}</span> &bull;
							users/{user?.email ? user.email.split("@")[0] : "zarqi_ezzoubair"}/ (Atomic UUID)
						</p>
					</div>

					<!-- Quick Action Buttons -->
					<div class="pt-1 flex items-center gap-2">
						<Button
							variant="outline"
							size="sm"
							class="flex-1 text-xs gap-1.5"
							disabled={isDownloading}
							onclick={handleDownloadImage}
						>
							<DownloadIcon class="size-3.5" />
							<span>Download</span>
						</Button>
						<Button
							size="sm"
							class="flex-1 text-xs gap-1.5"
							disabled={isSaving || !activeTab}
							onclick={handleSaveDerivedImage}
						>
							{#if isSaving}
								<Loader2Icon class="size-3.5 animate-spin" />
								<span>Saving...</span>
							{:else}
								<PencilIcon class="size-3.5" />
								<span>Save</span>
							{/if}
						</Button>
					</div>
				</Card.Content>
			</Card.Root>
		</div>
	</div>
</div>

<!-- ========================================================================= -->
<!-- 3. IMAGE PICKER DIALOG                                                    -->
<!-- ========================================================================= -->
<Dialog.Root bind:open={isImagePickerOpen}>
	<Dialog.Content class="max-w-2xl">
		<Dialog.Header>
			<Dialog.Title class="text-base font-bold">Select Image to Transform</Dialog.Title>
			<Dialog.Description class="text-xs text-muted-foreground">
				Choose any image from your dataset or reference archive to open in the Transformation Studio.
			</Dialog.Description>
		</Dialog.Header>

		<div class="py-4">
			{#if userImages.length === 0}
				<div class="text-center py-8 space-y-3">
					<ImageIcon class="size-8 mx-auto text-muted-foreground opacity-50" />
					<p class="text-xs text-muted-foreground">No custom uploaded images found in your gallery.</p>
					<Button
						variant="outline"
						size="sm"
						onclick={() => {
							originalFilename = "ghim_nature_peak.jpg";
							originalWidth = 1920;
							originalHeight = 1080;
							currentImageUrl = "/images/auth-hero.jpg";
							resetCropToCenter();
							isImagePickerOpen = false;
						}}
					>
						Load GHIM-10K Sample Mountain Peak
					</Button>
				</div>
			{:else}
				<div class="grid grid-cols-3 sm:grid-cols-4 gap-3 max-h-[360px] overflow-y-auto p-1">
					{#each userImages as img}
						<button
							type="button"
							class="group relative aspect-4/3 rounded-lg border overflow-hidden cursor-pointer transition-all hover:ring-2 hover:ring-primary {currentImage?.id === img.id ? 'ring-2 ring-primary border-primary' : 'border-border'}"
							onclick={() => selectImage(img)}
						>
							<img
								src={imageService.getImageFileUrl(img.id)}
								alt={img.filename}
								class="size-full object-cover group-hover:scale-105 transition-transform"
							/>
							<div class="absolute inset-x-0 bottom-0 bg-background/90 backdrop-blur-xs p-1 text-[10px] truncate text-center font-mono">
								{img.filename}
							</div>
						</button>
					{/each}
				</div>
			{/if}
		</div>

		<Dialog.Footer class="flex justify-between items-center sm:justify-between">
			<Button href="/dashboard/upload" variant="outline" size="sm" class="text-xs gap-1.5">
				Upload New Image
				<ExternalLinkIcon class="size-3" />
			</Button>
			<Button variant="ghost" size="sm" onclick={() => (isImagePickerOpen = false)}>
				Cancel
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>

<!-- ========================================================================= -->
<!-- 4. TRANSFORMATION PARAMS RAW MODAL                                        -->
<!-- ========================================================================= -->
<Dialog.Root bind:open={showParamsDialog}>
	<Dialog.Content class="max-w-md">
		<Dialog.Header>
			<Dialog.Title class="text-sm font-bold flex items-center gap-2">
				<CodeIcon class="size-4 text-primary" />
				Transformation Parameters Matrix
			</Dialog.Title>
			<Dialog.Description class="text-xs text-muted-foreground">
				JSON representation passed to the deterministic TransformEngine backend pipeline.
			</Dialog.Description>
		</Dialog.Header>

		<div class="py-2">
			<pre class="p-3 rounded-lg bg-muted text-foreground text-xs font-mono overflow-x-auto border border-border">
{JSON.stringify(
	{
		operation: activeTab || "none",
		params: activeParamsJson,
		dimensions: {
			original: `${originalWidth}x${originalHeight}`,
			computed_output: `${computedOutputWidth}x${computedOutputHeight}`
		}
	},
	null,
	2
)}
			</pre>
		</div>

		<Dialog.Footer>
			<Button size="sm" class="text-xs" onclick={() => (showParamsDialog = false)}>
				Close
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
