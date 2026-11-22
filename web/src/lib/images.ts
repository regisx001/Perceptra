import { auth } from "./auth.js";

export interface ImageItem {
	id: string;
	owner_id: string;
	category_id?: string | null;
	parent_image_id?: string | null;
	filename: string;
	storage_key: string;
	source_type: string;
	processing_status: "pending" | "processing" | "indexed" | "completed" | "failed" | string;
	mime_type: string;
	file_size: number;
	width?: number | null;
	height?: number | null;
	checksum?: string | null;
	transformation_params?: any;
	is_favorite?: boolean;
	created_at?: string;
}

export interface ColorHistogramFeature {
	channels: {
		h: number[];
		s: number[];
		v: number[];
	};
	vector: number[];
}

export interface ColorMomentsFeature {
	channels: {
		h: { mean: number; std: number; skewness: number };
		s: { mean: number; std: number; skewness: number };
		v: { mean: number; std: number; skewness: number };
	};
	vector: number[];
}

export interface DominantColorCluster {
	rank: number;
	rgb: [number, number, number];
	hex: string;
	percentage: number;
}

export interface DominantColorsFeature {
	clusters: DominantColorCluster[];
	vector: number[];
}

export interface GlcmMetricSet {
	contrast: number;
	correlation: number;
	energy: number;
	homogeneity: number;
}

export interface GlcmFeature {
	summary: GlcmMetricSet;
	by_angle: Record<string, GlcmMetricSet>;
	vector: number[];
}

export interface LbpHistogramFeature {
	bins: number[];
	labels: string[];
	vector: number[];
}

export interface DescriptorsMap {
	color_histogram?: ColorHistogramFeature;
	color_moments?: ColorMomentsFeature;
	dominant_colors?: DominantColorsFeature;
	dominant_colors_10?: DominantColorsFeature;
	dominant_colors_20?: DominantColorsFeature;
	glcm?: GlcmFeature;
	lbp_histogram?: LbpHistogramFeature;
	[key: string]: any;
}

export interface ImageDescriptorsResponse {
	success: boolean;
	image_id: string;
	processing_status: string;
	available_features: string[];
	descriptors: DescriptorsMap;
	error?: string;
}

export interface ExtractDescriptorsResponse {
	success: boolean;
	image_id: string;
	processing_status: string;
	descriptors: DescriptorsMap;
	error?: string;
}

export interface ImagePagination {
	page: number;
	per_page: number;
	total: number;
	pages: number;
}

export interface ListImagesResponse {
	success: boolean;
	images: ImageItem[];
	pagination: ImagePagination;
	error?: string;
}

export interface UploadImageResponse {
	success: boolean;
	image?: ImageItem;
	error?: string;
}

export interface BulkAssignResponse {
	success: boolean;
	updated_count?: number;
	error?: string;
}

export interface BulkDeleteResponse {
	success: boolean;
	deleted_count?: number;
	error?: string;
}

export interface ListImagesOptions {
	category_id?: string | null;
	uncategorized?: boolean;
	favorites?: boolean;
	page?: number;
	per_page?: number;
}

class ImageService {
	private get apiBase() {
		return auth.apiBase;
	}

	private getHeaders(contentType?: string): HeadersInit {
		const headers: Record<string, string> = {};
		if (contentType) {
			headers["Content-Type"] = contentType;
		}
		return headers;
	}

