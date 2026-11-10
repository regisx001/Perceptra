<script lang="ts">
	import { Button } from "#lib/components/ui/button/index.js";
	import {
		FieldGroup,
		Field,
		FieldLabel,
		FieldDescription,
		FieldSeparator,
	} from "#lib/components/ui/field/index.js";
	import { Input } from "#lib/components/ui/input/index.js";
	import { cn, type WithElementRef } from "#lib/utils.js";
	import * as m from "#lib/paraglide/messages.js";
	import { auth } from "#lib/auth.js";
	import { progress } from "#lib/progress.svelte.js";
	import { goto } from "$app/navigation";
	import CheckCircle2Icon from "@lucide/svelte/icons/check-circle-2";
	import Loader2Icon from "@lucide/svelte/icons/loader-2";
	import type { HTMLFormAttributes } from "svelte/elements";

	let {
		ref = $bindable(null),
		class: className,
		...restProps
	}: WithElementRef<HTMLFormAttributes> = $props();

	const id = $props.id();
	let email = $state("");
	let password = $state("");
	let confirmPassword = $state("");
	let isSubmitting = $state(false);
	let isSuccess = $state(false);
	let errorMessage = $state<string | null>(null);

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		errorMessage = null;

		if (password !== confirmPassword) {
			errorMessage = "Passwords do not match.";
			return;
		}

		if (password.length < 6) {
			errorMessage = "Password must be at least 6 characters long.";
			return;
		}

		isSubmitting = true;
		progress.start();

		try {
			await auth.register(email, password);
			isSuccess = true;
			progress.done();
			// Brief delay to allow the user to see the success state
			setTimeout(async () => {
				await goto("/");
			}, 900);
		} catch (err: any) {
			progress.done();
			isSubmitting = false;
			errorMessage = err?.message || "Registration failed. Please try again.";
		}
	}
</script>

<form
	class={cn("flex w-full flex-col gap-6", className)}
	bind:this={ref}
	onsubmit={handleSubmit}
	{...restProps}
>
	<div class="flex flex-col items-center gap-1.5 text-center">
		<h1 class="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
			{m.auth_register_title()}
		</h1>
		<p class="text-sm text-balance text-muted-foreground leading-normal">
			{m.auth_register_subtitle()}
		</p>
	</div>

	{#if isSuccess}
		<div
			class="flex items-center justify-center gap-2.5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3.5 text-sm font-medium text-emerald-600 dark:text-emerald-400 animate-in fade-in zoom-in-95 duration-200"
		>
			<CheckCircle2Icon class="size-4 shrink-0 text-emerald-500" />
			<span>{m.auth_register_success()}</span>
		</div>
	{/if}

	{#if errorMessage}
		<div class="rounded-md bg-destructive/15 p-3 text-sm text-destructive border border-destructive/20 text-center font-medium animate-in fade-in duration-150">
			{errorMessage}
		</div>
	{/if}

	<FieldGroup>
		<Field>
			<FieldLabel for="reg-email-{id}">{m.auth_email_label()}</FieldLabel>
			<Input
				id="reg-email-{id}"
				type="email"
				autocomplete="email"
				placeholder={m.auth_email_placeholder()}
				bind:value={email}
				disabled={isSubmitting || isSuccess}
				required
			/>
		</Field>

		<Field>
			<FieldLabel for="reg-password-{id}">{m.auth_password_label()}</FieldLabel>
			<Input
				id="reg-password-{id}"
				type="password"
				autocomplete="new-password"
				bind:value={password}
				disabled={isSubmitting || isSuccess}
				required
			/>
		</Field>

		<Field>
			<FieldLabel for="reg-confirm-{id}">{m.auth_confirm_password_label()}</FieldLabel>
			<Input
				id="reg-confirm-{id}"
				type="password"
				autocomplete="new-password"
				bind:value={confirmPassword}
				disabled={isSubmitting || isSuccess}
				required
			/>
		</Field>

		<Button
			type="submit"
			class="w-full mt-1 gap-2"
			disabled={isSubmitting || isSuccess}
		>
			{#if isSubmitting}
				<Loader2Icon class="size-4 animate-spin" />
				<span>{m.auth_signup_button()}</span>
			{:else if isSuccess}
				<CheckCircle2Icon class="size-4" />
				<span>{m.auth_signup_button()}</span>
			{:else}
				{m.auth_signup_button()}
			{/if}
		</Button>

		<FieldSeparator class="my-2">{m.auth_or_continue_with()}</FieldSeparator>

		<Button
			variant="outline"
			type="button"
			class="w-full gap-2"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				class="size-4 shrink-0 fill-current"
				aria-hidden="true"
			>
				<path
					d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
				/>
			</svg>
			{m.auth_github_button()}
		</Button>

		<FieldDescription class="text-center pt-1 text-sm text-muted-foreground">
			{m.auth_has_account()}
			<a
				href="/login"
				class="font-medium text-foreground underline underline-offset-4 hover:text-primary transition-colors ms-1"
			>
				{m.auth_sign_in_link()}
			</a>
		</FieldDescription>
	</FieldGroup>
</form>
