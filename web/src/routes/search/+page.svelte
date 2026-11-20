<script lang="ts">
	import { goto } from "$app/navigation";
	import { onMount } from "svelte";

	onMount(() => {
		goto("/dashboard/query", { replaceState: true });
	});
</script>

<div class="flex items-center justify-center min-h-[50vh] text-muted-foreground text-xs">
	Redirecting to Visual Query Studio...
</div>
