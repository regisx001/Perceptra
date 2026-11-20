import { auth } from "./auth.js";

export interface VisualQueryResultItem {
	rank: number;
	image_id: string;
	filename: string;
	category_id?: string | null;
	category: string;
	source_type: string;
	dimensions: string;
	file_size: number;
	overall_similarity: number;
	color_similarity: number;
	texture_similarity: number;
	feature_scores: Record<string, number>;
}

export interface ExecutionTimeBreakdown {
	extraction_ms: number;
	similarity_ms: number;
	total_ms: number;
}

export interface QuerySearchResponse {
	success: boolean;
	session_id: string;
	query_image: {
		source: "upload" | "existing";
		id?: string;
		filename: string;
		category_id?: string | null;
		category_name?: string | null;
		width?: number;
		height?: number;
	};
	execution_time_ms: ExecutionTimeBreakdown;
	active_weights: Record<string, number>;
	results: VisualQueryResultItem[];
	total_candidates: number;
	error?: string;
}

export interface QueryFeedbackResponse {
	success: boolean;
	session_id: string;
	iteration: number;
	execution_time_ms: number;
	updated_weights: Record<string, number>;
	prior_weights: Record<string, number>;
	diagnostics: Record<string, any>;
	precision_at_k: number | null;
	results: VisualQueryResultItem[];
	error?: string;
}

export interface QueryConfigResponse {
	success: boolean;
	supported_descriptors: string[];
	color_descriptors: string[];
	texture_descriptors: string[];
	similarity_metrics: { id: string; label: string; default?: boolean }[];
	normalization_methods: { id: string; label: string; default?: boolean }[];
	search_scopes: { id: string; label: string; default?: boolean }[];
	default_top_k: number;
	max_top_k: number;
	descriptor_defaults: Record<string, any>;
	error?: string;
}

export interface QuerySearchPayload {
	file?: File;
	image_id?: string;
	scope?: string;
	category_id?: string | null;
	top_k?: number;
	metric?: string;
	normalization?: string;
	descriptors?: string[];
	weights?: Record<string, number>;
}

export interface QueryFeedbackPayload {
	session_id: string;
	relevant_ids: string[];
	irrelevant_ids: string[];
	iteration?: number;
}

class QueryEngineClient {
	private get apiBase() {
		return auth.apiBase;
	}

	async getConfig(): Promise<QueryConfigResponse> {
		const res = await auth.fetchWithAuth(`${this.apiBase}/query/config`);
		const data = await res.json();
		if (!res.ok || !data.success) {
			throw new Error(data.error || "Failed to load visual query configuration");
		}
		return data;
	}

	async search(payload: QuerySearchPayload): Promise<QuerySearchResponse> {
		let res: Response;

		if (payload.file) {
			const formData = new FormData();
			formData.append("file", payload.file, payload.file.name);
			if (payload.scope) formData.append("scope", payload.scope);
			if (payload.category_id && payload.category_id !== "all") {
				formData.append("category_id", payload.category_id);
			}
			if (payload.top_k) formData.append("top_k", String(payload.top_k));
			if (payload.metric) formData.append("metric", payload.metric);
			if (payload.normalization) formData.append("normalization", payload.normalization);
			if (payload.descriptors) {
				formData.append("descriptors", JSON.stringify(payload.descriptors));
			}
			if (payload.weights) {
				formData.append("weights", JSON.stringify(payload.weights));
			}

			res = await auth.fetchWithAuth(`${this.apiBase}/query/search`, {
				method: "POST",
				body: formData,
			});
		} else {
			res = await auth.fetchWithAuth(`${this.apiBase}/query/search`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					image_id: payload.image_id,
					scope: payload.scope || "both",
					category_id: payload.category_id !== "all" ? payload.category_id : null,
					top_k: payload.top_k || 12,
					metric: payload.metric || "cosine",
					normalization: payload.normalization || "none",
					descriptors: payload.descriptors,
					weights: payload.weights,
				}),
			});
		}

		const data = await res.json();
		if (!res.ok || !data.success) {
			throw new Error(data.error || `Search failed with status ${res.status}`);
		}
		return data;
	}

	async feedback(payload: QueryFeedbackPayload): Promise<QueryFeedbackResponse> {
		const res = await auth.fetchWithAuth(`${this.apiBase}/query/feedback`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(payload),
		});

		const data = await res.json();
		if (!res.ok || !data.success) {
			throw new Error(data.error || `Feedback submission failed with status ${res.status}`);
		}
		return data;
	}
}

export const queryEngineClient = new QueryEngineClient();
