import { auth } from "./auth.js";

export interface CategoryItem {
	id: string;
	user_id?: string;
	parent_id?: string | null;
	name: string;
	created_at?: string | null;
	image_count?: number;
	children?: CategoryItem[];
}

export interface CategoryApiResponse<T = any> {
	success: boolean;
	error?: string;
	message?: string;
	category?: T;
	categories?: T[];
}

export interface CreateCategoryPayload {
	name: string;
	parent_id?: string | null;
}

export interface UpdateCategoryPayload {
	name?: string;
	parent_id?: string | null;
}

class CategoryService {
	private get apiBase() {
		return auth.apiBase;
	}

	private getHeaders(): HeadersInit {
		return {
			"Content-Type": "application/json"
		};
	}

	/**
	 * Fetch all categories, optionally as a nested tree and with image counts.
	 */
	async getCategories(options: { tree?: boolean; include_counts?: boolean; scope?: "user" | "dataset" | "all" } = {}): Promise<CategoryItem[]> {
		const params = new URLSearchParams();
		if (options.tree !== undefined) params.set("tree", String(options.tree));
		if (options.include_counts !== undefined) params.set("include_counts", String(options.include_counts));
		if (options.scope !== undefined) params.set("scope", options.scope);

		const queryString = params.toString() ? `?${params.toString()}` : "";
		const res = await auth.fetchWithAuth(`${this.apiBase}/categories${queryString}`, {
			method: "GET",
			headers: this.getHeaders()
		});

		const data: CategoryApiResponse<CategoryItem> = await res.json();
		if (!res.ok || !data.success) {
			throw new Error(data.error || "Failed to fetch categories");
		}
		return data.categories || [];
	}

	/**
	 * Get a single category by ID.
	 */
	async getCategory(id: string): Promise<CategoryItem> {
		const res = await auth.fetchWithAuth(`${this.apiBase}/categories/${id}`, {
			method: "GET",
			headers: this.getHeaders()
		});

		const data: CategoryApiResponse<CategoryItem> = await res.json();
		if (!res.ok || !data.success || !data.category) {
			throw new Error(data.error || "Category not found");
		}
		return data.category;
	}

	/**
	 * Create a new category.
	 */
	async createCategory(payload: CreateCategoryPayload): Promise<CategoryItem> {
		const res = await auth.fetchWithAuth(`${this.apiBase}/categories`, {
			method: "POST",
			headers: this.getHeaders(),
			body: JSON.stringify(payload)
		});

		const data: CategoryApiResponse<CategoryItem> = await res.json();
		if (!res.ok || !data.success || !data.category) {
			throw new Error(data.error || "Failed to create category");
		}
		return data.category;
	}

	/**
	 * Update category name and/or parent_id.
	 */
	async updateCategory(id: string, payload: UpdateCategoryPayload): Promise<CategoryItem> {
		const res = await auth.fetchWithAuth(`${this.apiBase}/categories/${id}`, {
			method: "PATCH",
			headers: this.getHeaders(),
			body: JSON.stringify(payload)
		});

		const data: CategoryApiResponse<CategoryItem> = await res.json();
		if (!res.ok || !data.success || !data.category) {
			throw new Error(data.error || "Failed to update category");
		}
		return data.category;
	}

	/**
	 * Delete category by ID.
	 */
	async deleteCategory(id: string): Promise<void> {
		const res = await auth.fetchWithAuth(`${this.apiBase}/categories/${id}`, {
			method: "DELETE",
			headers: this.getHeaders()
		});

		const data: CategoryApiResponse = await res.json();
		if (!res.ok || !data.success) {
			throw new Error(data.error || "Failed to delete category");
		}
	}
}

export const categoryService = new CategoryService();
