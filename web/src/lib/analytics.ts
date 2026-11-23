import { auth } from "./auth.js";

const API_BASE = "/api/v1";

export interface AnalyticsOverview {
	total_searches: number;
	feedback_sessions: number;
	average_iterations: number;
	average_retrieval_time_ms: number;
	failed_retrievals: number;
	total_feedback_judgments: number;
	relevant_judgments: number;
	irrelevant_judgments: number;
}

export interface ActivityPoint {
	date: string;
	searches: number;
	iterations: number;
}

export interface AnalyticsActivity {
	activity_timeline: ActivityPoint[];
	scope_distribution: Record<string, number>;
	metric_distribution: Record<string, number>;
}

export interface AnalyticsFeedback {
	relevant_count: number;
	irrelevant_count: number;
	ratio: number;
	average_judgments_per_search: number;
	feature_weight_evolution: Record<string, Record<string, number>>;
}

export interface AnalyticsDescriptors {
	descriptor_usage: Record<string, number>;
	categories: {
		hybrid: number;
		color_only: number;
		texture_only: number;
	};
}

export interface LatencyPoint {
	iteration_id: string;
	iteration_number: number;
	execution_time_ms: number;
	candidates: number;
	results: number;
	created_at: string;
}

export interface LatencyStage {
	id: string;
	name: string;
	short_name: string;
	ms: number;
	percentage: number;
	description: string;
	complexity: string;
	color: string;
}

export interface StageBreakdown {
	extraction_ms: number;
	db_fetch_ms: number;
	similarity_ms: number;
	reranking_ms: number;
	stages: LatencyStage[];
}

export interface AnalyticsPerformance {
	average_ms: number;
	min_ms: number;
	max_ms: number;
	stage_breakdown?: StageBreakdown;
	recent_latencies: LatencyPoint[];
}

export interface RetrievalResultItem {
	id: string;
	rank: number;
	image_id: string;
	similarity_score: number;
	feature_scores?: Record<string, number>;
	image?: {
		id: string;
		filename: string;
		category_name?: string;
		width?: number;
		height?: number;
		file_size?: number;
		source_type?: string;
	};
}

export interface RelevanceFeedbackItem {
	id: string;
	image_id: string;
	judgment: "relevant" | "irrelevant";
	image?: {
		id: string;
		filename: string;
		category_name?: string;
	};
}

export interface RetrievalIterationDetail {
	id: string;
	iteration_number: number;
	retrieval_method: string;
	feature_weights: Record<string, number>;
	feedback_count: number;
	execution_time_ms: number;
	total_candidates: number;
	results_count: number;
	created_at: string;
	results?: RetrievalResultItem[];
	feedback?: RelevanceFeedbackItem[];
}

export interface RetrievalQueryDetail {
	id: string;
	query_image_id?: string | null;
	query_storage_key?: string | null;
	query_source: "upload" | "gallery";
	search_scope: string;
	configuration: Record<string, any>;
	status: string;
	created_at: string;
	completed_at?: string | null;
	iterations_count: number;
	query_image?: {
		id: string;
		filename: string;
		width: number;
		height: number;
	};
	iterations?: RetrievalIterationDetail[];
}

export interface HistoryListResponse {
	success: boolean;
	items: RetrievalQueryDetail[];
	pagination: {
		page: number;
		per_page: number;
		total_items: number;
		total_pages: number;
		has_next: boolean;
		has_prev: boolean;
	};
}

export const analyticsClient = {
	async getOverview(): Promise<AnalyticsOverview> {
		const res = await auth.fetchWithAuth(`${API_BASE}/analytics/overview`);
		const data = await res.json();
		return data;
	},

	async getActivity(): Promise<AnalyticsActivity> {
		const res = await auth.fetchWithAuth(`${API_BASE}/analytics/activity`);
		const data = await res.json();
		return data;
	},

	async getFeedback(): Promise<AnalyticsFeedback> {
		const res = await auth.fetchWithAuth(`${API_BASE}/analytics/feedback`);
		const data = await res.json();
		return data;
	},

	async getDescriptors(): Promise<AnalyticsDescriptors> {
		const res = await auth.fetchWithAuth(`${API_BASE}/analytics/descriptors`);
		const data = await res.json();
		return data;
	},

	async getPerformance(): Promise<AnalyticsPerformance> {
		const res = await auth.fetchWithAuth(`${API_BASE}/analytics/performance`);
		const data = await res.json();
		return data;
	},

	async listHistory(page = 1, perPage = 15): Promise<HistoryListResponse> {
		const res = await auth.fetchWithAuth(`${API_BASE}/retrieval-history?page=${page}&per_page=${perPage}`);
		const data = await res.json();
		return data;
	},

	async getHistoryDetail(queryId: string): Promise<RetrievalQueryDetail> {
		const res = await auth.fetchWithAuth(`${API_BASE}/retrieval-history/${queryId}`);
		const data = await res.json();
		return data.query;
	},

	async deleteHistory(queryId: string): Promise<boolean> {
		const res = await auth.fetchWithAuth(`${API_BASE}/retrieval-history/${queryId}`, {
			method: "DELETE",
		});
		return res.ok;
	},
};
