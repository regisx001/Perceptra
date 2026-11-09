import { describe, it, expect } from 'vitest';
import * as m from '#lib/paraglide/messages.js';
import { locales, baseLocale, setLocale, getLocale } from '#lib/paraglide/runtime.js';

describe('Paraglide i18n setup', () => {
	it('defines supported locales and default baseLocale', () => {
		expect(baseLocale).toBe('en');
		expect(locales).toContain('en');
		expect(locales).toContain('fr');
		expect(locales).toHaveLength(2);
	});

	it('returns localized messages in English', () => {
		setLocale('en');
		expect(getLocale()).toBe('en');
		expect(m.app_title()).toBe('Content-Based Image Retrieval');
		expect(m.welcome()).toBe('Welcome to SvelteKit');
		expect(m.example_message({ username: 'Alice' })).toBe('Hello world Alice');
		expect(m.auth_login_title()).toBe('Welcome back');
	});

	it('returns localized messages in French', () => {
		setLocale('fr');
		expect(getLocale()).toBe('fr');
		expect(m.app_title()).toBe("Recherche d'images par le contenu");
		expect(m.welcome()).toBe('Bienvenue sur SvelteKit');
		expect(m.example_message({ username: 'Alice' })).toBe('Bonjour Alice');
		expect(m.auth_login_title()).toBe('Bon retour');
	});

	it('supports per-call locale override', () => {
		expect(m.app_title({}, { locale: 'fr' })).toBe("Recherche d'images par le contenu");
		expect(m.app_title({}, { locale: 'en' })).toBe('Content-Based Image Retrieval');
	});
});
