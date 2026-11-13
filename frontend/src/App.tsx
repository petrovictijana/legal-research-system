import { Route, Routes } from 'react-router-dom';
import { PublicLayout } from './components/layout/PublicLayout';
import { ChatPanel } from './features/chat/ChatPanel';

export default function App() {
  return (
    <Routes>
      {/* Public shell: SiteHeader + content. The app is chatbot-only. */}
      <Route element={<PublicLayout />}>
        <Route path="/" element={<ChatPanel />} />
      </Route>
    </Routes>
  );
}
