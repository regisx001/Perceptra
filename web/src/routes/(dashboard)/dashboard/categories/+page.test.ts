import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as m from '#lib/paraglide/messages.js';
import { setLocale, getLocale } from '#lib/paraglide/runtime.js';
import { categoryService, type CategoryItem } from '#lib/categories.js';

describe('Categories Page i18n & Client Service Tests', () => {
	beforeEach(() => {
		setLocale('en');
		vi.restoreAllMocks();
	});

	afterEach(() => {
		vi.restoreAllMocks();
	});

	describe('Paraglide i18n for Categories', () => {
		it('renders all categories messages correctly in English', () => {
			setLocale('en');
			expect(getLocale()).toBe('en');

			expect(m.categories_title()).toBe('Categories & Collections');
			expect(m.categories_subtitle()).toBe("Organize your collection's category structure and folder assignments.");
			expect(m.categories_collapse_all()).toBe('Collapse All');
			expect(m.categories_new_category()).toBe('New Category');
			expect(m.categories_stat_total()).toBe('Total Categories');
			expect(m.categories_stat_root()).toBe('Root Folders');
			expect(m.categories_stat_root_badge()).toBe('Top Level');
			expect(m.categories_stat_categorized()).toBe('Categorized Images');
			expect(m.categories_stat_uncategorized()).toBe('Uncategorized Images');
			expect(m.categories_tree_title()).toBe('Category Hierarchy');
			expect(m.categories_search_placeholder()).toBe('Search categories...');
			expect(m.categories_uncategorized_label()).toBe('Uncategorized');
			expect(m.categories_uncategorized_collection()).toBe('Uncategorized Collection');
			expect(m.categories_parent_label()).toBe('Parent');
			expect(m.categories_delete_btn()).toBe('Delete Category');
			expect(m.categories_add_subcategory_btn()).toBe('Subcategory');
			expect(m.categories_assigned_images_title()).toBe('Assigned Images');
			expect(m.categories_dialog_new_title()).toBe('Create New Category');
			expect(m.categories_dialog_edit_title()).toBe('Edit Category Name');
			expect(m.categories_dialog_subcat_title()).toBe('Add Subcategory');
			expect(m.categories_dialog_move_title()).toBe('Move Category');
			expect(m.categories_dialog_subcat_desc({ name: 'Landscapes' })).toBe('Create a child folder inside Landscapes.');
			expect(m.categories_dialog_move_desc({ name: 'Mountains' })).toBe('Select a new parent folder for Mountains.');
			expect(m.categories_alert_delete_title({ name: 'Persons' })).toBe('Delete "Persons"?');
			expect(m.categories_alert_delete_desc()).toContain('Are you sure you want to delete this category?');
			expect(m.categories_menu_add_sub()).toBe('Add Subcategory');
			expect(m.categories_menu_rename()).toBe('Rename');
			expect(m.categories_menu_move()).toBe('Move Folder');
			expect(m.categories_menu_delete()).toBe('Delete');
			expect(m.categories_empty_images()).toBe('No images in this category');
			expect(m.categories_showing_images({ count: 5, total: 10 })).toBe('Showing 5 of 10 images');
		});

		it('renders all categories messages correctly in French', () => {
			setLocale('fr');
			expect(getLocale()).toBe('fr');

			expect(m.categories_title()).toBe('Catégories & Collections');
			expect(m.categories_subtitle()).toBe("Organisez la structure des catégories et l'attribution des dossiers de votre collection.");
			expect(m.categories_collapse_all()).toBe('Tout réduire');
			expect(m.categories_new_category()).toBe('Nouvelle catégorie');
			expect(m.categories_stat_total()).toBe('Total des catégories');
			expect(m.categories_stat_root()).toBe('Dossiers racines');
			expect(m.categories_stat_root_badge()).toBe('Niveau supérieur');
			expect(m.categories_stat_categorized()).toBe('Images classées');
			expect(m.categories_stat_uncategorized()).toBe('Images non classées');
			expect(m.categories_tree_title()).toBe('Hiérarchie des catégories');
			expect(m.categories_search_placeholder()).toBe('Rechercher des catégories...');
			expect(m.categories_uncategorized_label()).toBe('Non classé');
			expect(m.categories_uncategorized_collection()).toBe('Collection non classée');
			expect(m.categories_parent_label()).toBe('Parent');
			expect(m.categories_delete_btn()).toBe('Supprimer la catégorie');
			expect(m.categories_add_subcategory_btn()).toBe('Sous-catégorie');
			expect(m.categories_assigned_images_title()).toBe('Images attribuées');
			expect(m.categories_dialog_new_title()).toBe('Créer une nouvelle catégorie');
			expect(m.categories_dialog_edit_title()).toBe('Modifier le nom de la catégorie');
			expect(m.categories_dialog_subcat_title()).toBe('Ajouter une sous-catégorie');
			expect(m.categories_dialog_move_title()).toBe('Déplacer la catégorie');
			expect(m.categories_dialog_subcat_desc({ name: 'Paysages' })).toBe('Créer un dossier enfant dans Paysages.');
			expect(m.categories_dialog_move_desc({ name: 'Montagnes' })).toBe('Sélectionnez un nouveau dossier parent pour Montagnes.');
			expect(m.categories_alert_delete_title({ name: 'Personnes' })).toBe('Supprimer « Personnes » ?');
			expect(m.categories_alert_delete_desc()).toContain('Voulez-vous vraiment supprimer cette catégorie ?');
			expect(m.categories_menu_add_sub()).toBe('Ajouter une sous-catégorie');
			expect(m.categories_menu_rename()).toBe('Renommer');
			expect(m.categories_menu_move()).toBe('Déplacer le dossier');
			expect(m.categories_menu_delete()).toBe('Supprimer');
			expect(m.categories_empty_images()).toBe('Aucune image dans cette catégorie');
			expect(m.categories_showing_images({ count: 5, total: 10 })).toBe('Affichage de 5 sur 10 images');
		});
	});

	describe('CategoryService API Client', () => {
		it('fetches categories with tree and include_counts query params', async () => {
			const mockCategories: CategoryItem[] = [
				{
					id: 'cat-1',
					name: 'Nature',
					image_count: 120,
					children: [
						{
							id: 'cat-2',
							parent_id: 'cat-1',
							name: 'Landscapes',
							image_count: 45,
							children: []
						}
					]
				}
			];

			const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({
					success: true,
					categories: mockCategories
				})
			} as Response);

			const result = await categoryService.getCategories({ tree: true, include_counts: true });

			expect(fetchSpy).toHaveBeenCalledTimes(1);
			const callUrl = fetchSpy.mock.calls[0][0].toString();
			expect(callUrl).toContain('/categories?tree=true&include_counts=true');
			expect(result).toHaveLength(1);
			expect(result[0].name).toBe('Nature');
			expect(result[0].children?.[0].name).toBe('Landscapes');
		});

		it('creates a category with parent_id', async () => {
			const newCat: CategoryItem = {
				id: 'cat-new',
				name: 'Wildlife',
				parent_id: 'cat-1',
				image_count: 0
			};

			const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: true,
				status: 201,
				json: async () => ({
					success: true,
					category: newCat
				})
			} as Response);

			const result = await categoryService.createCategory({
				name: 'Wildlife',
				parent_id: 'cat-1'
			});

			expect(fetchSpy).toHaveBeenCalledTimes(1);
			const requestOptions = fetchSpy.mock.calls[0][1];
			expect(requestOptions?.method).toBe('POST');
			expect(JSON.parse(requestOptions?.body as string)).toEqual({
				name: 'Wildlife',
				parent_id: 'cat-1'
			});
			expect(result.id).toBe('cat-new');
			expect(result.name).toBe('Wildlife');
		});

		it('updates category name and parent_id', async () => {
			const updatedCat: CategoryItem = {
				id: 'cat-2',
				name: 'Desert Landscapes',
				parent_id: null
			};

			const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({
					success: true,
					category: updatedCat
				})
			} as Response);

			const result = await categoryService.updateCategory('cat-2', {
				name: 'Desert Landscapes',
				parent_id: null
			});

			expect(fetchSpy).toHaveBeenCalledTimes(1);
			const callUrl = fetchSpy.mock.calls[0][0].toString();
			expect(callUrl).toContain('/categories/cat-2');
			const requestOptions = fetchSpy.mock.calls[0][1];
			expect(requestOptions?.method).toBe('PATCH');
			expect(JSON.parse(requestOptions?.body as string)).toEqual({
				name: 'Desert Landscapes',
				parent_id: null
			});
			expect(result.name).toBe('Desert Landscapes');
		});

		it('deletes category by id', async () => {
			const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: true,
				status: 200,
				json: async () => ({
					success: true,
					message: 'Category deleted'
				})
			} as Response);

			await categoryService.deleteCategory('cat-delete');

			expect(fetchSpy).toHaveBeenCalledTimes(1);
			const callUrl = fetchSpy.mock.calls[0][0].toString();
			expect(callUrl).toContain('/categories/cat-delete');
			const requestOptions = fetchSpy.mock.calls[0][1];
			expect(requestOptions?.method).toBe('DELETE');
		});

		it('handles API error responses gracefully', async () => {
			vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
				ok: false,
				status: 400,
				json: async () => ({
					success: false,
					error: 'A category with this name already exists at this level'
				})
			} as Response);

			await expect(
				categoryService.createCategory({ name: 'Duplicate Name' })
			).rejects.toThrow('A category with this name already exists at this level');
		});
	});
});
