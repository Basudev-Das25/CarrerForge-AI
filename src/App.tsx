import { Routes, Route } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import Dashboard from "./screens/Dashboard";
import Profile from "./screens/Profile";
import Education from "./screens/Education";
import Experience from "./screens/Experience";
import Projects from "./screens/Projects";
import Skills from "./screens/Skills";
import Certificates from "./screens/Certificates";
import Achievements from "./screens/Achievements";
import Languages from "./screens/Languages";
import Publications from "./screens/Publications";
import Awards from "./screens/Awards";
import Links from "./screens/Links";

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="education" element={<Education />} />
        <Route path="experience" element={<Experience />} />
        <Route path="projects" element={<Projects />} />
        <Route path="skills" element={<Skills />} />
        <Route path="certificates" element={<Certificates />} />
        <Route path="achievements" element={<Achievements />} />
        <Route path="languages" element={<Languages />} />
        <Route path="publications" element={<Publications />} />
        <Route path="awards" element={<Awards />} />
        <Route path="links" element={<Links />} />
        <Route path="resume" element={<div className="p-8 text-text-secondary">Resume Generator — coming soon</div>} />
        <Route path="documents" element={<div className="p-8 text-text-secondary">Document Vault — coming soon</div>} />
        <Route path="settings" element={<div className="p-8 text-text-secondary">Settings — coming soon</div>} />
      </Route>
    </Routes>
  );
}

export default App;
