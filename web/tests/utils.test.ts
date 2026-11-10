import { describe, it, expect } from 'vitest';
import { cn } from '#lib/utils.js';

describe('utils (cn)', () => {
	it('merges class names correctly', () => {
		expect(cn('px-2', 'py-1')).toBe('px-2 py-1');
	});

	it('handles conditional classes properly', () => {
		const isTrue = true;
		const isFalse = false;
		expect(cn('base', isTrue && 'active', isFalse && 'inactive')).toBe('base active');
	});
});