	/**
	 * Upload an image file with optional category assignment.
	 * Calls POST /api/v1/images with multipart/form-data.
	 */
	async uploadImage(
		file: File,
		categoryId?: string | null,
		onProgress?: (percent: number) => void
	): Promise<ImageItem> {
		const executeUpload = (token: string | null): Promise<ImageItem> => {
			return new Promise((resolve, reject) => {
				const xhr = new XMLHttpRequest();
				const url = `${this.apiBase}/images`;

				xhr.open("POST", url, true);

				if (token) {
					xhr.setRequestHeader("Authorization", `Bearer ${token}`);
				}

				if (xhr.upload && onProgress) {
					xhr.upload.onprogress = (e) => {
						if (e.lengthComputable) {
							const percent = Math.round((e.loaded / e.total) * 100);
							onProgress(percent);
						}
					};
				}

				xhr.onload = async () => {
					try {
						if (xhr.status === 401) {
							const newToken = await auth.refreshToken();
							if (newToken) {
								try {
									const retried = await executeUpload(newToken);
									resolve(retried);
									return;
								} catch (retryErr) {
									reject(retryErr);
									return;
								}
							}
						}

						const data = JSON.parse(xhr.responseText || "{}");
						if (xhr.status >= 200 && xhr.status < 300 && data.success && data.image) {
							resolve(data.image);
						} else {
							reject(new Error(data.error || `Upload failed with status ${xhr.status}`));
						}
					} catch (err: any) {
						reject(new Error(`Failed to parse response: ${err.message}`));
					}
				};

				xhr.onerror = () => {
					reject(new Error("Network error during file upload"));
				};

				const formData = new FormData();
				formData.append("file", file, file.name);
				if (categoryId && categoryId !== "uncategorized") {
					formData.append("category_id", categoryId);
				}

				xhr.send(formData);
			});
		};

		return executeUpload(auth.getToken());
	}

