import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ChatPage from './pages/ChatPage';
import DocumentsPage from './pages/DocumentsPage';
import NamespacesPage from './pages/NamespacesPage';
import EvalsPage from './pages/EvalsPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/chat" replace />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="chat/:conversationId" element={<ChatPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="documents/:docId" element={<DocumentsPage />} />
        <Route path="namespaces" element={<NamespacesPage />} />
        <Route path="evals" element={<EvalsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}

export default App;
