import { Document } from '../../lib/types';
import Dialog from '../ui/Dialog';
import Badge from '../ui/Badge';

interface ChunkPreviewProps {
  document: Document;
  onClose: () => void;
}

export default function ChunkPreview({ document, onClose }: ChunkPreviewProps) {
  return (
    <Dialog open={true} onClose={onClose}>
      <div className="p-6 max-w-3xl">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">{document.filename}</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              {document.namespace} • {document.chunk_count || 0} chunks
            </p>
          </div>
          <Badge variant="success">{document.status}</Badge>
        </div>

        <div className="space-y-4 max-h-96 overflow-y-auto">
          {/* In a real app, fetch chunks from API */}
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Chunk 1</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">512 tokens</span>
            </div>
            <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              [Preview content would be loaded from API]
            </div>
          </div>
          
          <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Chunk 2</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">498 tokens</span>
            </div>
            <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
              [Preview content would be loaded from API]
            </div>
          </div>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            Close
          </button>
        </div>
      </div>
    </Dialog>
  );
}
