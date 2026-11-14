import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as m from '#lib/paraglide/messages.js';
import { setLocale, getLocale } from '#lib/paraglide/runtime.js';
import { imageService, type ImageItem } from '#lib/images.js';

describe('Images Upload & Service Tests', () => {
	beforeEach(() => {
		setLocale('en');
		vi.restoreAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('Paraglide i18n for Upload', () => {
		it('renders all upload messages in English', () => {
			setLocale('en');
			expect(getLocale()).toBe('en');

			expect(m.upload_title()).toBe('Upload Images');
			expect(m.upload_subtitle()).toContain('Add images to the system');
			expect(m.upload_drag_title()).toBe('Drag and drop images here');
			expect(m.upload_select_files()).toBe('Select Files');
			expect(m.upload_target_category()).toBe('Target Category');
			expect(m.upload_uncategorized()).toBe('Uncategorized (No category)');
			expect(m.upload_create_category({ name: 'Architecture' })).toBe('Create category "Architecture"');
			expect(m.upload_queue_title()).toBe('Upload Queue');
			expect(m.upload_start_upload()).toBe('Start Upload');
			expect(m.upload_status_pending()).toBe('Pending');
			expect(m.upload_status_completed()).toBe('Completed');
			expect(m.upload_status_error()).toBe('Error');
		});

		it('renders all upload messages in French', () => {
			setLocale('fr');
			expect(getLocale()).toBe('fr');

			expect(m.upload_title()).toBe('Téléverser des images');
			expect(m.upload_subtitle()).toContain('Ajoutez des images au système');
			expect(m.upload_drag_title()).toBe('Glissez-déposez vos images ici');
			expect(m.upload_select_files()).toBe('Sélectionner des fichiers');
			expect(m.upload_target_category()).toBe('Catégorie cible');
			expect(m.upload_uncategorized()).toBe('Non classé (Aucune catégorie)');
			expect(m.upload_create_category({ name: 'Architecture' })).toBe('Créer la catégorie « Architecture »');
			expect(m.upload_queue_title()).toBe("File d'attente");
			expect(m.upload_start_upload()).toBe('Démarrer le téléversement');
			expect(m.upload_status_pending()).toBe('En attente');
			expect(m.upload_status_completed()).toBe('Terminé');
			expect(m.upload_status_error()).toBe('Erreur');
		});
	});

	describe('ImageService API Client', () => {
		it('generates correct stream and download file URLs', () => {
			const streamUrl = imageService.getImageFileUrl('img-123');
			expect(streamUrl).toBe('/api/v1/images/img-123/file');

			const downloadUrl = imageService.getImageFileUrl('img-123', true);
			expect(downloadUrl).toBe('/api/v1/images/img-123/file?download=true');
		});

		it('lists images with pagination and category filter', async () => {
			const mockImages: ImageItem[] = [
				{
					id: 'img-1',
					owner_id: 'user-1',
					category_id: 'cat-1',
					filename: 'photo.jpg',
					storage_key: 'users/user-1/photo.jpg',
					source_type: 'upload',
					processing_status: 'completed',
					mime_type: 'image/jpeg',
					file_size: 102400
				}
			];

			const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({
					success: true,
					images: mockImages,
					pagination: { page: 1, per_page: 24, total: 1, pages: 1 }
				})
			} as Response);

			const result = await imageService.listImages({ category_id: 'cat-1', page: 1, per_page: 24 });

			expect(fetchSpy).toHaveBeenCalledTimes(1);
			const callUrl = fetchSpy.mock.calls[0][0].toString();
			expect(callUrl).toContain('/images?category_id=cat-1&page=1&per_page=24');
			expect(result.images).toHaveLength(1);
			expect(result.images[0].filename).toBe('photo.jpg');
		});

		it('uploads an image via XMLHttpRequest and tracks progress', async () => {
			const dummyFile = new File(['fake-binary-content'], 'test.png', { type: 'image/png' });
			const mockUploaded: ImageItem = {
				id: 'img-new-1',
				owner_id: 'user-1',
				category_id: 'cat-10',
				filename: 'test.png',
				storage_key: 'users/user-1/uuid.png',
				source_type: 'upload',
				processing_status: 'pending',
				mime_type: 'image/png',
				file_size: 19
			};

			// Mock XMLHttpRequest
			class MockXMLHttpRequest {
				upload = { onprogress: null as any };
				status = 201;
				responseText = JSON.stringify({ success: true, image: mockUploaded });
				onload: (() => void) | null = null;
				onerror: (() => void) | null = null;

				open = vi.fn();
				setRequestHeader = vi.fn();
				send = vi.fn().mockImplementation(() => {
					if (this.upload.onprogress) {
						this.upload.onprogress({ lengthComputable: true, loaded: 50, total: 100 });
					}
					if (this.onload) this.onload();
				});
			}

			(globalThis as any).XMLHttpRequest = MockXMLHttpRequest;

			let recordedProgress = 0;
			const uploaded = await imageService.uploadImage(dummyFile, 'cat-10', (p) => {
				recordedProgress = p;
			});

			expect(uploaded.id).toBe('img-new-1');
			expect(uploaded.filename).toBe('test.png');
			expect(recordedProgress).toBe(50);
		});

		it('performs bulk assign of images', async () => {
			const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({
					success: true,
					updated_count: 3
				})
			} as Response);

			const count = await imageService.bulkAssign(['img-1', 'img-2', 'img-3'], 'cat-99');

			expect(fetchSpy).toHaveBeenCalledTimes(1);
			const requestOptions = fetchSpy.mock.calls[0][1];
			expect(requestOptions?.method).toBe('POST');
			expect(JSON.parse(requestOptions?.body as string)).toEqual({
				image_ids: ['img-1', 'img-2', 'img-3'],
				category_id: 'cat-99'
			});
			expect(count).toBe(3);
		});

		it('deletes an image', async () => {
			const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({
					success: true,
					message: 'Image deleted.'
				})
			} as Response);

			await imageService.deleteImage('img-delete-1');

			expect(fetchSpy).toHaveBeenCalledTimes(1);
			const callUrl = fetchSpy.mock.calls[0][0].toString();
			expect(callUrl).toContain('/images/img-delete-1');
			const requestOptions = fetchSpy.mock.calls[0][1];
			expect(requestOptions?.method).toBe('DELETE');
		});

		it('bulk deletes multiple images', async () => {
			const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({
					success: true,
					deleted_count: 2
				})
			} as Response);

			const count = await imageService.bulkDelete(['img-1', 'img-2']);

			expect(fetchSpy).toHaveBeenCalledTimes(1);
			const requestOptions = fetchSpy.mock.calls[0][1];
			expect(requestOptions?.method).toBe('POST');
			expect(JSON.parse(requestOptions?.body as string)).toEqual({
				image_ids: ['img-1', 'img-2']
			});
			expect(count).toBe(2);
		});
	});
});