	/**
	 * List images for the authenticated user with optional category filter.
	 * Calls GET /api/v1/images
	 */
	async listImages(options: ListImagesOptions = {}): Promise<ListImagesResponse> {
		const params = new URLSearchParams();
		if (options.category_id) {
			params.set("category_id", options.category_id);
		}
		if (options.uncategorized) {
			params.set("uncategorized", "true");
		}
		if (options.favorites) {
			params.set("favorites", "true");
		}
		if (options.page !== undefined) {
			params.set("page", String(options.page));
		}
		if (options.per_page !== undefined) {
			params.set("per_page", String(options.per_page));
		}

		const query = params.toString() ? `?${params.toString()}` : "";
		const response = await auth.fetchWithAuth(`${this.apiBase}/images${query}`, {
			method: "GET",
			headers: this.getHeaders("application/json")
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to fetch images (${response.status})`);
		}

		return data;
	}

	/**
	 * Get metadata for a single image.
	 * Calls GET /api/v1/images/:id
	 */
	async getImage(imageId: string): Promise<ImageItem> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}`, {
			method: "GET",
			headers: this.getHeaders("application/json")
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to get image (${response.status})`);
		}

		return data.image;
	}

	/**
	 * Returns the direct stream URL for an image, including the JWT auth token if available.
	 */
	getImageFileUrl(imageId: string, download = false): string {
		const token = auth.getToken();
		const params = new URLSearchParams();
		if (download) {
			params.set("download", "true");
		}
		if (token) {
			params.set("token", token);
		}
		const query = params.toString() ? `?${params.toString()}` : "";
		return `${this.apiBase}/images/${encodeURIComponent(imageId)}/file${query}`;
	}

	/**
	 * Alias for getImageFileUrl.
	 */
	getImageUrl(imageId: string, download = false): string {
		return this.getImageFileUrl(imageId, download);
	}

	/**
	 * Update an image's category assignment.
	 * Calls PATCH /api/v1/images/:id
	 */
	async updateCategory(imageId: string, categoryId: string | null): Promise<ImageItem> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}`, {
			method: "PATCH",
			headers: this.getHeaders("application/json"),
			body: JSON.stringify({ category_id: categoryId })
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to update image category (${response.status})`);
		}

		return data.image;
	}

	/**
	 * Bulk assign or unassign category for multiple images.
	 * Calls POST /api/v1/images/bulk-assign
	 */
	async bulkAssign(imageIds: string[], categoryId: string | null): Promise<number> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/bulk-assign`, {
			method: "POST",
			headers: this.getHeaders("application/json"),
			body: JSON.stringify({
				image_ids: imageIds,
				category_id: categoryId
			})
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to bulk assign (${response.status})`);
		}

		return data.updated_count ?? 0;
	}

	/**
	 * Delete single image.
	 * Calls DELETE /api/v1/images/:id
	 */
	async deleteImage(imageId: string): Promise<void> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}`, {
			method: "DELETE",
			headers: this.getHeaders("application/json")
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to delete image (${response.status})`);
		}
	}

	/**
	 * Bulk delete images.
	 * Calls POST /api/v1/images/bulk-delete
	 */
	async bulkDelete(imageIds: string[]): Promise<number> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/bulk-delete`, {
			method: "POST",
			headers: this.getHeaders("application/json"),
			body: JSON.stringify({ image_ids: imageIds })
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to bulk delete (${response.status})`);
		}

		return data.deleted_count ?? 0;
	}

	/**
	 * Validate transformation dimensions without modifying files.
	 * Calls POST /api/v1/images/:id/transform-validate
	 */
	async validateTransform(
		imageId: string,
		operation: string,
		params: Record<string, any>
	): Promise<{
		success: boolean;
		image_id: string;
		original_width: number;
		original_height: number;
		new_width: number;
		new_height: number;
		aspect_ratio: number;
		operation: string;
		params: Record<string, any>;
	}> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}/transform-validate`, {
			method: "POST",
			headers: this.getHeaders("application/json"),
			body: JSON.stringify({ operation, params })
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to validate transformation (${response.status})`);
		}

		return data;
	}

	/**
	 * Execute transformation creating a derived image.
	 * Calls POST /api/v1/images/:id/transform
	 */
	async transformImage(
		imageId: string,
		payload: {
			operation: string;
			params: Record<string, any>;
			filename?: string;
			category_id?: string | number | null;
		}
	): Promise<ImageItem> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}/transform`, {
			method: "POST",
			headers: this.getHeaders("application/json"),
			body: JSON.stringify(payload)
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to transform image (${response.status})`);
		}

		return data.image;
	}

	/**
	 * List all derived images from a parent image.
	 * Calls GET /api/v1/images/:id/derivatives
	 */
	async getDerivatives(imageId: string): Promise<ImageItem[]> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}/derivatives`, {
			method: "GET",
			headers: this.getHeaders("application/json")
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to get derivatives (${response.status})`);
		}

		return data.derivatives || [];
	}

	/**
	 * Retrieve stored visual descriptors for an image.
	 * Calls GET /api/v1/images/:id/descriptors
	 */
	async getImageDescriptors(imageId: string): Promise<ImageDescriptorsResponse> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}/descriptors`, {
			method: "GET",
			headers: this.getHeaders("application/json")
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to fetch descriptors (${response.status})`);
		}

		return data;
	}

	/**
	 * Extract or recompute visual descriptors for an image.
	 * Calls POST /api/v1/descriptors/extract/:id
	 */
	async extractDescriptors(
		imageId: string,
		payload?: { feature_types?: string[]; force?: boolean }
	): Promise<ExtractDescriptorsResponse> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/descriptors/extract/${encodeURIComponent(imageId)}`, {
			method: "POST",
			headers: this.getHeaders("application/json"),
			body: JSON.stringify(payload || {})
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to extract descriptors (${response.status})`);
		}

		return data;
	}

	/**
	 * Toggle favorite status of an image.
	 * Calls POST /api/v1/images/:id/favorite
	 */
	async toggleFavorite(imageId: string): Promise<{ is_favorite: boolean; message: string }> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}/favorite`, {
			method: "POST",
			headers: this.getHeaders("application/json"),
		});

		const data = await response.json();
		if (!response.ok || !data.success) {
			throw new Error(data.error || `Failed to toggle favorite (${response.status})`);
		}

		return {
			is_favorite: Boolean(data.is_favorite),
			message: data.message,
		};
	}

	/**
	 * Update image metadata such as category_id or filename.
	 * Calls PATCH /api/v1/images/:id
	 */
	async updateImage(imageId: string, payload: { category_id?: string | null; filename?: string }): Promise<ImageItem> {
		const response = await auth.fetchWithAuth(`${this.apiBase}/images/${encodeURIComponent(imageId)}`, {
			method: "PATCH",
			headers: this.getHeaders("application/json"),
			body: JSON.stringify(payload)
		});

		const data = await response.json();
		if (!response.ok || !data.success || !data.image) {
			throw new Error(data.error || `Failed to update image (${response.status})`);
		}

		return data.image;
	}
}

export const imageService = new ImageService();
