import { RetrievalResult } from '../../lib/types';
import Card from '../ui/Card';
import Badge from '../ui/Badge';

interface SourcePanelProps {
  sources: RetrievalResult[];
}

export default function SourcePanel({ sources }: SourcePanelProps) {
  return (
    <div className="h-full flex flex-col p-4">
      <h2 className="text-lg font-semibold mb-4">Sources</h2>
      
      {sources.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 text-sm">
          No sources yet
        </div>
      ) : (
        <div className="space-y-3 overflow-y-auto">
          {sources.map((source, idx) => (
            <Card key={idx}>
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="font-medium text-sm truncate flex-1">
                    {source.document_name}
                  </div>
                  <Badge variant="info">
                    {source.score.toFixed(3)}
                  </Badge>
                </div>
                
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  Chunk {source.chunk_index}
                </div>
                
                <div className="text-sm text-gray-700 dark:text-gray-300 line-clamp-4 bg-gray-50 dark:bg-gray-800 p-2 rounded">
                  {source.text}
                </div>
                
                {source.metadata && Object.keys(source.metadata).length > 0 && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {Object.entries(source.metadata).map(([key, value]) => (
                      <div key={key}>
                        {key}: {String(value)}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
