import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { imageService, type ImageItem } from '#lib/images.js';
import * as m from '#lib/paraglide/messages.js';
import { setLocale, getLocale } from '#lib/paraglide/runtime.js';

describe('Image Transformation Studio Tests', () => {
	beforeEach(() => {
		setLocale('en');
		vi.restoreAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('Navigation and i18n', () => {
		it('renders transform navigation title in English', () => {
			setLocale('en');
			expect(getLocale()).toBe('en');
			expect(m.nav_transform()).toBe('Image Transform');
		});

		it('renders transform navigation title in French', () => {
			setLocale('fr');
			expect(getLocale()).toBe('fr');
			expect(m.nav_transform()).toBe("Transformation d'image");
		});
	});

	describe('Mathematical transform dimension calculations', () => {
		it('computes affine shear expanded dimensions correctly', () => {
			const width = 1920;
			const height = 1080;
			const shearX = 0.25;
			const shearY = 0.0;

			const corners = [
				[0, 0],
				[width, 0],
				[0, height],
				[width, height]
			];
			const transX = corners.map(([x, y]) => x + shearX * y);
			const computedWidth = Math.ceil(Math.max(...transX) - Math.min(...transX));

			expect(computedWidth).toBe(1920 + Math.ceil(1080 * 0.25));
			expect(computedWidth).toBe(2190);
		});

		it('computes general 2D affine expanded dimensions correctly', () => {
			const width = 1000;
			const height = 500;
			// Scale 1.5 in X, 2.0 in Y, shearX 0.5
			const a = 1.5;
			const b = 0.5;
			const c = 0;
			const d = 0;
			const e = 2.0;
			const f = 0;

			const corners = [
				[0, 0],
				[width, 0],
				[0, height],
				[width, height]
			];
			const transX = corners.map(([x, y]) => a * x + b * y + c);
			const transY = corners.map(([x, y]) => d * x + e * y + f);
			const computedWidth = Math.ceil(Math.max(...transX) - Math.min(...transX));
			const computedHeight = Math.ceil(Math.max(...transY) - Math.min(...transY));

			// Max X is 1.5*1000 + 0.5*500 = 1500 + 250 = 1750
			expect(computedWidth).toBe(1750);
			// Max Y is 2.0*500 = 1000
			expect(computedHeight).toBe(1000);
		});

		it('computes rotate dimensions with expand toggle', () => {
			const width = 1000;
			const height = 1000;
			const angle = 90;
			const rad = Math.abs(angle) * (Math.PI / 180);
			const newW = Math.round(width * Math.abs(Math.cos(rad)) + height * Math.abs(Math.sin(rad)));
			const newH = Math.round(width * Math.abs(Math.sin(rad)) + height * Math.abs(Math.cos(rad)));

			expect(newW).toBe(1000);
			expect(newH).toBe(1000);
		});
	});

	describe('imageService transform API methods', () => {
		it('calls validateTransform with expected payload', async () => {
			const mockResponse = {
				success: true,
				image_id: 'img-123',
				original_width: 1920,
				original_height: 1080,
				new_width: 2190,
				new_height: 1080,
				aspect_ratio: 2.0278,
				operation: 'shear',
				params: { shear_x: 0.25, shear_y: 0.0, expand: true }
			};

			global.fetch = vi.fn().mockResolvedValue({
				ok: true,
				json: vi.fn().mockResolvedValue(mockResponse)
			});

			const res = await imageService.validateTransform('img-123', 'shear', {
				shear_x: 0.25,
				shear_y: 0.0,
				expand: true
			});

			expect(res.success).toBe(true);
			expect(res.new_width).toBe(2190);
			expect(global.fetch).toHaveBeenCalledWith(
				'/api/v1/images/img-123/transform-validate',
				expect.objectContaining({
					method: 'POST',
					body: JSON.stringify({
						operation: 'shear',
						params: { shear_x: 0.25, shear_y: 0.0, expand: true }
					})
				})
			);
		});

		it('calls transformImage and returns derived image record', async () => {
			const mockDerived: ImageItem = {
				id: 'derived-456',
				owner_id: 'user-1',
				parent_image_id: 'img-123',
				filename: 'ghim_nature_peak_sheared.jpg',
				storage_key: 'derived/user-1/derived-456.jpg',
				source_type: 'derived',
				processing_status: 'completed',
				mime_type: 'image/jpeg',
				file_size: 1542000,
				width: 2190,
				height: 1080,
				created_at: '2026-11-15T00:00:00Z',
				transformation_params: {
					operation: 'shear',
					params: { shear_x: 0.25, shear_y: 0.0 }
				}
			};

			global.fetch = vi.fn().mockResolvedValue({
				ok: true,
				json: vi.fn().mockResolvedValue({
					success: true,
					image: mockDerived
				})
			});

			const result = await imageService.transformImage('img-123', {
				operation: 'shear',
				params: { shear_x: 0.25, shear_y: 0.0 },
				filename: 'ghim_nature_peak_sheared.jpg'
			});

			expect(result.id).toBe('derived-456');
			expect(result.source_type).toBe('derived');
			expect(result.parent_image_id).toBe('img-123');
			expect(global.fetch).toHaveBeenCalledWith(
				'/api/v1/images/img-123/transform',
				expect.objectContaining({
					method: 'POST'
				})
			);
		});

		it('calls getDerivatives and returns children list', async () => {
			global.fetch = vi.fn().mockResolvedValue({
				ok: true,
				json: vi.fn().mockResolvedValue({
					success: true,
					parent_image_id: 'img-123',
					derivatives: [
						{ id: 'derived-1', filename: 'child1.jpg' },
						{ id: 'derived-2', filename: 'child2.jpg' }
					]
				})
			});

			const list = await imageService.getDerivatives('img-123');
			expect(list).toHaveLength(2);
			expect(list[0].id).toBe('derived-1');
		});

		it('calls transformImage with photographic adjustments', async () => {
			const mockAdjustDerived: ImageItem = {
				id: 'derived-adj-1',
				owner_id: 'user-1',
				parent_image_id: 'img-123',
				filename: 'nature_adjusted.jpg',
				storage_key: 'derived/user-1/nature_adjusted.jpg',
				source_type: 'derived',
				processing_status: 'completed',
				mime_type: 'image/jpeg',
				file_size: 1400000,
				width: 1920,
				height: 1080,
				created_at: '2026-11-23T00:00:00Z',
				transformation_params: {
					operation: 'adjust',
					params: {
						adjustments: {
							brightness: 15,
							contrast: 20,
							exposure: 10,
							vibrance: 25,
							sharpness: 30
						}
					}
				}
			};

			global.fetch = vi.fn().mockResolvedValue({
				ok: true,
				json: vi.fn().mockResolvedValue({
					success: true,
					image: mockAdjustDerived
				})
			});

			const result = await imageService.transformImage('img-123', {
				operation: 'adjust',
				params: {
					adjustments: {
						brightness: 15,
						contrast: 20,
						exposure: 10,
						vibrance: 25,
						sharpness: 30
					}
				},
				filename: 'nature_adjusted.jpg'
			});

			expect(result.id).toBe('derived-adj-1');
			expect(result.transformation_params?.operation).toBe('adjust');
			expect(global.fetch).toHaveBeenCalledWith(
				'/api/v1/images/img-123/transform',
				expect.objectContaining({
					method: 'POST',
					body: JSON.stringify({
						operation: 'adjust',
						params: {
							adjustments: {
								brightness: 15,
								contrast: 20,
								exposure: 10,
								vibrance: 25,
								sharpness: 30
							}
						},
						filename: 'nature_adjusted.jpg'
					})
				})
			);
		});

		it('calls transformImage with multi-step pipeline stacking', async () => {
			const mockPipelineDerived: ImageItem = {
				id: 'derived-pipe-1',
				owner_id: 'user-1',
				parent_image_id: 'img-123',
				filename: 'nature_pipelined.jpg',
				storage_key: 'derived/user-1/nature_pipelined.jpg',
				source_type: 'derived',
				processing_status: 'completed',
				mime_type: 'image/jpeg',
				file_size: 980000,
				width: 1024,
				height: 1024,
				created_at: '2026-11-23T00:00:00Z',
				transformation_params: {
					operation: 'pipeline',
					params: {
						steps: [
							{ operation: 'crop', params: { x: 100, y: 100, width: 1024, height: 1024 } },
							{ operation: 'adjust', params: { adjustments: { contrast: 25, saturation: 15 } } }
						]
					}
				}
			};

			global.fetch = vi.fn().mockResolvedValue({
				ok: true,
				json: vi.fn().mockResolvedValue({
					success: true,
					image: mockPipelineDerived
				})
			});

			const result = await imageService.transformImage('img-123', {
				operation: 'pipeline',
				params: {
					steps: [
						{ operation: 'crop', params: { x: 100, y: 100, width: 1024, height: 1024 } },
						{ operation: 'adjust', params: { adjustments: { contrast: 25, saturation: 15 } } }
					]
				},
				filename: 'nature_pipelined.jpg'
			});

			expect(result.id).toBe('derived-pipe-1');
			expect(result.transformation_params?.operation).toBe('pipeline');
			expect(global.fetch).toHaveBeenCalledWith(
				'/api/v1/images/img-123/transform',
				expect.objectContaining({
					method: 'POST'
				})
			);
		});
	});
});
