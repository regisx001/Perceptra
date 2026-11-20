export interface User {
	id: number;
	email: string;
	created_at?: string;
}

export interface AuthResponse {
	success: boolean;
	message?: string;
	access_token?: string;
	refresh_token?: string;
	user?: User;
	error?: string;
}

class AuthService {
	private tokenKey = 'cbir_auth_token';
	private refreshTokenKey = 'cbir_refresh_token';
	private userKey = 'cbir_auth_user';
	public apiBase = '/api/v1';

	// In-flight refresh promise to prevent multiple simultaneous refresh requests
	private refreshPromise: Promise<string | null> | null = null;

	getToken(): string | null {
		if (typeof window === 'undefined') return null;
		return localStorage.getItem(this.tokenKey);
	}

	getRefreshToken(): string | null {
		if (typeof window === 'undefined') return null;
		return localStorage.getItem(this.refreshTokenKey);
	}

	getUser(): User | null {
		if (typeof window === 'undefined') return null;
		const raw = localStorage.getItem(this.userKey);
		if (!raw) return null;
		try {
			return JSON.parse(raw);
		} catch {
			return null;
		}
	}

	setSession(token: string, refreshToken?: string, user?: User): void {
		if (typeof window === 'undefined') return;
		localStorage.setItem(this.tokenKey, token);
		if (refreshToken) {
			localStorage.setItem(this.refreshTokenKey, refreshToken);
		}
		if (user) {
			localStorage.setItem(this.userKey, JSON.stringify(user));
		}
	}

	clearSession(): void {
		if (typeof window === 'undefined') return;
		localStorage.removeItem(this.tokenKey);
		localStorage.removeItem(this.refreshTokenKey);
		localStorage.removeItem(this.userKey);
	}

	isAuthenticated(): boolean {
		return !!(this.getToken() || this.getRefreshToken());
	}

	/**
	 * Refreshes the access token using the stored refresh token.
	 * Handles token rotation and deduplicates concurrent refresh calls.
	 */
	async refreshToken(): Promise<string | null> {
		if (typeof window === 'undefined') return null;

		if (this.refreshPromise) {
			return this.refreshPromise;
		}

		this.refreshPromise = (async () => {
			const refreshToken = this.getRefreshToken();
			if (!refreshToken) {
				this.clearSession();
				return null;
			}

			try {
				const res = await fetch(`${this.apiBase}/auth/refresh`, {
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
						Authorization: `Bearer ${refreshToken}`,
					},
					body: JSON.stringify({ refresh_token: refreshToken }),
				});

				if (!res.ok) {
					this.clearSession();
					return null;
				}

				const data: AuthResponse = await res.json();
				if (data.access_token) {
					this.setSession(data.access_token, data.refresh_token, data.user);
					return data.access_token;
				}

				this.clearSession();
				return null;
			} catch {
				this.clearSession();
				return null;
			} finally {
				this.refreshPromise = null;
			}
		})();

		return this.refreshPromise;
	}

	/**
	 * Authenticated fetch wrapper.
	 * Automatically injects the access token and refreshes it on 401 before retrying once.
	 */
	async fetchWithAuth(input: RequestInfo | URL, init: RequestInit = {}): Promise<Response> {
		const token = this.getToken();
		const headers = new Headers(init.headers || {});
		if (token && !headers.has('Authorization')) {
			headers.set('Authorization', `Bearer ${token}`);
		}

		let response = await fetch(input, { ...init, headers });

		if (response.status === 401) {
			const newToken = await this.refreshToken();
			if (newToken) {
				const retryHeaders = new Headers(init.headers || {});
				retryHeaders.set('Authorization', `Bearer ${newToken}`);
				response = await fetch(input, { ...init, headers: retryHeaders });
			} else {
				this.clearSession();
				if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
					window.location.href = '/login';
				}
			}
		}

		return response;
	}

	async register(email: string, password: string): Promise<AuthResponse> {
		const res = await fetch(`${this.apiBase}/auth/register`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, password }),
		});
		const data: AuthResponse = await res.json();
		if (!res.ok) {
			throw new Error(data.error || 'Registration failed');
		}
		if (data.access_token && data.user) {
			this.setSession(data.access_token, data.refresh_token, data.user);
		}
		return data;
	}

	async login(email: string, password: string): Promise<AuthResponse> {
		const res = await fetch(`${this.apiBase}/auth/login`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, password }),
		});
		const data: AuthResponse = await res.json();
		if (!res.ok) {
			throw new Error(data.error || 'Login failed');
		}
		if (data.access_token && data.user) {
			this.setSession(data.access_token, data.refresh_token, data.user);
		}
		return data;
	}

	async fetchCurrentUser(): Promise<User | null> {
		if (!this.isAuthenticated()) {
			this.clearSession();
			return null;
		}

		try {
			const res = await this.fetchWithAuth(`${this.apiBase}/auth/me`);
			if (!res.ok) {
				this.clearSession();
				return null;
			}
			const data = await res.json();
			if (data.user) {
				if (typeof window !== 'undefined') {
					localStorage.setItem(this.userKey, JSON.stringify(data.user));
				}
				return data.user;
			}
			return null;
		} catch {
			return null;
		}
	}

	logout(): void {
		this.clearSession();
	}
}

export const auth = new AuthService();
