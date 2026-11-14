import { auth } from "./auth.js";

export interface ImageItem {
	id: string;
	owner_id: string;
	category_id?: string | null;
	parent_image_id?: string | null;
	filename: string;
	storage_key: string;
	source_type: string;
	processing_status: "pending" | "processing" | "completed" | "failed";
	mime_type: string;
	file_size: number;
	width?: number | null;
	height?: number | null;
	checksum?: string | null;
	transformation_params?: any;
	created_at?: string;
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
	page?: number;
	per_page?: number;
}

class ImageService {
	private get apiBase() {
		return auth.apiBase;
	}

	private getHeaders(contentType?: string): HeadersInit {
		const token = auth.getToken();
		const headers: Record<string, string> = {};
		if (contentType) {
			headers["Content-Type"] = contentType;
		}
		if (token) {
			headers["Authorization"] = `Bearer ${token}`;
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
		return new Promise((resolve, reject) => {
			const xhr = new XMLHttpRequest();
			const url = `${this.apiBase}/images`;

			xhr.open("POST", url, true);

			const token = auth.getToken();
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

			xhr.onload = () => {
				try {
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
		if (options.page !== undefined) {
			params.set("page", String(options.page));
		}
		if (options.per_page !== undefined) {
			params.set("per_page", String(options.per_page));
		}

		const query = params.toString() ? `?${params.toString()}` : "";
		const response = await fetch(`${this.apiBase}/images${query}`, {
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
		const response = await fetch(`${this.apiBase}/images/${encodeURIComponent(imageId)}`, {
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
	 * Update an image's category assignment.
	 * Calls PATCH /api/v1/images/:id
	 */
	async updateCategory(imageId: string, categoryId: string | null): Promise<ImageItem> {
		const response = await fetch(`${this.apiBase}/images/${encodeURIComponent(imageId)}`, {
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
		const response = await fetch(`${this.apiBase}/images/bulk-assign`, {
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
		const response = await fetch(`${this.apiBase}/images/${encodeURIComponent(imageId)}`, {
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
		const response = await fetch(`${this.apiBase}/images/bulk-delete`, {
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
}

export const imageService = new ImageService();
