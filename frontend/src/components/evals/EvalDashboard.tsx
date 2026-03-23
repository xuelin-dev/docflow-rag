import { useQuery } from '@tanstack/react-query';
import { api } from '../../lib/api';
import Card from '../ui/Card';
import MetricsChart from './MetricsChart';

export default function EvalDashboard() {
  const { data: metrics } = useQuery({
    queryKey: ['eval-metrics'],
    queryFn: async () => {
      const res = await api.get('/evals/metrics/latest');
      return res.data;
    },
  });

  const metricCards = [
    { label: 'Recall@K', value: metrics?.recall_at_k || 0, color: 'blue' },
    { label: 'Faithfulness', value: metrics?.faithfulness || 0, color: 'green' },
    { label: 'Relevance', value: metrics?.relevance || 0, color: 'purple' },
    { label: 'Precision', value: metrics?.precision || 0, color: 'yellow' },
    { label: 'Latency (ms)', value: metrics?.latency_ms || 0, color: 'red', isTime: true },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {metricCards.map((metric) => (
          <Card key={metric.label}>
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {metric.label}
            </div>
            <div className={`text-3xl font-bold mt-2 text-${metric.color}-600`}>
              {metric.isTime ? metric.value : (metric.value * 100).toFixed(1)}
              {!metric.isTime && '%'}
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h3 className="font-semibold mb-4">Recall Trend</h3>
          <MetricsChart metric="recall_at_k" />
        </Card>
        <Card>
          <h3 className="font-semibold mb-4">Latency Trend</h3>
          <MetricsChart metric="latency_ms" />
        </Card>
      </div>
    </div>
  );
}
