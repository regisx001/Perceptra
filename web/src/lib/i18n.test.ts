import { describe, it, expect } from 'vitest';
import * as m from '#lib/paraglide/messages.js';
import { locales, baseLocale, setLocale, getLocale } from '#lib/paraglide/runtime.js';

describe('Paraglide i18n setup', () => {
	it('defines supported locales and default baseLocale', () => {
		expect(baseLocale).toBe('en');
		expect(locales).toContain('en');
		expect(locales).toContain('de');
	});

	it('returns localized messages in English', () => {
		setLocale('en');
		expect(getLocale()).toBe('en');
		expect(m.app_title()).toBe('Content-Based Image Retrieval');
		expect(m.welcome()).toBe('Welcome to SvelteKit');
		expect(m.example_message({ username: 'Alice' })).toBe('Hello world Alice');
	});

	it('returns localized messages in German', () => {
		setLocale('de');
		expect(getLocale()).toBe('de');
		expect(m.app_title()).toBe('Inhaltsbasierte Bildsuche');
		expect(m.welcome()).toBe('Willkommen bei SvelteKit');
		expect(m.example_message({ username: 'Alice' })).toBe('Guten Tag Alice');
	});

	it('supports per-call locale override', () => {
		expect(m.app_title({}, { locale: 'de' })).toBe('Inhaltsbasierte Bildsuche');
		expect(m.app_title({}, { locale: 'en' })).toBe('Content-Based Image Retrieval');
	});
});
