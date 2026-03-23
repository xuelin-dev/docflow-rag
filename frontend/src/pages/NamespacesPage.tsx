import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import Button from '../components/ui/Button';
import Card from '../components/ui/Card';
import Dialog from '../components/ui/Dialog';
import Input from '../components/ui/Input';
import { Trash2, Plus } from 'lucide-react';

export default function NamespacesPage() {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newNamespace, setNewNamespace] = useState('');
  const queryClient = useQueryClient();

  const { data: namespaces = [] } = useQuery({
    queryKey: ['namespaces'],
    queryFn: async () => {
      const res = await api.get('/namespaces');
      return res.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (name: string) => api.post('/namespaces', { name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['namespaces'] });
      setShowCreateDialog(false);
      setNewNamespace('');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.delete(`/namespaces/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['namespaces'] });
    },
  });

  return (
    <div className="p-6 h-full">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Namespaces</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Organize documents into isolated namespaces
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Namespace
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {namespaces.map((ns: any) => (
          <Card key={ns.id}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{ns.name}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {ns.document_count || 0} documents
                </p>
                <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                  Created {new Date(ns.created_at).toLocaleDateString()}
                </p>
              </div>
              <button
                onClick={() => deleteMutation.mutate(ns.id)}
                className="text-red-600 hover:text-red-700 p-2"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </Card>
        ))}
      </div>

      <Dialog open={showCreateDialog} onClose={() => setShowCreateDialog(false)}>
        <div className="p-6">
          <h2 className="text-xl font-bold mb-4">Create Namespace</h2>
          <Input
            label="Namespace Name"
            value={newNamespace}
            onChange={(e) => setNewNamespace(e.target.value)}
            placeholder="e.g., product-docs"
          />
          <div className="flex gap-2 mt-6">
            <Button onClick={() => createMutation.mutate(newNamespace)} disabled={!newNamespace}>
              Create
            </Button>
            <Button variant="secondary" onClick={() => setShowCreateDialog(false)}>
              Cancel
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  );
}
