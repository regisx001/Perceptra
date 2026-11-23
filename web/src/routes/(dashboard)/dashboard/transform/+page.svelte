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
	import * as Dialog from "#lib/components/ui/dialog/index.js";
	import * as Select from "#lib/components/ui/select/index.js";
	import { Badge } from "#lib/components/ui/badge/index.js";
	import HeaderActionPortal from "#lib/components/header-action-portal.svelte";

	// Icons
	import CropIcon from "@lucide/svelte/icons/crop";
	import Maximize2Icon from "@lucide/svelte/icons/maximize-2";
	import RotateCwIcon from "@lucide/svelte/icons/rotate-cw";
	import RotateCcwIcon from "@lucide/svelte/icons/rotate-ccw";
	import SlidersHorizontalIcon from "@lucide/svelte/icons/sliders-horizontal";
	import RectangleHorizontalIcon from "@lucide/svelte/icons/rectangle-horizontal";
	import TriangleIcon from "@lucide/svelte/icons/triangle";
	import Undo2Icon from "@lucide/svelte/icons/undo-2";
	import Redo2Icon from "@lucide/svelte/icons/redo-2";
	import MinusIcon from "@lucide/svelte/icons/minus";
	import PlusIcon from "@lucide/svelte/icons/plus";
	import CrosshairIcon from "@lucide/svelte/icons/crosshair";
	import ScanIcon from "@lucide/svelte/icons/scan";
	import MaximizeIcon from "@lucide/svelte/icons/maximize";
	import LinkIcon from "@lucide/svelte/icons/link";
	import UnlinkIcon from "@lucide/svelte/icons/unlink";
	import ArrowRightIcon from "@lucide/svelte/icons/arrow-right";
	import UploadCloudIcon from "@lucide/svelte/icons/upload-cloud";
	import DownloadIcon from "@lucide/svelte/icons/download";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import ExternalLinkIcon from "@lucide/svelte/icons/external-link";
	import FlipHorizontalIcon from "@lucide/svelte/icons/flip-horizontal";
	import FlipVerticalIcon from "@lucide/svelte/icons/flip-vertical";
	import SunIcon from "@lucide/svelte/icons/sun";
	import PaletteIcon from "@lucide/svelte/icons/palette";
	import SparklesIcon from "@lucide/svelte/icons/sparkles";
	import LayersIcon from "@lucide/svelte/icons/layers";
	import EyeIcon from "@lucide/svelte/icons/eye";
	import XIcon from "@lucide/svelte/icons/x";
	import type { PhotoAdjustments } from "#lib/images.js";

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
	let isUploadDialogOpen = $state(false);
	let showParamsDialog = $state(false);

	// Upload Dialog State
	let uploadFile = $state<File | null>(null);
	let uploadPreviewUrl = $state<string | null>(null);
	let uploadCategoryId = $state<string>("");
	let isUploadingImage = $state(false);
	let uploadError = $state<string | null>(null);
	let uploadProgress = $state<number>(0);
	let isDraggingFile = $state(false);
	let uploadFileInputRef: HTMLInputElement | null = null;

	// Currently Active Image
	let currentImage = $state<ImageItem | null>(null);
	let currentImageUrl = $state<string>("/images/auth-hero.jpg");
	let originalWidth = $state<number>(2048);
	let originalHeight = $state<number>(1365);
	let originalFileSize = $state<number>(1420580);
	let originalMimeType = $state<string>("image/jpeg");
	let originalFilename = $state<string>("chair_01.jpg");
	let imageEl = $state<HTMLImageElement | null>(null);

	// Active Transform Operation - Concept 2 defaults to "crop"
	type TransformOp =
		| "crop"
		| "resize"
		| "rotate"
		| "flip"
		| "shear"
		| "affine"
		| "light"
		| "color"
		| "detail";
	let activeTab = $state<TransformOp>("crop");

	// Preview Controls
	let zoomLevel = $state<number>(100);
	let activePreset = $state<string>("1:1 (Square)");

	// 1. Interactive Crop Parameters (8-point control system)
	let cropX = $state<number>(512);
	let cropY = $state<number>(240);
	let cropWidth = $state<number>(1024);
	let cropHeight = $state<number>(1024);
	let showRuleOfThirds = $state<boolean>(true);

	// Interactive Crop Drag State
	let activeCropDrag = $state<string | null>(null);
	let dragStartPointer = { x: 0, y: 0 };
	let dragStartCrop = { x: 0, y: 0, w: 0, h: 0 };

	// History Stack for Snappy Undo / Redo
	let cropHistory = $state<{ x: number; y: number; w: number; h: number }[]>([
		{ x: 512, y: 240, w: 1024, h: 1024 },
	]);
	let cropHistoryIndex = $state(0);

	// 2. Shear Parameters
	let shearX = $state<number>(0.25);
	let shearY = $state<number>(0.0);
	let shearExpand = $state<boolean>(true);
	let shearBgColor = $state<string>("#FFFFFF");

	// 2b. Affine Parameters [a, b, c, d, e, f]
	// [ x' ]   [ a  b ] [ x ]   [ c ]
	// [ y' ] = [ d  e ] [ y ] + [ f ]
	let affineA = $state<number>(1.0); // Scale X
	let affineB = $state<number>(0.0); // Shear X
	let affineC = $state<number>(0.0); // Translation X (px)
	let affineD = $state<number>(0.0); // Shear Y
	let affineE = $state<number>(1.0); // Scale Y
	let affineF = $state<number>(0.0); // Translation Y (px)
	let affineExpand = $state<boolean>(true);
	let affineBgColor = $state<string>("#FFFFFF");

	// 3. Resize Parameters
	let resizeScale = $state<number>(1.0);
	let resizeWidth = $state<number>(1024);
	let resizeHeight = $state<number>(1024);
	let keepAspectRatio = $state<boolean>(true);

	// 4. Rotate Parameters
	let rotateAngle = $state<number>(0);
	let rotateExpand = $state<boolean>(true);
	let rotateBgColor = $state<string>("#FFFFFF");

	// 5. Flip Parameters
	let flipDirection = $state<"horizontal" | "vertical">("horizontal");

	// 6. Photographic Adjustments
	// Light
	let adjBrightness = $state<number>(0);
	let adjContrast = $state<number>(0);
	let adjExposure = $state<number>(0);
	let adjHighlights = $state<number>(0);
	let adjShadows = $state<number>(0);
	let adjWhites = $state<number>(0);
	let adjBlacks = $state<number>(0);

	// Color
	let adjSaturation = $state<number>(0);
	let adjVibrance = $state<number>(0);
	let adjHue = $state<number>(0);
	let adjTemperature = $state<number>(0);
	let adjTint = $state<number>(0);

	// Detail
	let adjSharpness = $state<number>(0);
	let adjClarity = $state<number>(0);
	let adjBlur = $state<number>(0);

	// A/B Comparison state
	let isComparing = $state<boolean>(false);

	// Multi-step transformation pipeline stack
	interface StackStep {
		id: string;
		operation: string;
		description: string;
		params: Record<string, any>;
	}
	let appliedStack = $state<StackStep[]>([]);

	// Active adjustment counters
	let activeLightCount = $derived.by(() => {
		let c = 0;
		if (adjBrightness !== 0) c++;
		if (adjContrast !== 0) c++;
		if (adjExposure !== 0) c++;
		if (adjHighlights !== 0) c++;
		if (adjShadows !== 0) c++;
		if (adjWhites !== 0) c++;
		if (adjBlacks !== 0) c++;
		return c;
	});

	let activeColorCount = $derived.by(() => {
		let c = 0;
		if (adjSaturation !== 0) c++;
		if (adjVibrance !== 0) c++;
		if (adjHue !== 0) c++;
		if (adjTemperature !== 0) c++;
		if (adjTint !== 0) c++;
		return c;
	});

	let activeDetailCount = $derived.by(() => {
		let c = 0;
		if (adjSharpness !== 0) c++;
		if (adjClarity !== 0) c++;
		if (adjBlur !== 0) c++;
		return c;
	});

	let totalActiveAdjustments = $derived.by(
		() => activeLightCount + activeColorCount + activeDetailCount,
	);

	let currentAdjustments = $derived.by((): PhotoAdjustments => {
		return {
			brightness: adjBrightness,
			contrast: adjContrast,
			exposure: adjExposure,
			highlights: adjHighlights,
			shadows: adjShadows,
			whites: adjWhites,
			blacks: adjBlacks,
			saturation: adjSaturation,
			vibrance: adjVibrance,
			hue: adjHue,
			temperature: adjTemperature,
			tint: adjTint,
			sharpness: adjSharpness,
			clarity: adjClarity,
			blur: adjBlur,
		};
	});

	// Real-time CSS Filter preview for center viewport
	let liveFilterStyle = $derived.by(() => {
		if (isComparing || totalActiveAdjustments === 0) return "";
		const brightFactor =
			(1 + adjBrightness / 100) * Math.pow(2, adjExposure / 50);
		const contrastFactor = 1 + adjContrast / 100;
		const satFactor = (1 + adjSaturation / 100) * (1 + adjVibrance / 150);
		const blurPx = adjBlur;
		const hueDeg = adjHue;
		const sepiaFactor = adjTemperature > 0 ? adjTemperature / 200 : 0;
		return `filter: brightness(${brightFactor}) contrast(${contrastFactor}) saturate(${satFactor}) hue-rotate(${hueDeg}deg) blur(${blurPx}px) sepia(${sepiaFactor});`;
	});

	function resetLightAdjustments() {
		adjBrightness = 0;
		adjContrast = 0;
		adjExposure = 0;
		adjHighlights = 0;
		adjShadows = 0;
		adjWhites = 0;
		adjBlacks = 0;
	}

	function resetColorAdjustments() {
		adjSaturation = 0;
		adjVibrance = 0;
		adjHue = 0;
		adjTemperature = 0;
		adjTint = 0;
	}

	function resetDetailAdjustments() {
		adjSharpness = 0;
		adjClarity = 0;
		adjBlur = 0;
	}

	function resetAllAdjustments() {
		resetLightAdjustments();
		resetColorAdjustments();
		resetDetailAdjustments();
	}

	function handleStackCurrentStep() {
		let stepOp = activeTab as string;
		let stepDesc = "";
		let stepParams: Record<string, any> = {};

		if (
			activeTab === "light" ||
			activeTab === "color" ||
			activeTab === "detail"
		) {
			if (totalActiveAdjustments === 0) return;
			stepOp = "adjust";
			stepDesc = `Adjustments (${totalActiveAdjustments} active)`;
			stepParams = { adjustments: { ...currentAdjustments } };
			resetAllAdjustments();
		} else {
			stepDesc = `${activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}`;
			stepParams = { ...activeParamsJson };
			if (totalActiveAdjustments > 0) {
				stepParams.adjustments = { ...currentAdjustments };
				resetAllAdjustments();
			}
		}

		appliedStack = [
			...appliedStack,
			{
				id: "step-" + Math.random().toString(36).substring(2, 7),
				operation: stepOp,
				description: stepDesc,
				params: stepParams,
			},
		];
	}

	function removeStackStep(index: number) {
		appliedStack = appliedStack.filter((_, i) => i !== index);
	}

	function clearStack() {
		appliedStack = [];
	}

	// Saved Info
	let derivedFilename = $state<string>("chair_01_cropped.jpg");
	let selectedCategoryId = $state<string>("");

	// Helpers
	function clamp(val: number, min: number, max: number): number {
		return Math.max(min, Math.min(max, val));
	}

	function formatFileSize(bytes: number): string {
		if (!bytes || bytes <= 0) return "0 B";
		const k = 1024;
		if (bytes < k) return `${bytes} B`;
		if (bytes < k * k) return `${(bytes / k).toFixed(1)} KB`;
		return `${(bytes / (k * k)).toFixed(1)} MB`;
	}

	let displayFormat = $derived.by(() => {
		if (originalMimeType && originalMimeType.includes("/")) {
			const sub = originalMimeType.split("/")[1];
			return sub.toUpperCase();
		}
		if (originalFilename.includes(".")) {
			return originalFilename.split(".").pop()?.toUpperCase() || "IMAGE";
		}
		return "JPEG";
	});

	let estimatedDerivedBytes = $derived.by(() => {
		if (!originalWidth || !originalHeight || originalWidth <= 0 || originalHeight <= 0) {
			return 0;
		}
		const originalPixels = originalWidth * originalHeight;
		const outputPixels = computedOutputWidth * computedOutputHeight;
		const ratio = outputPixels / originalPixels;

		if (originalFileSize > 0) {
			return Math.max(512, Math.round(originalFileSize * ratio));
		}
		return Math.max(512, Math.round(outputPixels * 0.25));
	});

	function pushCropHistory() {
		if (cropHistoryIndex < cropHistory.length - 1) {
			cropHistory = cropHistory.slice(0, cropHistoryIndex + 1);
		}
		cropHistory.push({ x: cropX, y: cropY, w: cropWidth, h: cropHeight });
		if (cropHistory.length > 40) cropHistory.shift();
		cropHistoryIndex = cropHistory.length - 1;
	}

	function undoCrop() {
		if (cropHistoryIndex > 0) {
			cropHistoryIndex--;
			const s = cropHistory[cropHistoryIndex];
			cropX = s.x;
			cropY = s.y;
			cropWidth = s.w;
			cropHeight = s.h;
		}
	}

	function redoCrop() {
		if (cropHistoryIndex < cropHistory.length - 1) {
			cropHistoryIndex++;
			const s = cropHistory[cropHistoryIndex];
			cropX = s.x;
			cropY = s.y;
			cropWidth = s.w;
			cropHeight = s.h;
		}
	}

	// Computed dynamic output dimensions
	let computedOutputWidth = $derived.by(() => {
		if (!activeTab || activeTab === "crop") {
			return Math.min(originalWidth, Math.max(1, Math.round(cropWidth)));
		} else if (activeTab === "shear") {
			if (!shearExpand) return originalWidth;
			const corners = [
				[0, 0],
				[originalWidth, 0],
				[0, originalHeight],
				[originalWidth, originalHeight],
			];
			const transX = corners.map(([x, y]) => x + shearX * y);
			return Math.max(
				1,
				Math.round(Math.max(...transX) - Math.min(...transX)),
			);
		} else if (activeTab === "affine") {
			if (!affineExpand) return originalWidth;
			const corners = [
				[0, 0],
				[originalWidth, 0],
				[0, originalHeight],
				[originalWidth, originalHeight],
			];
			const transX = corners.map(
				([x, y]) => affineA * x + affineB * y + affineC,
			);
			return Math.max(
				1,
				Math.round(Math.max(...transX) - Math.min(...transX)),
			);
		} else if (activeTab === "resize") {
			return Math.max(1, Math.round(resizeWidth));
		} else if (activeTab === "rotate") {
			if (!rotateExpand || rotateAngle === 0) return originalWidth;
			const rad = Math.abs(rotateAngle) * (Math.PI / 180);
			return Math.max(
				1,
				Math.round(
					originalWidth * Math.abs(Math.cos(rad)) +
						originalHeight * Math.abs(Math.sin(rad)),
				),
			);
		} else {
			return originalWidth;
		}
	});

	let computedOutputHeight = $derived.by(() => {
		if (!activeTab || activeTab === "crop") {
			return Math.min(
				originalHeight,
				Math.max(1, Math.round(cropHeight)),
			);
		} else if (activeTab === "shear") {
			if (!shearExpand) return originalHeight;
			const corners = [
				[0, 0],
				[originalWidth, 0],
				[0, originalHeight],
				[originalWidth, originalHeight],
			];
			const transY = corners.map(([x, y]) => shearY * x + y);
			return Math.max(
				1,
				Math.round(Math.max(...transY) - Math.min(...transY)),
			);
		} else if (activeTab === "affine") {
			if (!affineExpand) return originalHeight;
			const corners = [
				[0, 0],
				[originalWidth, 0],
				[0, originalHeight],
				[originalWidth, originalHeight],
			];
			const transY = corners.map(
				([x, y]) => affineD * x + affineE * y + affineF,
			);
			return Math.max(
				1,
				Math.round(Math.max(...transY) - Math.min(...transY)),
			);
		} else if (activeTab === "resize") {
			return Math.max(1, Math.round(resizeHeight));
		} else if (activeTab === "rotate") {
			if (!rotateExpand || rotateAngle === 0) return originalHeight;
			const rad = Math.abs(rotateAngle) * (Math.PI / 180);
			return Math.max(
				1,
				Math.round(
					originalWidth * Math.abs(Math.sin(rad)) +
						originalHeight * Math.abs(Math.cos(rad)),
				),
			);
		} else {
			return originalHeight;
		}
	});

	// Dynamic derived filename generator
	$effect(() => {
		const stem = originalFilename.replace(/\.[^/.]+$/, "");
		const ext = originalFilename.includes(".")
			? "." + originalFilename.split(".").pop()
			: ".jpg";
		if (appliedStack.length > 0) {
			derivedFilename = `${stem}_pipelined_${appliedStack.length}steps${ext}`;
		} else if (activeTab === "crop") {
			derivedFilename = `${stem}_cropped${ext}`;
		} else if (activeTab === "shear") {
			derivedFilename = `${stem}_sheared${ext}`;
		} else if (activeTab === "affine") {
			derivedFilename = `${stem}_affine${ext}`;
		} else if (activeTab === "resize") {
			derivedFilename = `${stem}_resized${ext}`;
		} else if (activeTab === "rotate") {
			derivedFilename = `${stem}_rotated${ext}`;
		} else if (activeTab === "flip") {
			derivedFilename = `${stem}_flipped_${flipDirection}${ext}`;
		} else if (
			activeTab === "light" ||
			activeTab === "color" ||
			activeTab === "detail"
		) {
			derivedFilename = `${stem}_adjusted${ext}`;
		} else {
			derivedFilename = `${stem}_transformed${ext}`;
		}
	});

	// Active Params Object for API payload
	let activeParamsJson = $derived.by(() => {
		if (activeTab === "crop") {
			return {
				x: Math.max(0, Math.floor(cropX)),
				y: Math.max(0, Math.floor(cropY)),
				width: Math.max(1, Math.floor(cropWidth)),
				height: Math.max(1, Math.floor(cropHeight)),
			};
		} else if (activeTab === "shear") {
			return {
				shear_x: Number(shearX),
				shear_y: Number(shearY),
				expand: shearExpand,
				bg_color: shearBgColor,
			};
		} else if (activeTab === "affine") {
			return {
				matrix: [
					Number(affineA),
					Number(affineB),
					Number(affineC),
					Number(affineD),
					Number(affineE),
					Number(affineF),
				],
				expand: affineExpand,
				bg_color: affineBgColor,
			};
		} else if (activeTab === "resize") {
			return {
				width: Math.max(1, Math.floor(resizeWidth)),
				height: Math.max(1, Math.floor(resizeHeight)),
				keep_aspect_ratio: keepAspectRatio,
			};
		} else if (activeTab === "rotate") {
			return {
				angle: Number(rotateAngle),
				expand: rotateExpand,
				bg_color: rotateBgColor,
			};
		} else if (activeTab === "flip") {
			return {
				direction: flipDirection,
			};
		} else {
			return {
				adjustments: { ...currentAdjustments },
			};
		}
	});

	onMount(async () => {
		try {
			const [imgList, catList] = await Promise.allSettled([
				imageService.listImages({ per_page: 50 }),
				categoryService.getCategories({ tree: true }),
			]);

			if (catList.status === "fulfilled") {
				categories = catList.value;
			}

			if (
				imgList.status === "fulfilled" &&
				imgList.value.images.length > 0
			) {
				userImages = imgList.value.images;
				const queryImageId = page.url.searchParams.get("image_id");
				const found = queryImageId
					? userImages.find((img) => img.id === queryImageId)
					: userImages[0];

				if (found) {
					selectImage(found);
				}
			} else {
				originalFilename = "chair_01.jpg";
				originalWidth = 2048;
				originalHeight = 1365;
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
		if (uploadPreviewUrl) {
			URL.revokeObjectURL(uploadPreviewUrl);
		}
	});

	function selectImage(img: ImageItem) {
		currentImage = img;
		originalFilename = img.filename;
		originalWidth = img.width || 2048;
		originalHeight = img.height || 1365;
		originalFileSize = img.file_size || 0;
		originalMimeType = img.mime_type || "image/jpeg";
		currentImageUrl = imageService.getImageFileUrl(img.id);
		resetCropToCenter();
		resizeWidth = originalWidth;
		resizeHeight = originalHeight;
		if (img.category_id) {
			selectedCategoryId = String(img.category_id);
		}
	}

	function handleFileSelected(file: File) {
		if (!file.type.startsWith("image/")) {
			uploadError =
				"Please select a valid image file (PNG, JPG, WEBP, etc.)";
			return;
		}
		uploadError = null;
		uploadFile = file;
		uploadProgress = 0;
		if (uploadPreviewUrl) {
			URL.revokeObjectURL(uploadPreviewUrl);
		}
		uploadPreviewUrl = URL.createObjectURL(file);
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		isDraggingFile = false;
		if (e.dataTransfer && e.dataTransfer.files.length > 0) {
			handleFileSelected(e.dataTransfer.files[0]);
		}
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		isDraggingFile = true;
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		isDraggingFile = false;
	}

	async function submitUpload() {
		if (!uploadFile) return;

		isUploadingImage = true;
		uploadError = null;
		uploadProgress = 10;

		try {
			const imgObj = new Image();
			const naturalDimsPromise = new Promise<{
				width: number;
				height: number;
			}>((resolve) => {
				imgObj.onload = () => {
					resolve({
						width: imgObj.naturalWidth || 2048,
						height: imgObj.naturalHeight || 1365,
					});
				};
				imgObj.onerror = () => {
					resolve({ width: 2048, height: 1365 });
				};
			});
			if (uploadPreviewUrl) {
				imgObj.src = uploadPreviewUrl;
			}

			let uploaded: ImageItem | null = null;
			try {
				uploaded = await imageService.uploadImage(
					uploadFile,
					uploadCategoryId || null,
					(p) => (uploadProgress = Math.max(10, p)),
				);
			} catch (err: any) {
				console.warn(
					"Backend upload failed, loading local image in studio:",
					err,
				);
			}

			const dims = await naturalDimsPromise;

			if (uploaded) {
				currentImage = uploaded;
				originalFilename = uploaded.filename;
				originalWidth = uploaded.width || dims.width;
				originalHeight = uploaded.height || dims.height;
				originalFileSize = uploaded.file_size || uploadFile.size;
				originalMimeType = uploaded.mime_type || uploadFile.type || "image/jpeg";
				currentImageUrl = imageService.getImageFileUrl(uploaded.id);
			} else {
				originalFilename = uploadFile.name;
				originalWidth = dims.width;
				originalHeight = dims.height;
				originalFileSize = uploadFile.size;
				originalMimeType = uploadFile.type || "image/jpeg";
				currentImageUrl =
					uploadPreviewUrl || URL.createObjectURL(uploadFile);
			}

			resetCropToCenter();
			resizeWidth = originalWidth;
			resizeHeight = originalHeight;
			resetCanvas();
			isUploadDialogOpen = false;
			uploadFile = null;
			uploadProgress = 0;
		} catch (err: any) {
			uploadError = err.message || "Failed to process image upload.";
		} finally {
			isUploadingImage = false;
		}
	}

	function resetCropToCenter() {
		cropWidth = Math.min(
			originalWidth,
			Math.max(100, Math.floor(originalWidth * 0.5)),
		);
		cropHeight = Math.min(
			originalHeight,
			Math.max(100, Math.floor(originalHeight * 0.5)),
		);
		cropX = Math.floor((originalWidth - cropWidth) / 2);
		cropY = Math.floor((originalHeight - cropHeight) / 2);
		pushCropHistory();
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

	// 8 Precise Control Points for the Crop Box
	const cropHandles = [
		{
			id: "nw",
			label: "Top-Left",
			cursor: "nwse-resize",
			positionStyle: "top: 0; left: 0; transform: translate(-50%, -50%);",
			isCorner: true,
		},
		{
			id: "n",
			label: "Top-Center",
			cursor: "ns-resize",
			positionStyle:
				"top: 0; left: 50%; transform: translate(-50%, -50%);",
			isCorner: false,
		},
		{
			id: "ne",
			label: "Top-Right",
			cursor: "nesw-resize",
			positionStyle: "top: 0; right: 0; transform: translate(50%, -50%);",
			isCorner: true,
		},
		{
			id: "e",
			label: "Middle-Right",
			cursor: "ew-resize",
			positionStyle:
				"top: 50%; right: 0; transform: translate(50%, -50%);",
			isCorner: false,
		},
		{
			id: "se",
			label: "Bottom-Right",
			cursor: "nwse-resize",
			positionStyle:
				"bottom: 0; right: 0; transform: translate(50%, 50%);",
			isCorner: true,
		},
		{
			id: "s",
			label: "Bottom-Center",
			cursor: "ns-resize",
			positionStyle:
				"bottom: 0; left: 50%; transform: translate(-50%, 50%);",
			isCorner: false,
		},
		{
			id: "sw",
			label: "Bottom-Left",
			cursor: "nesw-resize",
			positionStyle:
				"bottom: 0; left: 0; transform: translate(-50%, 50%);",
			isCorner: true,
		},
		{
			id: "w",
			label: "Middle-Left",
			cursor: "ew-resize",
			positionStyle:
				"top: 50%; left: 0; transform: translate(-50%, -50%);",
			isCorner: false,
		},
	];

	const cropCursorMap: Record<string, string> = {
		nw: "nwse-resize",
		n: "ns-resize",
		ne: "nesw-resize",
		e: "ew-resize",
		se: "nwse-resize",
		s: "ns-resize",
		sw: "nesw-resize",
		w: "ew-resize",
		move: "move",
	};

	function handleCropPointerDown(handle: string, e: PointerEvent) {
		e.preventDefault();
		e.stopPropagation();
		activeCropDrag = handle;
		dragStartPointer = { x: e.clientX, y: e.clientY };
		dragStartCrop = { x: cropX, y: cropY, w: cropWidth, h: cropHeight };

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
			cropX = clamp(
				dragStartCrop.x + deltaX,
				0,
				originalWidth - cropWidth,
			);
			cropY = clamp(
				dragStartCrop.y + deltaY,
				0,
				originalHeight - cropHeight,
			);
		} else if (activeCropDrag === "se") {
			cropWidth = clamp(
				dragStartCrop.w + deltaX,
				20,
				originalWidth - dragStartCrop.x,
			);
			cropHeight = clamp(
				dragStartCrop.h + deltaY,
				20,
				originalHeight - dragStartCrop.y,
			);
		} else if (activeCropDrag === "e") {
			cropWidth = clamp(
				dragStartCrop.w + deltaX,
				20,
				originalWidth - dragStartCrop.x,
			);
		} else if (activeCropDrag === "s") {
			cropHeight = clamp(
				dragStartCrop.h + deltaY,
				20,
				originalHeight - dragStartCrop.y,
			);
		} else if (activeCropDrag === "nw") {
			const newX = clamp(
				dragStartCrop.x + deltaX,
				0,
				dragStartCrop.x + dragStartCrop.w - 20,
			);
			const newY = clamp(
				dragStartCrop.y + deltaY,
				0,
				dragStartCrop.y + dragStartCrop.h - 20,
			);
			cropWidth = dragStartCrop.w + (dragStartCrop.x - newX);
			cropHeight = dragStartCrop.h + (dragStartCrop.y - newY);
			cropX = newX;
			cropY = newY;
		} else if (activeCropDrag === "ne") {
			const newY = clamp(
				dragStartCrop.y + deltaY,
				0,
				dragStartCrop.y + dragStartCrop.h - 20,
			);
			cropWidth = clamp(
				dragStartCrop.w + deltaX,
				20,
				originalWidth - dragStartCrop.x,
			);
			cropHeight = dragStartCrop.h + (dragStartCrop.y - newY);
			cropY = newY;
		} else if (activeCropDrag === "sw") {
			const newX = clamp(
				dragStartCrop.x + deltaX,
				0,
				dragStartCrop.x + dragStartCrop.w - 20,
			);
			cropWidth = dragStartCrop.w + (dragStartCrop.x - newX);
			cropHeight = clamp(
				dragStartCrop.h + deltaY,
				20,
				originalHeight - dragStartCrop.y,
			);
			cropX = newX;
		} else if (activeCropDrag === "n") {
			const newY = clamp(
				dragStartCrop.y + deltaY,
				0,
				dragStartCrop.y + dragStartCrop.h - 20,
			);
			cropHeight = dragStartCrop.h + (dragStartCrop.y - newY);
			cropY = newY;
		} else if (activeCropDrag === "w") {
			const newX = clamp(
				dragStartCrop.x + deltaX,
				0,
				dragStartCrop.x + dragStartCrop.w - 20,
			);
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
		pushCropHistory();
	}

	// Presets & Quick Actions
	function applyPreset(preset: string) {
		activePreset = preset;
		if (
			preset === "1:1 (Square)" ||
			preset === "Square (1:1)" ||
			preset === "1:1"
		) {
			const side = Math.min(originalWidth, originalHeight, cropWidth);
			cropWidth = side;
			cropHeight = side;
		} else if (preset === "Landscape (16:9)" || preset === "16:9") {
			cropWidth = Math.min(
				originalWidth,
				Math.floor((originalHeight * 16) / 9),
			);
			cropHeight = Math.floor((cropWidth * 9) / 16);
		} else if (preset === "Portrait (9:16)" || preset === "9:16") {
			cropHeight = Math.min(
				originalHeight,
				Math.floor((originalWidth * 16) / 9),
			);
			cropWidth = Math.floor((cropHeight * 9) / 16);
		} else if (preset === "4:3") {
			cropWidth = Math.min(
				originalWidth,
				Math.floor((originalHeight * 4) / 3),
			);
			cropHeight = Math.floor((cropWidth * 3) / 4);
		} else if (preset === "Original") {
			cropWidth = originalWidth;
			cropHeight = originalHeight;
			cropX = 0;
			cropY = 0;
			pushCropHistory();
			return;
		}
		cropX = clamp(cropX, 0, originalWidth - cropWidth);
		cropY = clamp(cropY, 0, originalHeight - cropHeight);
		pushCropHistory();
	}

	function centerCrop() {
		cropX = Math.floor((originalWidth - cropWidth) / 2);
		cropY = Math.floor((originalHeight - cropHeight) / 2);
		pushCropHistory();
	}

	function fitToImage() {
		cropX = 0;
		cropY = 0;
		cropWidth = originalWidth;
		cropHeight = originalHeight;
		activePreset = "Original";
		pushCropHistory();
	}

	function fillCrop() {
		const aspect = cropWidth / cropHeight;
		if (originalWidth / originalHeight > aspect) {
			cropHeight = originalHeight;
			cropWidth = Math.round(cropHeight * aspect);
		} else {
			cropWidth = originalWidth;
			cropHeight = Math.round(cropWidth / aspect);
		}
		centerCrop();
	}

	function resetCrop() {
		resetCropToCenter();
		activePreset = "1:1 (Square)";
	}

	function handleWidthInput() {
		cropWidth = clamp(cropWidth, 10, originalWidth);
		if (keepAspectRatio) {
			const ratio = originalWidth / originalHeight;
			cropHeight = clamp(
				Math.round(cropWidth / ratio),
				10,
				originalHeight,
			);
		}
		if (cropX + cropWidth > originalWidth) {
			cropX = originalWidth - cropWidth;
		}
		pushCropHistory();
	}

	function handleHeightInput() {
		cropHeight = clamp(cropHeight, 10, originalHeight);
		if (keepAspectRatio) {
			const ratio = originalWidth / originalHeight;
			cropWidth = clamp(
				Math.round(cropHeight * ratio),
				10,
				originalWidth,
			);
		}
		if (cropY + cropHeight > originalHeight) {
			cropY = originalHeight - cropHeight;
		}
		pushCropHistory();
	}

	function resetCanvas() {
		activeTab = "crop";
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
		zoomLevel = 100;
		activePreset = "1:1 (Square)";
		resetAllAdjustments();
		clearStack();
	}

	async function handleSaveDerivedImage() {
		isSaving = true;
		errorMessage = null;
		saveSuccessImage = null;

		try {
			let targetOp = activeTab as string;
			let targetParams: Record<string, any> = { ...activeParamsJson };

			if (appliedStack.length > 0) {
				targetOp = "pipeline";
				const steps = appliedStack.map((s) => ({
					operation: s.operation,
					params: s.params,
				}));

				// If there are unstacked adjustments or transforms, add them as the last step
				if (
					activeTab === "light" ||
					activeTab === "color" ||
					activeTab === "detail"
				) {
					if (totalActiveAdjustments > 0) {
						steps.push({
							operation: "adjust",
							params: { adjustments: { ...currentAdjustments } },
						});
					}
				} else {
					const finalStepParams: Record<string, any> = {
						...activeParamsJson,
					};
					if (totalActiveAdjustments > 0) {
						finalStepParams.adjustments = { ...currentAdjustments };
					}
					steps.push({
						operation: activeTab,
						params: finalStepParams,
					});
				}
				targetParams = { steps };
			} else if (
				activeTab === "light" ||
				activeTab === "color" ||
				activeTab === "detail"
			) {
				targetOp = "adjust";
				targetParams = { adjustments: { ...currentAdjustments } };
			} else if (totalActiveAdjustments > 0) {
				targetParams.adjustments = { ...currentAdjustments };
			}

			if (!currentImage) {
				const mockDerived: ImageItem = {
					id: "mock-" + Math.random().toString(36).substring(2, 9),
					owner_id: user?.email || "zarqi_ezzoubair",
					parent_image_id: "chair_01",
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
						operation: targetOp,
						params: targetParams,
					},
				};
				saveSuccessImage = mockDerived;
				return;
			}

			const derived = await imageService.transformImage(currentImage.id, {
				operation: targetOp,
				params: targetParams,
				filename: derivedFilename,
				category_id: selectedCategoryId
					? Number(selectedCategoryId)
					: null,
			});

			saveSuccessImage = derived;
		} catch (err: any) {
			errorMessage =
				err.message || "Failed to create derived transformed image.";
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
			if (!ctx)
				throw new Error(
					"Could not initialize 2D rendering canvas context.",
				);

			const img = new Image();
			img.crossOrigin = "anonymous";
			img.src = currentImageUrl;

			await new Promise((resolve, reject) => {
				img.onload = resolve;
				img.onerror = () =>
					reject(
						new Error("Failed to load source image for download."),
					);
			});

			const w = img.naturalWidth || originalWidth;
			const h = img.naturalHeight || originalHeight;

			if (liveFilterStyle && !isComparing) {
				const cssFilter = liveFilterStyle
					.replace("filter: ", "")
					.replace(";", "")
					.trim();
				ctx.filter = cssFilter;
			}

			if (activeTab === "crop") {
				canvas.width = cropWidth;
				canvas.height = cropHeight;
				ctx.drawImage(
					img,
					cropX,
					cropY,
					cropWidth,
					cropHeight,
					0,
					0,
					cropWidth,
					cropHeight,
				);
			} else if (activeTab === "shear") {
				const corners = [
					[0, 0],
					[w, 0],
					[0, h],
					[w, h],
				];
				const trans = corners.map(([x, y]) => [
					x + shearX * y,
					shearY * x + y,
				]);
				const minX = Math.min(...trans.map((pt) => pt[0]));
				const maxX = Math.max(...trans.map((pt) => pt[0]));
				const minY = Math.min(...trans.map((pt) => pt[1]));
				const maxY = Math.max(...trans.map((pt) => pt[1]));

				canvas.width = shearExpand
					? Math.max(1, Math.round(maxX - minX))
					: w;
				canvas.height = shearExpand
					? Math.max(1, Math.round(maxY - minY))
					: h;

				ctx.fillStyle = shearBgColor;
				ctx.fillRect(0, 0, canvas.width, canvas.height);

				ctx.save();
				if (shearExpand) {
					ctx.translate(-minX, -minY);
				}
				ctx.transform(1, shearY, shearX, 1, 0, 0);
				ctx.drawImage(img, 0, 0);
				ctx.restore();
			} else if (activeTab === "affine") {
				const corners = [
					[0, 0],
					[w, 0],
					[0, h],
					[w, h],
				];
				const trans = corners.map(([x, y]) => [
					affineA * x + affineB * y + affineC,
					affineD * x + affineE * y + affineF,
				]);
				const minX = Math.min(...trans.map((pt) => pt[0]));
				const maxX = Math.max(...trans.map((pt) => pt[0]));
				const minY = Math.min(...trans.map((pt) => pt[1]));
				const maxY = Math.max(...trans.map((pt) => pt[1]));

				canvas.width = affineExpand
					? Math.max(1, Math.round(maxX - minX))
					: w;
				canvas.height = affineExpand
					? Math.max(1, Math.round(maxY - minY))
					: h;

				ctx.fillStyle = affineBgColor;
				ctx.fillRect(0, 0, canvas.width, canvas.height);

				ctx.save();
				if (affineExpand) {
					ctx.translate(-minX, -minY);
				}
				ctx.transform(
					affineA,
					affineD,
					affineB,
					affineE,
					affineC,
					affineF,
				);
				ctx.drawImage(img, 0, 0);
				ctx.restore();
			} else if (activeTab === "resize") {
				canvas.width = resizeWidth;
				canvas.height = resizeHeight;
				ctx.drawImage(img, 0, 0, resizeWidth, resizeHeight);
			} else if (activeTab === "rotate") {
				const rad = (rotateAngle * Math.PI) / 180;
				if (rotateExpand) {
					const newW = Math.round(
						w * Math.abs(Math.cos(rad)) +
							h * Math.abs(Math.sin(rad)),
					);
					const newH = Math.round(
						w * Math.abs(Math.sin(rad)) +
							h * Math.abs(Math.cos(rad)),
					);
					canvas.width = newW;
					canvas.height = newH;
					ctx.fillStyle = rotateBgColor;
					ctx.fillRect(0, 0, newW, newH);
					ctx.save();
					ctx.translate(newW / 2, newH / 2);
					ctx.rotate(rad);
					ctx.drawImage(img, -w / 2, -h / 2);
					ctx.restore();
				} else {
					canvas.width = w;
					canvas.height = h;
					ctx.fillStyle = rotateBgColor;
					ctx.fillRect(0, 0, w, h);
					ctx.save();
					ctx.translate(w / 2, h / 2);
					ctx.rotate(rad);
					ctx.drawImage(img, -w / 2, -h / 2);
					ctx.restore();
				}
			} else if (activeTab === "flip") {
				canvas.width = w;
				canvas.height = h;
				ctx.save();
				ctx.translate(
					flipDirection === "horizontal" ? w : 0,
					flipDirection === "vertical" ? h : 0,
				);
				ctx.scale(
					flipDirection === "horizontal" ? -1 : 1,
					flipDirection === "vertical" ? -1 : 1,
				);
				ctx.drawImage(img, 0, 0);
				ctx.restore();
			} else {
				canvas.width = w;
				canvas.height = h;
				ctx.drawImage(img, 0, 0);
			}

			const dataUrl = canvas.toDataURL("image/jpeg", 0.95);
			const link = document.createElement("a");
			link.download = derivedFilename;
			link.href = dataUrl;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
		} catch (err: any) {
			errorMessage = err.message || "Failed to download image.";
		} finally {
			isDownloading = false;
		}
	}
</script>

<svelte:head>
	<title>Image Transformation Engine - Perceptra</title>
</svelte:head>

<HeaderActionPortal>
	{#snippet breadcrumb()}
		<nav class="flex items-center gap-2 text-xs text-muted-foreground min-w-0" aria-label="Breadcrumb">
			<a
				href="/dashboard"
				class="text-sm font-semibold tracking-tight text-foreground hover:text-primary transition-colors shrink-0"
			>
				Perceptra
			</a>

			<span class="text-xs text-muted-foreground/60 shrink-0">/</span>

			<a
				href="/dashboard/transform"
				class="transition-colors hover:text-foreground shrink-0 {currentImage ? 'text-muted-foreground' : 'text-foreground font-medium'}"
			>
				{m.nav_transform()}
			</a>

			{#if currentImage}
				<span class="text-xs text-muted-foreground/60 shrink-0">/</span>
				<span class="max-w-[110px] sm:max-w-[150px] md:max-w-[190px] lg:max-w-[240px] truncate font-medium text-foreground font-mono" title={currentImage.filename}>
					{currentImage.filename}
				</span>
			{/if}
		</nav>
	{/snippet}

	<div class="flex items-center gap-2">
		<!-- Upload Image Dialog Trigger -->
		<Button
			variant="outline"
			size="sm"
			class="h-8 px-2.5 sm:px-3 text-xs font-semibold gap-1.5 cursor-pointer shadow-2xs border-border"
			onclick={() => {
				uploadError = null;
				uploadFile = null;
				if (uploadPreviewUrl) {
					URL.revokeObjectURL(uploadPreviewUrl);
					uploadPreviewUrl = null;
				}
				isUploadDialogOpen = true;
			}}
			title={m.transform_upload_btn()}
		>
			<UploadCloudIcon data-icon="inline-start" class="size-3.5" />
			<span class="hidden sm:inline">{m.transform_upload_btn()}</span>
		</Button>

		<!-- Reset Canvas -->
		<Button
			variant="outline"
			size="sm"
			class="h-8 px-2.5 sm:px-3 text-xs font-semibold gap-1.5 cursor-pointer shadow-2xs border-border"
			onclick={resetCanvas}
			title={m.transform_reset_btn()}
		>
			<RotateCcwIcon data-icon="inline-start" class="size-3.5" />
			<span class="hidden sm:inline">{m.transform_reset_btn()}</span>
		</Button>

		<!-- Save Derived Image Button (Primary Accent) -->
		<Button
			size="sm"
			class="h-8 px-3 sm:px-3.5 text-xs font-semibold gap-1.5 cursor-pointer shadow-xs bg-primary text-primary-foreground hover:bg-primary/90"
			disabled={isSaving}
			onclick={handleSaveDerivedImage}
			title={m.transform_save_derived_btn()}
		>
			{#if isSaving}
				<Loader2Icon class="size-3.5 animate-spin" />
				<span>{m.transform_saving()}</span>
			{:else}
				<DownloadIcon data-icon="inline-start" class="size-3.5" />
				<span>{m.transform_save_derived_btn()}</span>
			{/if}
		</Button>
	</div>
</HeaderActionPortal>

<div
	class="w-full h-full min-h-0 flex flex-col p-3 sm:p-4 gap-3 select-none overflow-y-auto lg:overflow-hidden"
>
	<!-- Alert Messages -->
	{#if errorMessage}
		<div
			class="p-3.5 rounded-xl border border-destructive/30 bg-destructive/10 text-destructive text-xs flex items-center justify-between"
		>
			<span>{errorMessage}</span>
			<button
				type="button"
				class="underline font-bold cursor-pointer"
				onclick={() => (errorMessage = null)}>{m.query_dismiss()}</button
			>
		</div>
	{/if}

	{#if saveSuccessImage}
		<div
			class="p-4 rounded-xl border border-primary/30 bg-primary/10 text-foreground text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-xs"
		>
			<div class="flex items-center gap-2.5">
				<div
					class="size-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold"
				>
					✓
				</div>
				<div>
					<p class="font-bold">{m.transform_saved_success_title()}</p>
					<p class="text-muted-foreground font-mono text-[11px]">
						{m.transform_saved_success_desc({ filename: saveSuccessImage.filename, width: saveSuccessImage.width ?? 0, height: saveSuccessImage.height ?? 0 })}
					</p>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<Button
					href="/dashboard/images/{saveSuccessImage.id}"
					variant="default"
					size="sm"
					class="h-8 px-3 text-xs gap-1.5 shadow-xs"
				>
					<span>{m.transform_view_features()}</span>
					<ExternalLinkIcon class="size-3.5" />
				</Button>
				<Button
					variant="outline"
					size="sm"
					class="h-8 px-3 text-xs gap-1.5"
					onclick={handleDownloadImage}
				>
					<DownloadIcon class="size-3.5" />
					<span>{m.transform_download()}</span>
				</Button>
				<Button
					href="/dashboard/images"
					variant="outline"
					size="sm"
					class="h-8 px-3 text-xs gap-1.5"
				>
					<span>{m.transform_gallery()}</span>
				</Button>
				<Button
					variant="ghost"
					size="sm"
					class="h-8 px-2 text-xs"
					onclick={() => (saveSuccessImage = null)}
				>
					Dismiss
				</Button>
			</div>
		</div>
	{/if}

	<!-- ========================================================================= -->
	<!-- 2. MAIN 3-COLUMN WORKSPACE (Left: Tools, Center: Canvas, Right: Settings) -->
	<!-- ========================================================================= -->
	<div class="flex-1 min-h-0 flex flex-col lg:flex-row gap-3 items-stretch">
		<!-- --------------------------------------------------------------------- -->
		<!-- COLUMN 1: TRANSFORMATION TOOLS & PRESETS (Left Sidebar)               -->
		<!-- --------------------------------------------------------------------- -->
		<div class="w-full lg:w-56 xl:w-64 shrink-0 flex flex-col h-full min-h-0">
			<Card.Root
				class="h-full border border-border/80 shadow-xs p-3.5 flex flex-col justify-between gap-4 overflow-y-auto rounded-xl"
			>
				<!-- Section: Transformation Tools -->
				<div class="space-y-2">
					<h3
						class="text-sm font-semibold tracking-tight text-foreground"
					>
						{m.transform_tools_title()}
					</h3>

					<div class="flex flex-col gap-1.5">
						<!-- Crop -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center gap-2.5 text-xs font-medium transition-all cursor-pointer {activeTab ===
							'crop'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => {
								activeTab = "crop";
								resetCropToCenter();
							}}
						>
							<div
								class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
								'crop'
									? 'bg-primary text-primary-foreground shadow-2xs'
									: 'text-muted-foreground'}"
							>
								<CropIcon class="size-3.5" />
							</div>
							<span>{m.transform_tool_crop()}</span>
						</button>

						<!-- Resize -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center gap-2.5 text-xs font-medium transition-all cursor-pointer {activeTab ===
							'resize'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => (activeTab = "resize")}
						>
							<div
								class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
								'resize'
									? 'bg-primary text-primary-foreground shadow-2xs'
									: 'text-muted-foreground'}"
							>
								<Maximize2Icon class="size-3.5" />
							</div>
							<span>{m.transform_tool_resize()}</span>
						</button>

						<!-- Rotate -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center gap-2.5 text-xs font-medium transition-all cursor-pointer {activeTab ===
							'rotate'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => (activeTab = "rotate")}
						>
							<div
								class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
								'rotate'
									? 'bg-primary text-primary-foreground shadow-2xs'
									: 'text-muted-foreground'}"
							>
								<RotateCwIcon class="size-3.5" />
							</div>
							<span>{m.transform_tool_rotate()}</span>
						</button>

						<!-- Flip -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center gap-2.5 text-xs font-medium transition-all cursor-pointer {activeTab ===
							'flip'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => (activeTab = "flip")}
						>
							<div
								class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
								'flip'
									? 'bg-primary text-primary-foreground shadow-2xs'
									: 'text-muted-foreground'}"
							>
								<SlidersHorizontalIcon class="size-3.5" />
							</div>
							<span>{m.transform_tool_flip()}</span>
						</button>

						<!-- Shear -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center gap-2.5 text-xs font-medium transition-all cursor-pointer {activeTab ===
							'shear'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => (activeTab = "shear")}
						>
							<div
								class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
								'shear'
									? 'bg-primary text-primary-foreground shadow-2xs'
									: 'text-muted-foreground'}"
							>
								<RectangleHorizontalIcon class="size-3.5" />
							</div>
							<span>{m.transform_tool_shear()}</span>
						</button>

						<!-- Affine -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center gap-2.5 text-xs font-medium transition-all cursor-pointer {activeTab ===
							'affine'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => (activeTab = "affine")}
						>
							<div
								class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
								'affine'
									? 'bg-primary text-primary-foreground shadow-2xs'
									: 'text-muted-foreground'}"
							>
								<TriangleIcon class="size-3.5" />
							</div>
							<span>{m.transform_tool_affine()}</span>
						</button>
					</div>
				</div>

				<!-- Section: Photographic Adjustments -->
				<div class="space-y-2 pt-2 border-t border-border/80">
					<div class="flex items-center justify-between">
						<h3
							class="text-sm font-semibold tracking-tight text-foreground"
						>
							{m.transform_adjustments_title()}
						</h3>
						{#if totalActiveAdjustments > 0}
							<button
								type="button"
								class="text-[10px] text-muted-foreground hover:text-primary transition-colors cursor-pointer"
								onclick={resetAllAdjustments}
							>
								{m.transform_reset_all()}
							</button>
						{/if}
					</div>

					<div class="flex flex-col gap-1.5">
						<!-- Light -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center justify-between text-xs font-medium transition-all cursor-pointer {activeTab ===
							'light'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => (activeTab = "light")}
						>
							<div class="flex items-center gap-2.5">
								<div
									class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
									'light'
										? 'bg-primary text-primary-foreground shadow-2xs'
										: 'text-muted-foreground'}"
								>
									<SunIcon class="size-3.5" />
								</div>
								<span>{m.transform_tool_light()}</span>
							</div>
							{#if activeLightCount > 0}
								<span
									class="px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-primary text-primary-foreground"
								>
									{activeLightCount}
								</span>
							{/if}
						</button>

						<!-- Color -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center justify-between text-xs font-medium transition-all cursor-pointer {activeTab ===
							'color'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => (activeTab = "color")}
						>
							<div class="flex items-center gap-2.5">
								<div
									class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
									'color'
										? 'bg-primary text-primary-foreground shadow-2xs'
										: 'text-muted-foreground'}"
								>
									<PaletteIcon class="size-3.5" />
								</div>
								<span>{m.transform_tool_color()}</span>
							</div>
							{#if activeColorCount > 0}
								<span
									class="px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-primary text-primary-foreground"
								>
									{activeColorCount}
								</span>
							{/if}
						</button>

						<!-- Detail -->
						<button
							type="button"
							class="w-full h-10 px-2.5 rounded-lg flex items-center justify-between text-xs font-medium transition-all cursor-pointer {activeTab ===
							'detail'
								? 'bg-primary/10 text-primary border border-primary/25 font-bold shadow-2xs'
								: 'text-muted-foreground hover:text-foreground hover:bg-muted/70 border border-transparent'}"
							onclick={() => (activeTab = "detail")}
						>
							<div class="flex items-center gap-2.5">
								<div
									class="size-6 rounded-md flex items-center justify-center shrink-0 {activeTab ===
									'detail'
										? 'bg-primary text-primary-foreground shadow-2xs'
										: 'text-muted-foreground'}"
								>
									<SparklesIcon class="size-3.5" />
								</div>
								<span>{m.transform_tool_detail()}</span>
							</div>
							{#if activeDetailCount > 0}
								<span
									class="px-1.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-primary text-primary-foreground"
								>
									{activeDetailCount}
								</span>
							{/if}
						</button>
					</div>
				</div>

				<!-- Section: Active Pipeline Stack (if any) -->
				{#if appliedStack.length > 0}
					<div class="space-y-2 pt-2 border-t border-border/80">
						<div class="flex items-center justify-between">
							<div class="flex items-center gap-1.5">
								<LayersIcon class="size-3.5 text-primary" />
								<h3
									class="text-xs font-semibold tracking-tight text-foreground"
								>
									{m.transform_stack_title({ count: appliedStack.length })}
								</h3>
							</div>
							<button
								type="button"
								class="text-[10px] text-muted-foreground hover:text-destructive transition-colors cursor-pointer"
								onclick={clearStack}
							>
								{m.transform_clear_stack()}
							</button>
						</div>
						<div
							class="flex flex-col gap-1 max-h-32 overflow-y-auto"
						>
							{#each appliedStack as step, idx}
								<div
									class="flex items-center justify-between px-2 py-1.5 rounded-md bg-muted/40 border border-border/60 text-2xs"
								>
									<div
										class="flex items-center gap-1.5 truncate"
									>
										<span
											class="font-mono text-[10px] text-muted-foreground"
											>#{idx + 1}</span
										>
										<span
											class="font-medium text-foreground truncate"
											>{step.description}</span
										>
									</div>
									<button
										type="button"
										class="text-muted-foreground hover:text-destructive p-0.5 cursor-pointer rounded"
										onclick={() => removeStackStep(idx)}
										title="Remove layer step"
									>
										<XIcon class="size-3" />
									</button>
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Section: Presets -->
				<div class="space-y-2 pt-2 border-t border-border/80">
					<h3
						class="text-sm font-semibold tracking-tight text-foreground"
					>
						{m.transform_presets_title()}
					</h3>

					<div class="grid grid-cols-2 gap-2">
						{#if activeTab === "affine"}
							{#each [{ label: "Identity", apply: () => {
											affineA = 1;
											affineB = 0;
											affineC = 0;
											affineD = 0;
											affineE = 1;
											affineF = 0;
											activePreset = "Identity";
										} }, { label: "Slant Right", apply: () => {
											affineA = 1;
											affineB = 0.25;
											affineC = 0;
											affineD = 0;
											affineE = 1;
											affineF = 0;
											activePreset = "Slant Right";
										} }, { label: "Slant Left", apply: () => {
											affineA = 1;
											affineB = -0.25;
											affineC = 0;
											affineD = 0;
											affineE = 1;
											affineF = 0;
											activePreset = "Slant Left";
										} }, { label: "Scale 1.25x", apply: () => {
											affineA = 1.25;
											affineB = 0;
											affineC = 0;
											affineD = 0;
											affineE = 1.25;
											affineF = 0;
											activePreset = "Scale 1.25x";
										} }] as p}
								<button
									type="button"
									class="h-9 px-2 rounded-lg border text-xs font-medium text-center transition-all cursor-pointer truncate {activePreset ===
									p.label
										? 'border-primary bg-primary/10 text-primary font-bold shadow-2xs'
										: 'border-border bg-card text-muted-foreground hover:bg-muted hover:text-foreground'}"
									onclick={p.apply}
								>
									{p.label}
								</button>
							{/each}
						{:else}
							{#each [{ label: "Square (1:1)", value: "1:1 (Square)" }, { label: "Landscape (16:9)", value: "Landscape (16:9)" }, { label: "Portrait (9:16)", value: "Portrait (9:16)" }, { label: "Original", value: "Original" }] as p}
								<button
									type="button"
									class="h-9 px-2 rounded-lg border text-xs font-medium text-center transition-all cursor-pointer truncate {activePreset ===
									p.value
										? 'border-primary bg-primary/10 text-primary font-bold shadow-2xs'
										: 'border-border bg-card text-muted-foreground hover:bg-muted hover:text-foreground'}"
									onclick={() => applyPreset(p.value)}
								>
									{p.label}
								</button>
							{/each}
						{/if}
					</div>
				</div>
			</Card.Root>
		</div>

		<!-- --------------------------------------------------------------------- -->
		<!-- COLUMN 2: CENTER CANVAS VIEWPORT & DOCKED TOOLBAR                     -->
		<!-- --------------------------------------------------------------------- -->
		<div class="flex-1 min-w-0 h-full flex flex-col min-h-0">
			<Card.Root
				class="h-full border border-border/80 shadow-xs flex flex-col rounded-xl overflow-hidden min-h-0"
			>
				<!-- Canvas Viewport -->
				<div
					class="relative w-full flex-1 min-h-[300px] overflow-hidden flex items-center justify-center p-4 sm:p-6 select-none bg-muted/50"
				>
					<!-- Zoom Scaler Container -->
					<div
						class="relative max-w-full max-h-full transition-transform duration-100 ease-out origin-center flex items-center justify-center"
						style="transform: scale({zoomLevel / 100});"
					>
						<!-- Image Container -->
						<div
							class="relative overflow-hidden shadow-2xl transition-transform duration-100 ease-out select-none"
							style="
								{activeTab === 'crop'
								? 'transform: none;'
								: activeTab === 'shear'
									? `transform: matrix(1, ${shearY}, ${shearX}, 1, 0, 0);`
									: activeTab === 'affine'
										? `transform: matrix(${affineA}, ${affineD}, ${affineB}, ${affineE}, ${affineC}, ${affineF});`
										: activeTab === 'rotate'
											? `transform: rotate(${rotateAngle}deg);`
											: activeTab === 'flip'
												? `transform: scale(${flipDirection === 'horizontal' ? -1 : 1}, ${flipDirection === 'vertical' ? -1 : 1});`
												: ''}
							"
						>
							<!-- Source Image Element -->
							<img
								bind:this={imageEl}
								src={currentImageUrl}
								alt={originalFilename}
								onload={handleImageLoad}
								class="max-w-[85vw] max-h-[calc(100vh-250px)] object-contain rounded-xs border border-white/20 select-none pointer-events-none block transition-[filter] duration-75"
								style={liveFilterStyle}
							/>

							<!-- ========================================================= -->
							<!-- INTERACTIVE CROP BOX OVERLAY (Matching Concept 2)         -->
							<!-- ========================================================= -->
							{#if activeTab === "crop"}
								<div
									role="region"
									aria-label="Interactive crop selection box"
									class="absolute border-2 border-white select-none shadow-[0_0_0_9999px_rgba(0,0,0,0.52)] z-30"
									style="
										left: {(cropX / originalWidth) * 100}%;
										top: {(cropY / originalHeight) * 100}%;
										width: {(cropWidth / originalWidth) * 100}%;
										height: {(cropHeight / originalHeight) * 100}%;
										cursor: move;
									"
									onpointerdown={(e) =>
										handleCropPointerDown("move", e)}
								>
									<!-- Rule of Thirds Guide Lines -->
									{#if showRuleOfThirds}
										<div
											class="absolute inset-0 pointer-events-none"
										>
											<div
												class="absolute top-0 bottom-0 left-1/3 w-px border-l border-white/40"
											></div>
											<div
												class="absolute top-0 bottom-0 left-2/3 w-px border-l border-white/40"
											></div>
											<div
												class="absolute left-0 right-0 top-1/3 h-px border-t border-white/40"
											></div>
											<div
												class="absolute left-0 right-0 top-2/3 h-px border-t border-white/40"
											></div>
										</div>
									{/if}

									<!-- 8 Precision Handles (4 Corners are circular primary nodes, 4 Edges are subtle pills) -->
									{#each cropHandles as handle (handle.id)}
										{#if handle.isCorner}
											<div
												role="button"
												tabindex="0"
												aria-label="Resize {handle.label}"
												class="absolute size-3.5 sm:size-4 rounded-full bg-primary border-2 border-background shadow-md z-40 transition-transform hover:scale-125 focus:outline-hidden after:absolute after:-inset-2.5 after:content-['']"
												style="{handle.positionStyle}; cursor: {handle.cursor};"
												onpointerdown={(e) =>
													handleCropPointerDown(
														handle.id,
														e,
													)}
											></div>
										{:else}
											<div
												role="button"
												tabindex="0"
												aria-label="Resize {handle.label}"
												class="absolute size-2 sm:size-2.5 rounded-full bg-primary/90 border border-background shadow-xs z-40 transition-transform hover:scale-125 focus:outline-hidden after:absolute after:-inset-2 after:content-['']"
												style="{handle.positionStyle}; cursor: {handle.cursor};"
												onpointerdown={(e) =>
													handleCropPointerDown(
														handle.id,
														e,
													)}
											></div>
										{/if}
									{/each}
								</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- DOCKED CANVAS BOTTOM TOOLBAR -->
				<div
					class="p-2.5 px-4 border-t border-border bg-card flex items-center justify-between text-xs text-muted-foreground select-none"
				>
					<!-- Left: Undo & Redo -->
					<div class="flex items-center gap-1.5">
						<Button
							variant="outline"
							size="icon"
							class="size-8 rounded-lg cursor-pointer hover:bg-muted text-muted-foreground hover:text-foreground"
							disabled={cropHistoryIndex <= 0}
							onclick={undoCrop}
							title="Undo (Ctrl+Z)"
						>
							<Undo2Icon class="size-4" />
						</Button>
						<Button
							variant="outline"
							size="icon"
							class="size-8 rounded-lg cursor-pointer hover:bg-muted text-muted-foreground hover:text-foreground"
							disabled={cropHistoryIndex >=
								cropHistory.length - 1}
							onclick={redoCrop}
							title="Redo (Ctrl+Y)"
						>
							<Redo2Icon class="size-4" />
						</Button>
					</div>

					<!-- Center: Compare, Stack & Zoom Controls -->
					<div class="flex items-center gap-2">
						<!-- A/B Hold Compare Button -->
						<Button
							variant={isComparing ? "default" : "outline"}
							size="sm"
							class="h-8 px-2.5 text-xs font-semibold gap-1.5 cursor-pointer shadow-2xs transition-colors {isComparing
								? 'bg-amber-600 text-white hover:bg-amber-700'
								: 'text-muted-foreground hover:text-foreground'}"
							onpointerdown={() => (isComparing = true)}
							onpointerup={() => (isComparing = false)}
							onpointerleave={() => (isComparing = false)}
							title="Hold down to preview original unadjusted image"
						>
							<EyeIcon class="size-3.5" />
							<span class="hidden sm:inline"
								>{isComparing
									? m.transform_btn_compare_viewing()
									: m.transform_btn_compare_hold()}</span
							>
						</Button>

						<!-- Stack Step Button -->
						<Button
							variant="outline"
							size="sm"
							class="h-8 px-2.5 text-xs font-semibold gap-1.5 cursor-pointer shadow-2xs border-primary/30 text-primary hover:bg-primary/10"
							onclick={handleStackCurrentStep}
							title="Stack current adjustments or transform onto the working image pipeline"
						>
							<LayersIcon class="size-3.5" />
							<span class="hidden sm:inline">{m.transform_btn_stack_step()}</span>
							{#if appliedStack.length > 0}
								<span
									class="px-1.5 py-0.2 rounded-full text-[10px] font-mono font-bold bg-primary text-primary-foreground"
								>
									{appliedStack.length}
								</span>
							{/if}
						</Button>

						<!-- Zoom Controls Pill -->
						<div
							class="flex items-center gap-1 px-2.5 py-1 rounded-lg border border-border bg-muted/30 font-mono"
						>
							<button
								type="button"
								class="p-0.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
								onclick={() =>
									(zoomLevel = Math.max(50, zoomLevel - 10))}
								title="Zoom Out"
							>
								<MinusIcon class="size-3.5" />
							</button>
							<span
								class="text-xs font-semibold text-foreground px-2 select-none"
								>{zoomLevel}%</span
							>
							<button
								type="button"
								class="p-0.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
								onclick={() =>
									(zoomLevel = Math.min(200, zoomLevel + 10))}
								title="Zoom In"
							>
								<PlusIcon class="size-3.5" />
							</button>
						</div>
					</div>

					<!-- Right: Fit to View / Fullscreen -->
					<div class="flex items-center gap-1">
						<Button
							variant="outline"
							size="icon"
							class="size-8 rounded-lg cursor-pointer hover:bg-muted text-muted-foreground hover:text-foreground"
							onclick={() => (zoomLevel = 100)}
							title="Reset zoom to 100%"
						>
							<Maximize2Icon class="size-4" />
						</Button>
					</div>
				</div>
			</Card.Root>
		</div>

		<!-- --------------------------------------------------------------------- -->
		<!-- COLUMN 3: SETTINGS & QUICK ACTIONS (Right Sidebar)                    -->
		<!-- --------------------------------------------------------------------- -->
		<div class="w-full lg:w-72 xl:w-80 shrink-0 flex flex-col h-full min-h-0">
			<Card.Root
				class="h-full border border-border/80 shadow-xs p-3.5 flex flex-col justify-between gap-4 overflow-y-auto rounded-xl"
			>
				<!-- Section: Dynamic Tool Settings Title -->
				<div class="space-y-4">
					<h3
						class="text-sm font-semibold tracking-tight text-foreground flex items-center justify-between"
					>
						<span>
							{activeTab === "crop"
								? m.transform_crop_settings()
								: activeTab === "resize"
									? m.transform_resize_settings()
									: activeTab === "rotate"
										? m.transform_rotate_settings()
										: activeTab === "flip"
											? m.transform_flip_settings()
											: activeTab === "shear"
												? m.transform_shear_settings()
												: activeTab === "affine"
													? m.transform_affine_settings()
													: activeTab === "light"
														? m.transform_light_settings()
														: activeTab === "color"
															? m.transform_color_settings()
															: m.transform_detail_settings()}
						</span>
						{#if activeTab === "light" && activeLightCount > 0}
							<button
								type="button"
								class="text-xs font-normal text-muted-foreground hover:text-primary transition-colors cursor-pointer"
								onclick={resetLightAdjustments}
							>
								{m.transform_reset_light()}
							</button>
						{:else if activeTab === "color" && activeColorCount > 0}
							<button
								type="button"
								class="text-xs font-normal text-muted-foreground hover:text-primary transition-colors cursor-pointer"
								onclick={resetColorAdjustments}
							>
								{m.transform_reset_color()}
							</button>
						{:else if activeTab === "detail" && activeDetailCount > 0}
							<button
								type="button"
								class="text-xs font-normal text-muted-foreground hover:text-primary transition-colors cursor-pointer"
								onclick={resetDetailAdjustments}
							>
								{m.transform_reset_detail()}
							</button>
						{/if}
					</h3>

					<!-- CROP CONTROLS -->
					{#if activeTab === "crop"}
						<!-- Aspect Ratio Dropdown -->
						<div class="space-y-1.5">
							<span class="text-xs font-medium text-foreground"
								>{m.transform_aspect_ratio()}</span
							>
							<Select.Root
								type="single"
								value={activePreset}
								onValueChange={(val) => {
									if (val) applyPreset(val);
								}}
							>
								<Select.Trigger
									class="w-full text-xs h-9 justify-between font-normal"
								>
									<span>{activePreset}</span>
								</Select.Trigger>
								<Select.Content>
									<Select.Item value="1:1 (Square)"
										>1:1 (Square)</Select.Item
									>
									<Select.Item value="Landscape (16:9)"
										>Landscape (16:9)</Select.Item
									>
									<Select.Item value="Portrait (9:16)"
										>Portrait (9:16)</Select.Item
									>
									<Select.Item value="4:3">4:3</Select.Item>
									<Select.Item value="Original"
										>Original</Select.Item
									>
									<Select.Item value="Free">Free</Select.Item>
								</Select.Content>
							</Select.Root>
						</div>

						<!-- Dimensions (W / H with Aspect Lock) -->
						<div class="space-y-1.5">
							<span class="text-xs font-medium text-foreground"
								>{m.transform_dimensions()}</span
							>
							<div class="flex items-center gap-2">
								<!-- Width Box -->
								<div
									class="flex-1 flex items-center h-8.5 rounded-lg border border-input bg-card px-2.5 gap-1.5 focus-within:ring-2 focus-within:ring-ring focus-within:border-primary"
								>
									<span
										class="text-xs font-semibold text-muted-foreground select-none"
										>W</span
									>
									<input
										type="number"
										bind:value={cropWidth}
										oninput={handleWidthInput}
										class="w-full bg-transparent text-xs font-mono text-foreground focus:outline-none"
										min="10"
										max={originalWidth}
									/>
									<span
										class="text-[11px] text-muted-foreground select-none"
										>px</span
									>
								</div>

								<!-- Lock Aspect Ratio Toggle Button -->
								<Button
									variant="ghost"
									size="icon"
									class="size-8 rounded-full shrink-0 transition-colors {keepAspectRatio
										? 'text-primary bg-primary/10 shadow-2xs'
										: 'text-muted-foreground hover:bg-muted'}"
									onclick={() =>
										(keepAspectRatio = !keepAspectRatio)}
									title={keepAspectRatio
										? "Aspect ratio locked"
										: "Aspect ratio unlocked"}
								>
									{#if keepAspectRatio}
										<LinkIcon class="size-3.5" />
									{:else}
										<UnlinkIcon class="size-3.5" />
									{/if}
								</Button>

								<!-- Height Box -->
								<div
									class="flex-1 flex items-center h-8.5 rounded-lg border border-input bg-card px-2.5 gap-1.5 focus-within:ring-2 focus-within:ring-ring focus-within:border-primary"
								>
									<span
										class="text-xs font-semibold text-muted-foreground select-none"
										>H</span
									>
									<input
										type="number"
										bind:value={cropHeight}
										oninput={handleHeightInput}
										class="w-full bg-transparent text-xs font-mono text-foreground focus:outline-none"
										min="10"
										max={originalHeight}
									/>
									<span
										class="text-[11px] text-muted-foreground select-none"
										>px</span
									>
								</div>
							</div>
						</div>

						<!-- Position (X / Y) -->
						<div class="space-y-1.5">
							<span class="text-xs font-medium text-foreground"
								>{m.transform_position()}</span
							>
							<div class="flex items-center gap-2">
								<div
									class="flex-1 flex items-center h-8.5 rounded-lg border border-input bg-card px-2.5 gap-1.5 focus-within:ring-2 focus-within:ring-ring focus-within:border-primary"
								>
									<span
										class="text-xs font-semibold text-muted-foreground select-none"
										>X</span
									>
									<input
										type="number"
										bind:value={cropX}
										oninput={() => {
											cropX = clamp(
												cropX,
												0,
												Math.max(
													0,
													originalWidth - cropWidth,
												),
											);
											pushCropHistory();
										}}
										class="w-full bg-transparent text-xs font-mono text-foreground focus:outline-none"
										min="0"
										max={Math.max(
											0,
											originalWidth - cropWidth,
										)}
									/>
									<span
										class="text-[11px] text-muted-foreground select-none"
										>px</span
									>
								</div>

								<div
									class="flex-1 flex items-center h-8.5 rounded-lg border border-input bg-card px-2.5 gap-1.5 focus-within:ring-2 focus-within:ring-ring focus-within:border-primary"
								>
									<span
										class="text-xs font-semibold text-muted-foreground select-none"
										>Y</span
									>
									<input
										type="number"
										bind:value={cropY}
										oninput={() => {
											cropY = clamp(
												cropY,
												0,
												Math.max(
													0,
													originalHeight - cropHeight,
												),
											);
											pushCropHistory();
										}}
										class="w-full bg-transparent text-xs font-mono text-foreground focus:outline-none"
										min="0"
										max={Math.max(
											0,
											originalHeight - cropHeight,
										)}
									/>
									<span
										class="text-[11px] text-muted-foreground select-none"
										>px</span
									>
								</div>
							</div>
						</div>

						<!-- RESIZE CONTROLS -->
					{:else if activeTab === "resize"}
						<div class="space-y-3">
							<div class="space-y-1">
								<div
									class="flex items-center justify-between text-xs"
								>
									<span class="text-muted-foreground"
										>{m.transform_scale()}</span
									>
									<span
										class="font-mono font-bold text-foreground"
										>{(resizeScale * 100).toFixed(0)}%</span
									>
								</div>
								<input
									type="range"
									min="0.1"
									max="2.0"
									step="0.05"
									bind:value={resizeScale}
									oninput={() => {
										resizeWidth = Math.round(
											originalWidth * resizeScale,
										);
										resizeHeight = Math.round(
											originalHeight * resizeScale,
										);
									}}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<div class="flex items-center gap-2">
								<div
									class="flex-1 flex items-center h-8.5 rounded-lg border border-input bg-card px-2.5 gap-1.5"
								>
									<span
										class="text-xs text-muted-foreground select-none"
										>W</span
									>
									<input
										type="number"
										bind:value={resizeWidth}
										oninput={() => {
											if (keepAspectRatio) {
												resizeHeight = Math.round(
													(resizeWidth /
														originalWidth) *
														originalHeight,
												);
											}
										}}
										class="w-full bg-transparent text-xs font-mono text-foreground focus:outline-none"
									/>
								</div>
								<div
									class="flex-1 flex items-center h-8.5 rounded-lg border border-input bg-card px-2.5 gap-1.5"
								>
									<span
										class="text-xs text-muted-foreground select-none"
										>H</span
									>
									<input
										type="number"
										bind:value={resizeHeight}
										oninput={() => {
											if (keepAspectRatio) {
												resizeWidth = Math.round(
													(resizeHeight /
														originalHeight) *
														originalWidth,
												);
											}
										}}
										class="w-full bg-transparent text-xs font-mono text-foreground focus:outline-none"
									/>
								</div>
							</div>
						</div>

						<!-- ROTATE CONTROLS -->
					{:else if activeTab === "rotate"}
						<div class="space-y-3">
							<div class="grid grid-cols-4 gap-1.5">
								{#each [-90, 90, 180, 0] as deg}
									<Button
										variant="outline"
										size="sm"
										class="h-8 text-xs font-mono"
										onclick={() => (rotateAngle = deg)}
									>
										{deg > 0 ? `+${deg}°` : `${deg}°`}
									</Button>
								{/each}
							</div>
							<div class="space-y-1">
								<div
									class="flex items-center justify-between text-xs"
								>
									<span class="text-muted-foreground"
										>{m.transform_angle()}</span
									>
									<span
										class="font-mono font-bold text-foreground"
										>{rotateAngle}°</span
									>
								</div>
								<input
									type="range"
									min="-180"
									max="180"
									step="1"
									bind:value={rotateAngle}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>
						</div>

						<!-- FLIP CONTROLS -->
					{:else if activeTab === "flip"}
						<div class="grid grid-cols-2 gap-2">
							<button
								type="button"
								class="p-3 rounded-xl border flex flex-col items-center gap-2 transition-all cursor-pointer {flipDirection ===
								'horizontal'
									? 'border-primary bg-primary/10 text-primary font-bold shadow-2xs'
									: 'border-border bg-card text-muted-foreground hover:bg-muted'}"
								onclick={() => (flipDirection = "horizontal")}
							>
								<FlipHorizontalIcon class="size-5" />
								<span class="text-xs">{m.transform_horizontal()}</span>
							</button>
							<button
								type="button"
								class="p-3 rounded-xl border flex flex-col items-center gap-2 transition-all cursor-pointer {flipDirection ===
								'vertical'
									? 'border-primary bg-primary/10 text-primary font-bold shadow-2xs'
									: 'border-border bg-card text-muted-foreground hover:bg-muted'}"
								onclick={() => (flipDirection = "vertical")}
							>
								<FlipVerticalIcon class="size-5" />
								<span class="text-xs">{m.transform_vertical()}</span>
							</button>
						</div>

						<!-- SHEAR CONTROLS -->
					{:else if activeTab === "shear"}
						<div class="space-y-3">
							<div class="space-y-1">
								<div
									class="flex items-center justify-between text-xs"
								>
									<span class="text-muted-foreground"
										>{m.transform_shear_x()}</span
									>
									<span
										class="font-mono font-bold text-foreground"
										>{shearX.toFixed(2)}</span
									>
								</div>
								<input
									type="range"
									min="-2.0"
									max="2.0"
									step="0.05"
									bind:value={shearX}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>
							<div class="space-y-1">
								<div
									class="flex items-center justify-between text-xs"
								>
									<span class="text-muted-foreground"
										>{m.transform_shear_y()}</span
									>
									<span
										class="font-mono font-bold text-foreground"
										>{shearY.toFixed(2)}</span
									>
								</div>
								<input
									type="range"
									min="-2.0"
									max="2.0"
									step="0.05"
									bind:value={shearY}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<div class="flex items-center justify-between pt-1">
								<span class="text-xs text-muted-foreground">{m.transform_expand_canvas()}</span>
								<input
									type="checkbox"
									bind:checked={shearExpand}
									class="rounded border-border accent-primary cursor-pointer"
								/>
							</div>
							<div class="flex items-center justify-between pt-1">
								<span class="text-xs text-muted-foreground">{m.transform_bg_color()}</span>
								<div class="flex items-center gap-1.5">
									<input
										type="color"
										bind:value={shearBgColor}
										class="size-6 p-0 border border-border rounded cursor-pointer bg-transparent"
									/>
									<span class="font-mono text-2xs uppercase text-foreground">{shearBgColor}</span>
								</div>
							</div>
						</div>

						<!-- AFFINE CONTROLS -->
					{:else if activeTab === "affine"}
						<div class="space-y-3">
							<!-- Matrix Visual Preview Card -->
							<div
								class="p-2.5 rounded-lg border border-border bg-muted/30 font-mono text-2xs space-y-1.5"
							>
								<div
									class="flex justify-between items-center text-muted-foreground border-b border-border/50 pb-1 font-sans text-xs"
								>
									<span class="font-semibold text-foreground">{m.transform_matrix()}</span>
									<span class="font-mono text-2xs">det = {(affineA * affineE - affineB * affineD).toFixed(2)}</span>
								</div>
								<div class="grid grid-cols-3 gap-1 pt-1 text-center font-mono">
									<div class="p-1 rounded bg-card border border-border/70">
										<span class="text-muted-foreground text-[10px] block font-sans">a (scaleX)</span>
										<span class="font-bold text-foreground">{affineA.toFixed(2)}</span>
									</div>
									<div class="p-1 rounded bg-card border border-border/70">
										<span class="text-muted-foreground text-[10px] block font-sans">b (shearX)</span>
										<span class="font-bold text-foreground">{affineB.toFixed(2)}</span>
									</div>
									<div class="p-1 rounded bg-card border border-border/70">
										<span class="text-muted-foreground text-[10px] block font-sans">c (offsetX)</span>
										<span class="font-bold text-foreground">{Math.round(affineC)}px</span>
									</div>
									<div class="p-1 rounded bg-card border border-border/70">
										<span class="text-muted-foreground text-[10px] block font-sans">d (shearY)</span>
										<span class="font-bold text-foreground">{affineD.toFixed(2)}</span>
									</div>
									<div class="p-1 rounded bg-card border border-border/70">
										<span class="text-muted-foreground text-[10px] block font-sans">e (scaleY)</span>
										<span class="font-bold text-foreground">{affineE.toFixed(2)}</span>
									</div>
									<div class="p-1 rounded bg-card border border-border/70">
										<span class="text-muted-foreground text-[10px] block font-sans">f (offsetY)</span>
										<span class="font-bold text-foreground">{Math.round(affineF)}px</span>
									</div>
								</div>
							</div>

							<!-- Matrix Sliders -->
							<div class="space-y-2">
								<div class="grid grid-cols-2 gap-2">
									<div class="space-y-1">
										<div class="flex items-center justify-between text-2xs">
											<span class="text-muted-foreground">Scale X (a)</span>
											<span class="font-mono font-bold text-foreground">{affineA.toFixed(2)}</span>
										</div>
										<input
											type="range"
											min="-2.5"
											max="2.5"
											step="0.05"
											bind:value={affineA}
											class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
										/>
									</div>
									<div class="space-y-1">
										<div class="flex items-center justify-between text-2xs">
											<span class="text-muted-foreground">Scale Y (e)</span>
											<span class="font-mono font-bold text-foreground">{affineE.toFixed(2)}</span>
										</div>
										<input
											type="range"
											min="-2.5"
											max="2.5"
											step="0.05"
											bind:value={affineE}
											class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
										/>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-2">
									<div class="space-y-1">
										<div class="flex items-center justify-between text-2xs">
											<span class="text-muted-foreground">Shear X (b)</span>
											<span class="font-mono font-bold text-foreground">{affineB.toFixed(2)}</span>
										</div>
										<input
											type="range"
											min="-2.0"
											max="2.0"
											step="0.05"
											bind:value={affineB}
											class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
										/>
									</div>
									<div class="space-y-1">
										<div class="flex items-center justify-between text-2xs">
											<span class="text-muted-foreground">Shear Y (d)</span>
											<span class="font-mono font-bold text-foreground">{affineD.toFixed(2)}</span>
										</div>
										<input
											type="range"
											min="-2.0"
											max="2.0"
											step="0.05"
											bind:value={affineD}
											class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
										/>
									</div>
								</div>

								<div class="grid grid-cols-2 gap-2">
									<div class="space-y-1">
										<div class="flex items-center justify-between text-2xs">
											<span class="text-muted-foreground">Offset X (c)</span>
											<span class="font-mono font-bold text-foreground">{Math.round(affineC)}px</span>
										</div>
										<input
											type="range"
											min={-Math.max(500, originalWidth)}
											max={Math.max(500, originalWidth)}
											step="1"
											bind:value={affineC}
											class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
										/>
									</div>
									<div class="space-y-1">
										<div class="flex items-center justify-between text-2xs">
											<span class="text-muted-foreground">Offset Y (f)</span>
											<span class="font-mono font-bold text-foreground">{Math.round(affineF)}px</span>
										</div>
										<input
											type="range"
											min={-Math.max(500, originalHeight)}
											max={Math.max(500, originalHeight)}
											step="1"
											bind:value={affineF}
											class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
										/>
									</div>
								</div>

								<div class="flex items-center justify-between pt-1">
									<span class="text-xs text-muted-foreground">{m.transform_expand_canvas()}</span>
									<input
										type="checkbox"
										bind:checked={affineExpand}
										class="rounded border-border accent-primary cursor-pointer"
									/>
								</div>
								<div class="flex items-center justify-between pt-1">
									<span class="text-xs text-muted-foreground">{m.transform_bg_color()}</span>
									<div class="flex items-center gap-1.5">
										<input
											type="color"
											bind:value={affineBgColor}
											class="size-6 p-0 border border-border rounded cursor-pointer bg-transparent"
										/>
										<span class="font-mono text-2xs uppercase text-foreground">{affineBgColor}</span>
									</div>
								</div>
							</div>
						</div>

					<!-- LIGHT CONTROLS -->
					{:else if activeTab === "light"}
						<div class="space-y-3">
							<!-- Brightness -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Brightness</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjBrightness !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjBrightness > 0 ? `+${adjBrightness}` : adjBrightness}
										</span>
										{#if adjBrightness !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjBrightness = 0)}
												title="Reset Brightness"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjBrightness}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Contrast -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Contrast</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjContrast !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjContrast > 0 ? `+${adjContrast}` : adjContrast}
										</span>
										{#if adjContrast !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjContrast = 0)}
												title="Reset Contrast"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjContrast}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Exposure -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Exposure</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjExposure !== 0 ? 'text-primary' : 'text-foreground'}">
											{(adjExposure / 50).toFixed(2)} EV
										</span>
										{#if adjExposure !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjExposure = 0)}
												title="Reset Exposure"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjExposure}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Highlights -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Highlights</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjHighlights !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjHighlights > 0 ? `+${adjHighlights}` : adjHighlights}
										</span>
										{#if adjHighlights !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjHighlights = 0)}
												title="Reset Highlights"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjHighlights}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Shadows -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Shadows</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjShadows !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjShadows > 0 ? `+${adjShadows}` : adjShadows}
										</span>
										{#if adjShadows !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjShadows = 0)}
												title="Reset Shadows"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjShadows}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Whites -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Whites</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjWhites !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjWhites > 0 ? `+${adjWhites}` : adjWhites}
										</span>
										{#if adjWhites !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjWhites = 0)}
												title="Reset Whites"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjWhites}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Blacks -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Blacks</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjBlacks !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjBlacks > 0 ? `+${adjBlacks}` : adjBlacks}
										</span>
										{#if adjBlacks !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjBlacks = 0)}
												title="Reset Blacks"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjBlacks}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>
						</div>

					<!-- COLOR CONTROLS -->
					{:else if activeTab === "color"}
						<div class="space-y-3">
							<!-- Saturation -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Saturation</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjSaturation !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjSaturation > 0 ? `+${adjSaturation}` : adjSaturation}
										</span>
										{#if adjSaturation !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjSaturation = 0)}
												title="Reset Saturation"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjSaturation}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Vibrance -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Vibrance</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjVibrance !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjVibrance > 0 ? `+${adjVibrance}` : adjVibrance}
										</span>
										{#if adjVibrance !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjVibrance = 0)}
												title="Reset Vibrance"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjVibrance}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Hue -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Hue Shift</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjHue !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjHue > 0 ? `+${adjHue}` : adjHue}°
										</span>
										{#if adjHue !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjHue = 0)}
												title="Reset Hue"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-180"
									max="180"
									step="1"
									bind:value={adjHue}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Temperature -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Temperature (Warm / Cool)</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjTemperature !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjTemperature > 0 ? `+${adjTemperature}` : adjTemperature}
										</span>
										{#if adjTemperature !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjTemperature = 0)}
												title="Reset Temperature"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjTemperature}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Tint -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Tint (Magenta / Green)</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjTint !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjTint > 0 ? `+${adjTint}` : adjTint}
										</span>
										{#if adjTint !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjTint = 0)}
												title="Reset Tint"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjTint}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>
						</div>

					<!-- DETAIL CONTROLS -->
					{:else if activeTab === "detail"}
						<div class="space-y-3">
							<!-- Sharpness -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Sharpness</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjSharpness !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjSharpness}
										</span>
										{#if adjSharpness !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjSharpness = 0)}
												title="Reset Sharpness"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="0"
									max="100"
									step="1"
									bind:value={adjSharpness}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Clarity -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Clarity</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjClarity !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjClarity > 0 ? `+${adjClarity}` : adjClarity}
										</span>
										{#if adjClarity !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjClarity = 0)}
												title="Reset Clarity"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="-100"
									max="100"
									step="1"
									bind:value={adjClarity}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>

							<!-- Blur -->
							<div class="space-y-1">
								<div class="flex items-center justify-between text-2xs">
									<span class="text-muted-foreground">Gaussian Blur</span>
									<div class="flex items-center gap-1 font-mono">
										<span class="font-bold {adjBlur !== 0 ? 'text-primary' : 'text-foreground'}">
											{adjBlur}px
										</span>
										{#if adjBlur !== 0}
											<button
												type="button"
												class="p-0.5 rounded text-muted-foreground hover:text-foreground cursor-pointer"
												onclick={() => (adjBlur = 0)}
												title="Reset Blur"
											>
												<RotateCcwIcon class="size-2.5" />
											</button>
										{/if}
									</div>
								</div>
								<input
									type="range"
									min="0"
									max="20"
									step="1"
									bind:value={adjBlur}
									class="w-full accent-primary h-1.5 bg-muted rounded-lg cursor-pointer"
								/>
							</div>
						</div>
					{/if}
				</div>

				<!-- Section: Quick Actions (Matching Concept 2 2x2 Grid) -->
				<div class="space-y-2.5 pt-2 border-t border-border/80">
					<h3
						class="text-sm font-semibold tracking-tight text-foreground"
					>
						{m.transform_quick_actions_title()}
					</h3>

					<div class="grid grid-cols-2 gap-2">
						{#if activeTab === "crop"}
							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={centerCrop}
							>
								<CrosshairIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>{m.transform_action_center()}</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={fitToImage}
							>
								<ScanIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>{m.transform_action_fit()}</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={fillCrop}
							>
								<MaximizeIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>{m.transform_action_fill()}</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={resetCrop}
							>
								<RotateCcwIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>{m.transform_action_reset_crop()}</span>
							</Button>
						{:else if activeTab === "affine"}
							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									affineA = 1;
									affineB = 0;
									affineC = 0;
									affineD = 0;
									affineE = 1;
									affineF = 0;
								}}
							>
								<RotateCcwIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>{m.transform_action_reset_matrix()}</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									affineC = 0;
									affineF = 0;
								}}
							>
								<CrosshairIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>{m.transform_action_zero_offset()}</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									affineA = -affineA;
								}}
							>
								<FlipHorizontalIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>{m.transform_action_reflect_x()}</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									affineE = -affineE;
								}}
							>
								<FlipVerticalIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>{m.transform_action_reflect_y()}</span>
								<span>Reflect Y</span>
							</Button>
						{:else if activeTab === "light"}
							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjContrast = 20;
									adjHighlights = -25;
									adjShadows = 35;
									adjWhites = 10;
									adjBlacks = -10;
								}}
							>
								<SunIcon data-icon="inline-start" class="size-3.5" />
								<span>HDR Dynamic</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjContrast = 30;
									adjWhites = 15;
									adjBlacks = -15;
								}}
							>
								<SparklesIcon data-icon="inline-start" class="size-3.5" />
								<span>Pop Contrast</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjBrightness = 15;
									adjExposure = 12;
									adjShadows = 20;
								}}
							>
								<MaximizeIcon data-icon="inline-start" class="size-3.5" />
								<span>Brighten</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={resetLightAdjustments}
							>
								<RotateCcwIcon data-icon="inline-start" class="size-3.5" />
								<span>Reset Light</span>
							</Button>
						{:else if activeTab === "color"}
							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjVibrance = 25;
									adjTemperature = 15;
									adjSaturation = 10;
								}}
							>
								<PaletteIcon data-icon="inline-start" class="size-3.5" />
								<span>Vivid Warm</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjTemperature = -20;
									adjTint = 5;
									adjSaturation = -10;
									adjVibrance = 15;
								}}
							>
								<SparklesIcon data-icon="inline-start" class="size-3.5" />
								<span>Cool Moody</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjSaturation = -30;
									adjVibrance = 15;
									adjTemperature = 18;
									adjTint = -5;
								}}
							>
								<SlidersHorizontalIcon data-icon="inline-start" class="size-3.5" />
								<span>Vintage Film</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={resetColorAdjustments}
							>
								<RotateCcwIcon data-icon="inline-start" class="size-3.5" />
								<span>Reset Color</span>
							</Button>
						{:else if activeTab === "detail"}
							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjSharpness = 40;
									adjClarity = 25;
								}}
							>
								<SparklesIcon data-icon="inline-start" class="size-3.5" />
								<span>Crisp Pop</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjClarity = -25;
									adjBlur = 2;
								}}
							>
								<CrosshairIcon data-icon="inline-start" class="size-3.5" />
								<span>Soft Glow</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={() => {
									adjSharpness = 75;
									adjClarity = 15;
								}}
							>
								<ScanIcon data-icon="inline-start" class="size-3.5" />
								<span>Ultra Sharp</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={resetDetailAdjustments}
							>
								<RotateCcwIcon data-icon="inline-start" class="size-3.5" />
								<span>Reset Detail</span>
							</Button>
						{:else}
							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={centerCrop}
							>
								<CrosshairIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>Center</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={fitToImage}
							>
								<ScanIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>Fit to Image</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={fillCrop}
							>
								<MaximizeIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>Fill</span>
							</Button>

							<Button
								variant="outline"
								size="sm"
								class="h-9 text-xs font-medium gap-1.5 justify-center shadow-xs cursor-pointer border-border"
								onclick={resetCrop}
							>
								<RotateCcwIcon
									data-icon="inline-start"
									class="size-3.5"
								/>
								<span>Reset</span>
							</Button>
						{/if}
					</div>
				</div>
			</Card.Root>
		</div>
	</div>

	<!-- ========================================================================= -->
	<!-- 3. BOTTOM SUMMARY CARD (Original File Info -> Arrow -> Derived Info)      -->
	<!-- ========================================================================= -->
	<Card.Root
		class="shrink-0 border border-border/80 bg-card p-3 sm:p-3.5 rounded-xl shadow-xs flex flex-col sm:flex-row items-center justify-between gap-3"
	>
		<!-- Left: Original Image Info -->
		<div class="flex items-center gap-3.5 w-full sm:w-auto">
			<div
				class="size-12 rounded-lg overflow-hidden border border-border bg-muted shrink-0"
			>
				<img
					src={currentImageUrl}
					alt={originalFilename}
					class="size-full object-cover"
				/>
			</div>
			<div class="space-y-0.5 min-w-0">
				<div
					class="font-bold text-sm text-foreground truncate max-w-[220px] sm:max-w-[340px]"
				>
					{originalFilename}
				</div>
				<div class="text-xs text-muted-foreground font-mono">
					{displayFormat} &bull; {originalWidth} &times; {originalHeight} &bull; {formatFileSize(originalFileSize)}
				</div>
			</div>
		</div>

		<!-- Center: Direction Arrow -->
		<div
			class="hidden sm:flex items-center justify-center text-primary"
		>
			<ArrowRightIcon class="size-5" />
		</div>

		<!-- Right: Derived Transformation Info -->
		<div class="flex flex-col sm:items-end gap-1 w-full sm:w-auto">
			<Badge
				variant="secondary"
				class="bg-primary/10 text-primary border-primary/20 font-semibold px-2.5 py-0.5 w-fit"
			>
				Derived Image ({activeTab
					? activeTab.charAt(0).toUpperCase() + activeTab.slice(1)
					: "Crop"})
			</Badge>
			<div class="text-xs text-muted-foreground font-mono">
				{computedOutputWidth} &times; {computedOutputHeight} &bull; ~{formatFileSize(estimatedDerivedBytes)}
			</div>
		</div>
	</Card.Root>
