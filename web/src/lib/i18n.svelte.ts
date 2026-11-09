import { getLocale, setLocale as paraglideSetLocale, type Locale, locales, baseLocale } from './paraglide/runtime.js';
import { overwriteGetLocale, overwriteSetLocale } from './paraglide/runtime.js';

let currentLocaleState = $state<Locale>(baseLocale);

// Initialize on client
if (typeof window !== 'undefined') {
	try {
		currentLocaleState = getLocale();
	} catch {
		currentLocaleState = baseLocale;
	}

	// Wire paraglide to read from the reactive state
	overwriteGetLocale(() => currentLocaleState);

	// Wire paraglide to update reactive state without full page reload
	overwriteSetLocale((newLocale: Locale, options?: { reload?: boolean }) => {
		currentLocaleState = newLocale;
		// Update cookie / storage in the background without reloading
		try {
			document.cookie = `PARAGLIDE_LOCALE=${newLocale}; path=/; max-age=31536000; SameSite=Lax`;
		} catch {
			// ignore cookie errors
		}
		if (options?.reload) {
			window.location.reload();
		}
	});
}

/**
 * Reactive accessor for the current active locale.
 */
export function useLocale() {
	return {
		get current(): Locale {
			return currentLocaleState;
		},
		set(next: Locale) {
			currentLocaleState = next;
			if (typeof document !== 'undefined') {
				try {
					document.cookie = `PARAGLIDE_LOCALE=${next}; path=/; max-age=31536000; SameSite=Lax`;
				} catch {
					// ignore
				}
			}
		},
		toggle() {
			const next = currentLocaleState === 'en' ? 'fr' : 'en';
			this.set(next);
		}
	};
}

export { locales, baseLocale };
