export interface User {
	id: number;
	email: string;
	created_at?: string;
}

export interface AuthResponse {
	success: boolean;
	message?: string;
	access_token?: string;
	user?: User;
	error?: string;
}

class AuthService {
	private tokenKey = 'cbir_auth_token';
	private userKey = 'cbir_auth_user';
	public apiBase = '/api/v1';

	getToken(): string | null {
		if (typeof window === 'undefined') return null;
		return localStorage.getItem(this.tokenKey);
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

	setSession(token: string, user: User): void {
		if (typeof window === 'undefined') return;
		localStorage.setItem(this.tokenKey, token);
		localStorage.setItem(this.userKey, JSON.stringify(user));
	}

	clearSession(): void {
		if (typeof window === 'undefined') return;
		localStorage.removeItem(this.tokenKey);
		localStorage.removeItem(this.userKey);
	}

	isAuthenticated(): boolean {
		return !!this.getToken();
	}

	async register(email: string, password: string): Promise<AuthResponse> {
		const res = await fetch(`${this.apiBase}/auth/register`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, password }),
		});
		const data = await res.json();
		if (!res.ok) {
			throw new Error(data.error || 'Registration failed');
		}
		if (data.access_token && data.user) {
			this.setSession(data.access_token, data.user);
		}
		return data;
	}

	async login(email: string, password: string): Promise<AuthResponse> {
		const res = await fetch(`${this.apiBase}/auth/login`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ email, password }),
		});
		const data = await res.json();
		if (!res.ok) {
			throw new Error(data.error || 'Login failed');
		}
		if (data.access_token && data.user) {
			this.setSession(data.access_token, data.user);
		}
		return data;
	}

	async fetchCurrentUser(): Promise<User | null> {
		const token = this.getToken();
		if (!token) {
			this.clearSession();
			return null;
		}
		try {
			const res = await fetch(`${this.apiBase}/auth/me`, {
				headers: {
					Authorization: `Bearer ${token}`,
				},
			});
			if (!res.ok) {
				this.clearSession();
				return null;
			}
			const data = await res.json();
			if (data.user) {
				localStorage.setItem(this.userKey, JSON.stringify(data.user));
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
