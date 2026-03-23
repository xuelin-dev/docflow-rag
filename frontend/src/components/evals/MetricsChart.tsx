interface MetricsChartProps {
  metric: string;
}

export default function MetricsChart({ metric }: MetricsChartProps) {
  return (
    <div className="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="text-center text-gray-500 dark:text-gray-400">
        <div className="text-lg font-medium">Chart: {metric}</div>
        <div className="text-sm mt-2">Charting library integration pending</div>
      </div>
    </div>
  );
}
