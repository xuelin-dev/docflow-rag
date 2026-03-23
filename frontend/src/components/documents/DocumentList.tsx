import { Document } from '../../lib/types';
import Badge from '../ui/Badge';
import { FileText, Trash2 } from 'lucide-react';

interface DocumentListProps {
  documents: Document[];
}

export default function DocumentList({ documents }: DocumentListProps) {
  const getStatusVariant = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'info';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      <table className="w-full">
        <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Document
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Chunks
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Created
            </th>
            <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {documents.map((doc) => (
            <tr key={doc.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="font-medium text-gray-900 dark:text-gray-100">
                      {doc.filename}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {doc.namespace}
                    </div>
                  </div>
                </div>
              </td>
              <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                {doc.content_type}
              </td>
              <td className="px-6 py-4">
                <Badge variant={getStatusVariant(doc.status)}>
                  {doc.status}
                </Badge>
              </td>
              <td className="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                {doc.chunk_count || 0}
              </td>
              <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                {new Date(doc.created_at).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 text-right">
                <button className="text-red-600 hover:text-red-700 p-2">
                  <Trash2 className="w-4 h-4" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
