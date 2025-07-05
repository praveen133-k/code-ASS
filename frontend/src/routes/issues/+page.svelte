<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';

	interface Issue {
		id: number;
		title: string;
		description: string;
		severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
		status: 'OPEN' | 'TRIAGED' | 'IN_PROGRESS' | 'DONE';
		created_at: string;
		reporter_id: number;
	}

	interface User {
		id: number;
		email: string;
		role: 'ADMIN' | 'MAINTAINER' | 'REPORTER';
	}

	let issues: Issue[] = [];
	let currentUser: User | null = null;
	let loading = true;
	let showCreateForm = false;
	let newIssue = {
		title: '',
		description: '',
		severity: 'MEDIUM' as const
	};

	onMount(async () => {
		if (!browser || !localStorage.getItem('token')) {
			goto('/');
			return;
		}
		await loadUser();
		await loadIssues();
	});

	async function loadUser() {
		try {
			const response = await fetch('http://localhost:8000/users/me/', {
				headers: {
					'Authorization': `Bearer ${localStorage.getItem('token')}`
				}
			});
			if (response.ok) {
				currentUser = await response.json();
			} else {
				localStorage.removeItem('token');
				goto('/');
			}
		} catch (err) {
			console.error('Error loading user:', err);
		}
	}

	async function loadIssues() {
		try {
			const response = await fetch('http://localhost:8000/issues/', {
				headers: {
					'Authorization': `Bearer ${localStorage.getItem('token')}`
				}
			});
			if (response.ok) {
				issues = await response.json();
			}
		} catch (err) {
			console.error('Error loading issues:', err);
		} finally {
			loading = false;
		}
	}

	async function createIssue() {
		try {
			const response = await fetch('http://localhost:8000/issues/', {
				method: 'POST',
				headers: {
					'Authorization': `Bearer ${localStorage.getItem('token')}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(newIssue)
			});
			if (response.ok) {
				await loadIssues();
				showCreateForm = false;
				newIssue = { title: '', description: '', severity: 'MEDIUM' };
			}
		} catch (err) {
			console.error('Error creating issue:', err);
		}
	}

	async function updateIssueStatus(issueId: number, status: Issue['status']) {
		try {
			const response = await fetch(`http://localhost:8000/issues/${issueId}`, {
				method: 'PUT',
				headers: {
					'Authorization': `Bearer ${localStorage.getItem('token')}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ status })
			});
			if (response.ok) {
				await loadIssues();
			}
		} catch (err) {
			console.error('Error updating issue:', err);
		}
	}

	function logout() {
		localStorage.removeItem('token');
		goto('/');
	}

	function getSeverityColor(severity: string) {
		switch (severity) {
			case 'CRITICAL': return 'bg-red-100 text-red-800';
			case 'HIGH': return 'bg-orange-100 text-orange-800';
			case 'MEDIUM': return 'bg-yellow-100 text-yellow-800';
			case 'LOW': return 'bg-green-100 text-green-800';
			default: return 'bg-gray-100 text-gray-800';
		}
	}

	function getStatusColor(status: string) {
		switch (status) {
			case 'OPEN': return 'bg-blue-100 text-blue-800';
			case 'TRIAGED': return 'bg-purple-100 text-purple-800';
			case 'IN_PROGRESS': return 'bg-yellow-100 text-yellow-800';
			case 'DONE': return 'bg-green-100 text-green-800';
			default: return 'bg-gray-100 text-gray-800';
		}
	}
</script>

<svelte:head>
	<title>Issues Dashboard - Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-white shadow">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center py-6">
				<h1 class="text-3xl font-bold text-gray-900">Issues Dashboard</h1>
				<div class="flex items-center space-x-4">
					<a href="/dashboard" class="text-indigo-600 hover:text-indigo-500">Dashboard</a>
					{#if currentUser}
						<span class="text-sm text-gray-600">
							{currentUser.email} ({currentUser.role})
						</span>
					{/if}
					<button
						on:click={logout}
						class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
					>
						Logout
					</button>
				</div>
			</div>
		</div>
	</header>

	<!-- Main Content -->
	<div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
		<!-- Create Issue Button -->
		<div class="px-4 py-6 sm:px-0">
			<button
				on:click={() => showCreateForm = !showCreateForm}
				class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
			>
				{showCreateForm ? 'Cancel' : 'Create New Issue'}
			</button>
		</div>

		<!-- Create Issue Form -->
		{#if showCreateForm}
			<div class="px-4 py-6 sm:px-0">
				<div class="bg-white shadow rounded-lg p-6">
					<h3 class="text-lg font-medium text-gray-900 mb-4">Create New Issue</h3>
					<form on:submit|preventDefault={createIssue} class="space-y-4">
						<div>
							<label for="title" class="block text-sm font-medium text-gray-700">Title</label>
							<input
								type="text"
								id="title"
								bind:value={newIssue.title}
								required
								class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
							/>
						</div>
						<div>
							<label for="description" class="block text-sm font-medium text-gray-700">Description</label>
							<textarea
								id="description"
								bind:value={newIssue.description}
								required
								rows="3"
								class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
							></textarea>
						</div>
						<div>
							<label for="severity" class="block text-sm font-medium text-gray-700">Severity</label>
							<select
								id="severity"
								bind:value={newIssue.severity}
								class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
							>
								<option value="LOW">Low</option>
								<option value="MEDIUM">Medium</option>
								<option value="HIGH">High</option>
								<option value="CRITICAL">Critical</option>
							</select>
						</div>
						<button
							type="submit"
							class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
						>
							Create Issue
						</button>
					</form>
				</div>
			</div>
		{/if}

		<!-- Issues List -->
		<div class="px-4 py-6 sm:px-0">
			{#if loading}
				<div class="text-center py-12">
					<div class="text-gray-500">Loading issues...</div>
				</div>
			{:else if issues.length === 0}
				<div class="text-center py-12">
					<div class="text-gray-500">No issues found.</div>
				</div>
			{:else}
				<div class="bg-white shadow overflow-hidden sm:rounded-md">
					<ul class="divide-y divide-gray-200">
						{#each issues as issue}
							<li class="px-6 py-4">
								<div class="flex items-center justify-between">
									<div class="flex-1">
										<div class="flex items-center justify-between">
											<p class="text-sm font-medium text-indigo-600 truncate">
												{issue.title}
											</p>
											<div class="flex space-x-2">
												<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getSeverityColor(issue.severity)}">
													{issue.severity}
												</span>
												<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium {getStatusColor(issue.status)}">
													{issue.status}
												</span>
											</div>
										</div>
										<p class="mt-1 text-sm text-gray-600 line-clamp-2">
											{issue.description}
										</p>
										<p class="mt-1 text-xs text-gray-500">
											Created: {new Date(issue.created_at).toLocaleDateString()}
										</p>
									</div>
									{#if currentUser && (currentUser.role === 'ADMIN' || currentUser.role === 'MAINTAINER')}
										<div class="ml-4">
											<select
												value={issue.status}
												on:change={(e) => updateIssueStatus(issue.id, (e.target as HTMLSelectElement).value)}
												class="text-sm border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
											>
												<option value="OPEN">Open</option>
												<option value="TRIAGED">Triaged</option>
												<option value="IN_PROGRESS">In Progress</option>
												<option value="DONE">Done</option>
											</select>
										</div>
									{/if}
								</div>
							</li>
						{/each}
					</ul>
				</div>
			{/if}
		</div>
	</div>
</div> 