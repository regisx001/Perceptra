import { setContext, getContext } from "svelte";
import type { Snippet } from "svelte";

export interface HeaderPortalState {
	content: Snippet | null;
	breadcrumb: Snippet | null;
}

const HEADER_PORTAL_KEY = Symbol("header-portal");

export function createHeaderPortal() {
	let portal = $state<HeaderPortalState>({ content: null, breadcrumb: null });
	setContext(HEADER_PORTAL_KEY, portal);
	return portal;
}

export function useHeaderPortal() {
	return getContext<HeaderPortalState>(HEADER_PORTAL_KEY);
}
