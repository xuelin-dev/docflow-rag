import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import EvalDashboard from '../components/evals/EvalDashboard';
import Card from '../components/ui/Card';

export default function EvalsPage() {
  const { data: evalRuns = [] } = useQuery({
    queryKey: ['eval-runs'],
    queryFn: async () => {
      const res = await api.get('/evals/runs');
      return res.data;
    },
  });

  return (
    <div className="p-6 h-full overflow-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Evaluation Metrics</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Track RAG pipeline performance
        </p>
      </div>

      <EvalDashboard />

      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Recent Evaluation Runs</h2>
        <div className="space-y-4">
          {evalRuns.map((run: any) => (
            <Card key={run.id}>
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-medium">{run.name || `Run ${run.id.slice(0, 8)}`}</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                    {new Date(run.created_at).toLocaleString()}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {run.metrics?.recall_at_k?.toFixed(2) || 'N/A'} Recall@5
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {run.test_cases_count || 0} test cases
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
