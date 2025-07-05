<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';

	let email = '';
	let password = '';
	let isLogin = true;
	let loading = false;
	let error = '';

	onMount(() => {
		// Check if user is already logged in
		if (browser && localStorage.getItem('token')) {
			goto('/issues');
		}
	});

	async function handleSubmit() {
		loading = true;
		error = '';

		try {
			const endpoint = isLogin ? '/api/token' : '/api/users/';
			const body = isLogin 
				? new URLSearchParams({ username: email, password })
				: JSON.stringify({ email, password, role: 'REPORTER' });

			const response = await fetch(`http://localhost:8000${endpoint}`, {
				method: 'POST',
				headers: isLogin 
					? { 'Content-Type': 'application/x-www-form-urlencoded' }
					: { 'Content-Type': 'application/json' },
				body
			});

			if (response.ok) {
				const data = await response.json();
				if (isLogin && data.access_token) {
					localStorage.setItem('token', data.access_token);
					goto('/issues');
				} else if (!isLogin) {
					isLogin = true;
					error = 'Registration successful! Please log in.';
				}
			} else {
				const errorData = await response.json();
				error = errorData.detail || 'An error occurred';
			}
		} catch (err) {
			error = 'Network error. Please try again.';
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Issues & Insights Tracker - Login</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
	<div class="max-w-md w-full space-y-8">
		<div>
			<h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
				{isLogin ? 'Sign in to your account' : 'Create new account'}
			</h2>
			<p class="mt-2 text-center text-sm text-gray-600">
				Issues & Insights Tracker
			</p>
		</div>
		<form class="mt-8 space-y-6" on:submit|preventDefault={handleSubmit}>
			<div class="rounded-md shadow-sm -space-y-px">
				<div>
					<label for="email" class="sr-only">Email address</label>
					<input
						id="email"
						name="email"
						type="email"
						required
						bind:value={email}
						class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
						placeholder="Email address"
					/>
				</div>
				<div>
					<label for="password" class="sr-only">Password</label>
					<input
						id="password"
						name="password"
						type="password"
						required
						bind:value={password}
						class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
						placeholder="Password"
					/>
				</div>
			</div>

			{#if error}
				<div class="text-red-600 text-sm text-center">{error}</div>
			{/if}

			<div>
				<button
					type="submit"
					disabled={loading}
					class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
				>
					{loading ? 'Loading...' : (isLogin ? 'Sign in' : 'Sign up')}
				</button>
			</div>

			<div class="text-center">
				<button
					type="button"
					on:click={() => { isLogin = !isLogin; error = ''; }}
					class="text-indigo-600 hover:text-indigo-500 text-sm"
				>
					{isLogin ? 'Need an account? Sign up' : 'Already have an account? Sign in'}
				</button>
			</div>
		</form>
	</div>
</div> 