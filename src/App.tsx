import { Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<div className="p-8">Dashboard — coming soon</div>} />
        <Route path="profile" element={<div className="p-8">Profile — coming soon</div>} />
        <Route path="resume" element={<div className="p-8">Resume Generator — coming soon</div>} />
        <Route path="documents" element={<div className="p-8">Document Vault — coming soon</div>} />
        <Route path="settings" element={<div className="p-8">Settings — coming soon</div>} />
      </Route>
    </Routes>
  );
}

export default App;
