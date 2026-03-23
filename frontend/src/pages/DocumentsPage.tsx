import { useParams } from 'react-router-dom';
import { useDocumentStore } from '../stores/documentStore';
import DocumentList from '../components/documents/DocumentList';
import UploadDropzone from '../components/documents/UploadDropzone';
import ChunkPreview from '../components/documents/ChunkPreview';

export default function DocumentsPage() {
  const { docId } = useParams();
  const { documents } = useDocumentStore();
  
  const selectedDoc = docId ? documents.find(d => d.id === docId) : null;

  return (
    <div className="h-full flex flex-col p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Documents</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Upload and manage your document library
        </p>
      </div>

      <div className="mb-6">
        <UploadDropzone />
      </div>

      <div className="flex-1 overflow-auto">
        <DocumentList documents={documents} />
      </div>

      {selectedDoc && (
        <ChunkPreview document={selectedDoc} onClose={() => window.history.back()} />
      )}
    </div>
  );
}
