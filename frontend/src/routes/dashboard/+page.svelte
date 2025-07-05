<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import { Chart, registerables } from 'chart.js';

	Chart.register(...registerables);

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
	let severityChart: Chart | null = null;
	let statusChart: Chart | null = null;

	onMount(async () => {
		if (!browser || !localStorage.getItem('token')) {
			goto('/');
			return;
		}
		await loadUser();
		await loadIssues();
		createCharts();
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

	function createCharts() {
		// Prepare data
		const severityData = prepareSeverityData();
		const statusData = prepareStatusData();

		// Create severity chart
		const severityCtx = document.getElementById('severityChart') as HTMLCanvasElement;
		if (severityCtx && severityChart) {
			severityChart.destroy();
		}
		if (severityCtx) {
			severityChart = new Chart(severityCtx, {
				type: 'doughnut',
				data: {
					labels: severityData.labels,
					datasets: [{
						data: severityData.values,
						backgroundColor: [
							'#10B981', // Green for LOW
							'#F59E0B', // Yellow for MEDIUM
							'#F97316', // Orange for HIGH
							'#EF4444'  // Red for CRITICAL
						],
						borderWidth: 2,
						borderColor: '#ffffff'
					}]
				},
				options: {
					responsive: true,
					plugins: {
						legend: {
							position: 'bottom'
						},
						title: {
							display: true,
							text: 'Open Issues by Severity'
						}
					}
				}
			});
		}

		// Create status chart
		const statusCtx = document.getElementById('statusChart') as HTMLCanvasElement;
		if (statusCtx && statusChart) {
			statusChart.destroy();
		}
		if (statusCtx) {
			statusChart = new Chart(statusCtx, {
				type: 'bar',
				data: {
					labels: statusData.labels,
					datasets: [{
						label: 'Number of Issues',
						data: statusData.values,
						backgroundColor: [
							'#3B82F6', // Blue for OPEN
							'#8B5CF6', // Purple for TRIAGED
							'#F59E0B', // Yellow for IN_PROGRESS
							'#10B981'  // Green for DONE
						],
						borderWidth: 1,
						borderColor: '#ffffff'
					}]
				},
				options: {
					responsive: true,
					plugins: {
						legend: {
							display: false
						},
						title: {
							display: true,
							text: 'Issues by Status'
						}
					},
					scales: {
						y: {
							beginAtZero: true,
							ticks: {
								stepSize: 1
							}
						}
					}
				}
			});
		}
	}

	function prepareSeverityData() {
		const severityCounts = {
			LOW: 0,
			MEDIUM: 0,
			HIGH: 0,
			CRITICAL: 0
		};

		// Count open issues by severity
		issues.forEach(issue => {
			if (issue.status !== 'DONE') {
				severityCounts[issue.severity]++;
			}
		});

		return {
			labels: Object.keys(severityCounts),
			values: Object.values(severityCounts)
		};
	}

	function prepareStatusData() {
		const statusCounts = {
			OPEN: 0,
			TRIAGED: 0,
			IN_PROGRESS: 0,
			DONE: 0
		};

		// Count issues by status
		issues.forEach(issue => {
			statusCounts[issue.status]++;
		});

		return {
			labels: Object.keys(statusCounts),
			values: Object.values(statusCounts)
		};
	}

	function logout() {
		localStorage.removeItem('token');
		goto('/');
	}

	function getTotalIssues() {
		return issues.length;
	}

	function getOpenIssues() {
		return issues.filter(issue => issue.status !== 'DONE').length;
	}

	function getCriticalIssues() {
		return issues.filter(issue => issue.severity === 'CRITICAL' && issue.status !== 'DONE').length;
	}
</script>

<svelte:head>
	<title>Dashboard - Issues & Insights Tracker</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-white shadow">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center py-6">
				<h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
				<div class="flex items-center space-x-4">
					<a href="/issues" class="text-indigo-600 hover:text-indigo-500">Issues</a>
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
		{#if loading}
			<div class="text-center py-12">
				<div class="text-gray-500">Loading dashboard...</div>
			</div>
		{:else}
			<!-- Stats Cards -->
			<div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
				<div class="bg-white overflow-hidden shadow rounded-lg">
					<div class="p-5">
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
									<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
									</svg>
								</div>
							</div>
							<div class="ml-5 w-0 flex-1">
								<dl>
									<dt class="text-sm font-medium text-gray-500 truncate">Total Issues</dt>
									<dd class="text-lg font-medium text-gray-900">{getTotalIssues()}</dd>
								</dl>
							</div>
						</div>
					</div>
				</div>

				<div class="bg-white overflow-hidden shadow rounded-lg">
					<div class="p-5">
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
									<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
									</svg>
								</div>
							</div>
							<div class="ml-5 w-0 flex-1">
								<dl>
									<dt class="text-sm font-medium text-gray-500 truncate">Open Issues</dt>
									<dd class="text-lg font-medium text-gray-900">{getOpenIssues()}</dd>
								</dl>
							</div>
						</div>
					</div>
				</div>

				<div class="bg-white overflow-hidden shadow rounded-lg">
					<div class="p-5">
						<div class="flex items-center">
							<div class="flex-shrink-0">
								<div class="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
									<svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
									</svg>
								</div>
							</div>
							<div class="ml-5 w-0 flex-1">
								<dl>
									<dt class="text-sm font-medium text-gray-500 truncate">Critical Issues</dt>
									<dd class="text-lg font-medium text-gray-900">{getCriticalIssues()}</dd>
								</dl>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- Charts -->
			<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
				<div class="bg-white shadow rounded-lg p-6">
					<canvas id="severityChart"></canvas>
				</div>
				<div class="bg-white shadow rounded-lg p-6">
					<canvas id="statusChart"></canvas>
				</div>
			</div>
		{/if}
	</div>
</div> 