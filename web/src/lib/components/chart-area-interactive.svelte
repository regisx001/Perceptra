<script lang="ts">
	import { scaleUtc } from "d3-scale";
	import { curveNatural } from "d3-shape";
	import { Area, AreaChart } from "layerchart";
	import * as Card from "#lib/components/ui/card/index.js";
	import * as Chart from "#lib/components/ui/chart/index.js";
	import * as Select from "#lib/components/ui/select/index.js";
	import * as ToggleGroup from "#lib/components/ui/toggle-group/index.js";

	// CBIR Visual Search queries over time: Color-based searches vs Texture/Hybrid searches
	const chartData = [
		{ date: new Date("2024-04-01"), colorQueries: 142, textureQueries: 95 },
		{ date: new Date("2024-04-02"), colorQueries: 165, textureQueries: 110 },
		{ date: new Date("2024-04-03"), colorQueries: 180, textureQueries: 140 },
		{ date: new Date("2024-04-04"), colorQueries: 210, textureQueries: 175 },
		{ date: new Date("2024-04-05"), colorQueries: 290, textureQueries: 210 },
		{ date: new Date("2024-04-06"), colorQueries: 240, textureQueries: 195 },
		{ date: new Date("2024-04-07"), colorQueries: 190, textureQueries: 160 },
		{ date: new Date("2024-04-08"), colorQueries: 310, textureQueries: 245 },
		{ date: new Date("2024-04-09"), colorQueries: 220, textureQueries: 180 },
		{ date: new Date("2024-04-10"), colorQueries: 260, textureQueries: 220 },
		{ date: new Date("2024-04-11"), colorQueries: 340, textureQueries: 280 },
		{ date: new Date("2024-04-12"), colorQueries: 280, textureQueries: 240 },
		{ date: new Date("2024-04-13"), colorQueries: 320, textureQueries: 290 },
		{ date: new Date("2024-04-14"), colorQueries: 210, textureQueries: 170 },
		{ date: new Date("2024-04-15"), colorQueries: 230, textureQueries: 190 },
		{ date: new Date("2024-04-16"), colorQueries: 275, textureQueries: 215 },
		{ date: new Date("2024-04-17"), colorQueries: 380, textureQueries: 310 },
		{ date: new Date("2024-04-18"), colorQueries: 340, textureQueries: 295 },
		{ date: new Date("2024-04-19"), colorQueries: 290, textureQueries: 220 },
		{ date: new Date("2024-04-20"), colorQueries: 180, textureQueries: 150 },
		{ date: new Date("2024-04-21"), colorQueries: 200, textureQueries: 165 },
		{ date: new Date("2024-04-22"), colorQueries: 260, textureQueries: 210 },
		{ date: new Date("2024-04-23"), colorQueries: 240, textureQueries: 205 },
		{ date: new Date("2024-04-24"), colorQueries: 350, textureQueries: 290 },
		{ date: new Date("2024-04-25"), colorQueries: 270, textureQueries: 225 },
		{ date: new Date("2024-04-26"), colorQueries: 190, textureQueries: 160 },
		{ date: new Date("2024-04-27"), colorQueries: 360, textureQueries: 310 },
		{ date: new Date("2024-04-28"), colorQueries: 220, textureQueries: 175 },
		{ date: new Date("2024-04-29"), colorQueries: 310, textureQueries: 260 },
		{ date: new Date("2024-04-30"), colorQueries: 410, textureQueries: 340 },
		{ date: new Date("2024-05-01"), colorQueries: 250, textureQueries: 205 },
		{ date: new Date("2024-05-02"), colorQueries: 320, textureQueries: 270 },
		{ date: new Date("2024-05-03"), colorQueries: 280, textureQueries: 230 },
		{ date: new Date("2024-05-04"), colorQueries: 390, textureQueries: 330 },
		{ date: new Date("2024-05-05"), colorQueries: 440, textureQueries: 360 },
		{ date: new Date("2024-05-06"), colorQueries: 460, textureQueries: 390 },
		{ date: new Date("2024-05-07"), colorQueries: 380, textureQueries: 310 },
		{ date: new Date("2024-05-08"), colorQueries: 260, textureQueries: 210 },
		{ date: new Date("2024-05-09"), colorQueries: 300, textureQueries: 250 },
		{ date: new Date("2024-05-10"), colorQueries: 330, textureQueries: 280 },
		{ date: new Date("2024-05-11"), colorQueries: 350, textureQueries: 295 },
		{ date: new Date("2024-05-12"), colorQueries: 240, textureQueries: 190 },
		{ date: new Date("2024-05-13"), colorQueries: 220, textureQueries: 180 },
		{ date: new Date("2024-05-14"), colorQueries: 420, textureQueries: 370 },
		{ date: new Date("2024-05-15"), colorQueries: 450, textureQueries: 390 },
		{ date: new Date("2024-05-16"), colorQueries: 360, textureQueries: 310 },
		{ date: new Date("2024-05-17"), colorQueries: 470, textureQueries: 400 },
		{ date: new Date("2024-05-18"), colorQueries: 340, textureQueries: 290 },
		{ date: new Date("2024-05-19"), colorQueries: 250, textureQueries: 200 },
		{ date: new Date("2024-05-20"), colorQueries: 280, textureQueries: 220 },
		{ date: new Date("2024-05-21"), colorQueries: 390, textureQueries: 320 },
		{ date: new Date("2024-05-22"), colorQueries: 320, textureQueries: 260 },
		{ date: new Date("2024-05-23"), colorQueries: 290, textureQueries: 240 },
		{ date: new Date("2024-05-24"), colorQueries: 440, textureQueries: 360 },
		{ date: new Date("2024-05-25"), colorQueries: 330, textureQueries: 270 },
		{ date: new Date("2024-05-26"), colorQueries: 230, textureQueries: 190 },
		{ date: new Date("2024-05-27"), colorQueries: 410, textureQueries: 330 },
		{ date: new Date("2024-05-28"), colorQueries: 350, textureQueries: 290 },
		{ date: new Date("2024-05-29"), colorQueries: 310, textureQueries: 250 },
		{ date: new Date("2024-05-30"), colorQueries: 460, textureQueries: 380 },
		{ date: new Date("2024-05-31"), colorQueries: 420, textureQueries: 350 },
		{ date: new Date("2024-06-01"), colorQueries: 280, textureQueries: 230 },
		{ date: new Date("2024-06-02"), colorQueries: 260, textureQueries: 210 },
		{ date: new Date("2024-06-03"), colorQueries: 430, textureQueries: 360 },
		{ date: new Date("2024-06-04"), colorQueries: 450, textureQueries: 380 },
		{ date: new Date("2024-06-05"), colorQueries: 390, textureQueries: 320 },
		{ date: new Date("2024-06-06"), colorQueries: 420, textureQueries: 350 },
		{ date: new Date("2024-06-07"), colorQueries: 470, textureQueries: 400 },
		{ date: new Date("2024-06-08"), colorQueries: 330, textureQueries: 270 },
		{ date: new Date("2024-06-09"), colorQueries: 270, textureQueries: 220 },
		{ date: new Date("2024-06-10"), colorQueries: 460, textureQueries: 380 },
		{ date: new Date("2024-06-11"), colorQueries: 410, textureQueries: 340 },
		{ date: new Date("2024-06-12"), colorQueries: 360, textureQueries: 300 },
		{ date: new Date("2024-06-13"), colorQueries: 440, textureQueries: 370 },
		{ date: new Date("2024-06-14"), colorQueries: 480, textureQueries: 410 },
		{ date: new Date("2024-06-15"), colorQueries: 350, textureQueries: 290 },
		{ date: new Date("2024-06-16"), colorQueries: 290, textureQueries: 240 },
		{ date: new Date("2024-06-17"), colorQueries: 490, textureQueries: 410 },
		{ date: new Date("2024-06-18"), colorQueries: 430, textureQueries: 360 },
		{ date: new Date("2024-06-19"), colorQueries: 380, textureQueries: 310 },
		{ date: new Date("2024-06-20"), colorQueries: 450, textureQueries: 380 },
		{ date: new Date("2024-06-21"), colorQueries: 270, textureQueries: 220 },
		{ date: new Date("2024-06-22"), colorQueries: 340, textureQueries: 280 },
		{ date: new Date("2024-06-23"), colorQueries: 510, textureQueries: 430 },
		{ date: new Date("2024-06-24"), colorQueries: 260, textureQueries: 210 },
		{ date: new Date("2024-06-25"), colorQueries: 280, textureQueries: 230 },
		{ date: new Date("2024-06-26"), colorQueries: 470, textureQueries: 390 },
		{ date: new Date("2024-06-27"), colorQueries: 490, textureQueries: 410 },
		{ date: new Date("2024-06-28"), colorQueries: 280, textureQueries: 230 },
		{ date: new Date("2024-06-29"), colorQueries: 220, textureQueries: 180 },
		{ date: new Date("2024-06-30"), colorQueries: 520, textureQueries: 440 },
	];

	let timeRange = $state("90d");

	const selectedLabel = $derived.by(() => {
		switch (timeRange) {
			case "90d":
				return "Last 3 months";
			case "30d":
				return "Last 30 days";
			case "7d":
				return "Last 7 days";
			default:
				return "Last 3 months";
		}
	});

	const filteredData = $derived(
		chartData.filter((item) => {
			const referenceDate = new Date("2024-06-30");
			let daysToSubtract = 90;
			if (timeRange === "30d") {
				daysToSubtract = 30;
			} else if (timeRange === "7d") {
				daysToSubtract = 7;
			}

			referenceDate.setDate(referenceDate.getDate() - daysToSubtract);
			return item.date >= referenceDate;
		})
	);

	const chartConfig = {
		colorQueries: { label: "Color Descriptors", color: "var(--primary)" },
		textureQueries: { label: "Texture & GLCM", color: "hsl(var(--muted-foreground))" },
	} satisfies Chart.ChartConfig;