</div>

<!-- ========================================================================= -->
<!-- 4. UPLOAD IMAGE DIALOG                                                    -->
<!-- ========================================================================= -->
<Dialog.Root bind:open={isUploadDialogOpen}>
	<Dialog.Content class="max-w-md sm:max-w-lg p-5">
		<Dialog.Header class="pb-1">
			<Dialog.Title class="text-base font-bold text-foreground">
				{m.transform_upload_dialog_title()}
			</Dialog.Title>
			<Dialog.Description class="text-xs text-muted-foreground">
				{m.transform_upload_dialog_desc()}
			</Dialog.Description>
		</Dialog.Header>

		{#if uploadError}
			<div
				class="p-2.5 rounded-md border border-destructive/30 bg-destructive/10 text-destructive text-xs flex items-center justify-between"
			>
				<span>{uploadError}</span>
				<button
					type="button"
					class="underline font-bold cursor-pointer"
					onclick={() => (uploadError = null)}>{m.query_dismiss()}</button
				>
			</div>
		{/if}

		<div class="py-2 space-y-3.5">
			<!-- Drop Zone -->
			<div
				role="button"
				tabindex="0"
				aria-label="Upload image drop zone"
				class="relative rounded-xl border-2 border-dashed p-6 flex flex-col items-center justify-center gap-2.5 text-center cursor-pointer transition-all {isDraggingFile
					? 'border-primary bg-primary/5'
					: 'border-border/80 bg-muted/20 hover:border-primary/50 hover:bg-muted/40'}"
				onclick={() => uploadFileInputRef?.click()}
				onkeydown={(e) => {
					if (e.key === "Enter" || e.key === " ") {
						e.preventDefault();
						uploadFileInputRef?.click();
					}
				}}
				ondragover={handleDragOver}
				ondragleave={handleDragLeave}
				ondrop={handleDrop}
			>
				<input
					bind:this={uploadFileInputRef}
					type="file"
					accept="image/png, image/jpeg, image/webp, image/gif, image/tiff"
					class="hidden"
					onchange={(e) => {
						const input = e.currentTarget;
						if (input.files && input.files[0]) {
							handleFileSelected(input.files[0]);
						}
					}}
				/>

				{#if uploadPreviewUrl}
					<!-- Selected File Preview -->
					<div
						class="relative max-h-36 max-w-full rounded-md overflow-hidden border border-border shadow-xs"
					>
						<img
							src={uploadPreviewUrl}
							alt={uploadFile?.name || "Selected Preview"}
							class="max-h-36 max-w-full object-contain"
						/>
					</div>
					<div class="space-y-0.5">
						<p
							class="text-xs font-semibold text-foreground truncate max-w-[260px]"
						>
							{uploadFile?.name}
						</p>
						<p class="text-[11px] font-mono text-muted-foreground">
							{uploadFile
								? (uploadFile.size / 1024).toFixed(1) + " KB"
								: ""}
						</p>
					</div>
					<span class="text-[11px] text-primary underline"
						>Click to choose another image</span
					>
				{:else}
					<div
						class="size-11 rounded-full bg-primary/10 text-primary flex items-center justify-center"
					>
						<UploadCloudIcon class="size-5" />
					</div>
					<div class="space-y-1">
						<p class="text-xs font-semibold text-foreground">
							{m.transform_upload_drop_zone()}
						</p>
						<p class="text-[11px] text-muted-foreground">
							{m.transform_upload_drop_formats()}
						</p>
					</div>
				{/if}
			</div>

			<!-- Optional Category Assignment -->
			{#if categories.length > 0}
				<div class="space-y-1">
					<label
						for="upload-category"
						class="text-xs font-medium text-foreground"
					>
						{m.transform_upload_assign_cat()}
					</label>
					<select
						id="upload-category"
						bind:value={uploadCategoryId}
						class="w-full h-8.5 rounded-md border border-input bg-card px-2.5 text-xs text-foreground shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
					>
						<option value="">{m.transform_upload_no_cat()}</option>
						{#each categories as cat}
							<option value={cat.id}>{cat.name}</option>
						{/each}
					</select>
				</div>
			{/if}

			{#if isUploadingImage && uploadProgress > 0}
				<!-- Progress Bar -->
				<div class="space-y-1">
					<div
						class="flex items-center justify-between text-[11px] font-mono text-muted-foreground"
					>
						<span>{m.transform_upload_uploading()}</span>
						<span>{uploadProgress}%</span>
					</div>
					<div
						class="h-1.5 w-full bg-muted rounded-full overflow-hidden"
					>
						<div
							class="h-full bg-primary transition-all duration-200"
							style="width: {uploadProgress}%;"
						></div>
					</div>
				</div>
			{/if}
		</div>

		<Dialog.Footer
			class="flex justify-between items-center sm:justify-between pt-1"
		>
			<Button
				variant="ghost"
				size="sm"
				class="text-xs"
				onclick={() => {
					isUploadDialogOpen = false;
					uploadFile = null;
					if (uploadPreviewUrl) {
						URL.revokeObjectURL(uploadPreviewUrl);
						uploadPreviewUrl = null;
					}
				}}
			>
				{m.settings_cancel()}
			</Button>

			<Button
				size="sm"
				class="text-xs font-semibold"
				disabled={!uploadFile || isUploadingImage}
				onclick={submitUpload}
			>
				{#if isUploadingImage}
					<Loader2Icon class="size-3.5 animate-spin mr-1.5" />
					<span>{m.transform_upload_uploading()}</span>
				{:else}
					<span>{m.transform_upload_load_canvas()}</span>
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
