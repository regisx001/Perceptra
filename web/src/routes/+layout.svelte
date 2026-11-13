<script lang="ts">
	import "./layout.css";
	import type { LayoutProps } from "./$types";
	import ProgressBar from "#lib/components/progress-bar.svelte";

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<!-- Dynamic favicon based on browser/OS color scheme -->
	<!-- Light theme tab: dark/flat-black icon -->
	<link
		rel="icon"
		href="/favicon-dark.ico"
		sizes="any"
		media="(prefers-color-scheme: light)"
	/>
	<link
		rel="icon"
		type="image/png"
		sizes="32x32"
		href="/favicon-light-32x32.png"
		media="(prefers-color-scheme: light)"
	/>

	<!-- Dark theme tab: beige icon for high contrast -->
	<link
		rel="icon"
		href="/favicon-light.ico"
		sizes="any"
		media="(prefers-color-scheme: dark)"
	/>
	<link
		rel="icon"
		type="image/png"
		sizes="32x32"
		href="/favicon-dark-32x32.png"
		media="(prefers-color-scheme: dark)"
	/>

	<!-- Default fallback and Apple Touch icon -->
	<link rel="icon" href="/favicon.ico" sizes="any" />
	<link rel="apple-touch-icon" href="/apple-touch-icon.png" />
</svelte:head>

<ProgressBar />

{@render children()}