</script>

<Card.Root class="@container/card">
	<Card.Header class="flex flex-col items-start gap-4 @[767px]/card:flex-row @[767px]/card:items-center">
		<div>
			<Card.Title>Similarity Search Activity</Card.Title>
			<Card.Description>
				Query volume and descriptor extraction breakdown ({selectedLabel})
			</Card.Description>
		</div>
		<Card.Action>
			<ToggleGroup.Root
				type="single"
				bind:value={timeRange}
				variant="outline"
				class="hidden *:data-[slot=toggle-group-item]:!px-3 @[767px]/card:flex"
			>
				<ToggleGroup.Item value="90d">Last 3 months</ToggleGroup.Item>
				<ToggleGroup.Item value="30d">Last 30 days</ToggleGroup.Item>
				<ToggleGroup.Item value="7d">Last 7 days</ToggleGroup.Item>
			</ToggleGroup.Root>
			<Select.Root type="single" bind:value={timeRange}>
				<Select.Trigger
					size="sm"
					class="flex w-36 **:data-[slot=select-value]:block **:data-[slot=select-value]:truncate @[767px]/card:hidden"
					aria-label="Select a time range"
				>
					<span data-slot="select-value">
						{selectedLabel}
					</span>
				</Select.Trigger>
				<Select.Content class="rounded-lg">
					<Select.Item value="90d" class="rounded-md">Last 3 months</Select.Item>
					<Select.Item value="30d" class="rounded-md">Last 30 days</Select.Item>
					<Select.Item value="7d" class="rounded-md">Last 7 days</Select.Item>
				</Select.Content>
			</Select.Root>
		</Card.Action>
	</Card.Header>
	<Card.Content class="px-2 pt-4 sm:px-6 sm:pt-6">
		<Chart.Container config={chartConfig} class="aspect-auto h-[260px] w-full">
			<AreaChart
				legend
				data={filteredData}
				x="date"
				xScale={scaleUtc()}
				series={[
					{
						key: "colorQueries",
						label: "Color Descriptors (Histograms + Moments)",
						color: chartConfig.colorQueries.color,
					},
					{
						key: "textureQueries",
						label: "Texture Descriptors (GLCM + LBP)",
						color: chartConfig.textureQueries.color,
					},
				]}
				seriesLayout="stack"
				props={{
					xAxis: {
						ticks: timeRange === "7d" ? 7 : undefined,
						format: (v) => {
							return new Date(v).toLocaleDateString("en-US", {
								month: "short",
								day: "numeric",
							});
						},
					},
					yAxis: {
						format: (v) => `${v} q`,
					},
				}}
			>
				{#snippet tooltip()}
					<Chart.Tooltip
						labelFormatter={(v) => {
							return new Date(v).toLocaleDateString("en-US", {
								month: "short",
								day: "numeric",
								year: "numeric",
							});
						}}
					/>
				{/snippet}
			</AreaChart>
		</Chart.Container>
	</Card.Content>
</Card.Root>
