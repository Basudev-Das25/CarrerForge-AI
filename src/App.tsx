import { Routes, Route } from "react-router-dom";
import { useState } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import Onboarding from "./screens/Onboarding/index";
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
import ResumeGenerator from "./screens/ResumeGenerator";
import ATSDashboard from "./screens/ATSDashboard";
import UpdateSettings from "./screens/UpdateSettings";
import Feedback from "./screens/Feedback";

function AboutPage() {
  return (
    <div className="max-w-2xl space-y-6 animate-fade-in">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="h-16 w-16 rounded-2xl bg-brand-600 flex items-center justify-center shadow-lg">
            <span className="text-white text-2xl font-bold">CF</span>
          </div>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-text-primary">CareerForge AI</h1>
          <p className="text-sm text-text-tertiary">Version 0.5.0-alpha · Build 1</p>
        </div>
      </div>
      <div className="card space-y-3">
        <h3 className="section-title">About</h3>
        <p className="text-sm text-text-secondary">
          AI-powered desktop career intelligence platform for resume generation,
          ATS optimization, document management, and career development.
        </p>
      </div>
      <div className="card space-y-3">
        <h3 className="section-title">License</h3>
        <p className="text-sm text-text-secondary">CareerForge AI — All rights reserved.</p>
      </div>
      <div className="card space-y-3">
        <h3 className="section-title">Third-Party Libraries</h3>
        <div className="grid grid-cols-2 gap-2 text-xs text-text-secondary">
          <span>React 19</span><span>FastAPI</span>
          <span>SQLAlchemy 2.0</span><span>LanceDB</span>
          <span>Tauri 2</span><span>Typst</span>
          <span>Zustand 5</span><span>Pydantic 2</span>
          <span>Tailwind CSS</span><span>structlog</span>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [onboarded, setOnboarded] = useState(
    () => localStorage.getItem("careerforge_onboarding_complete") === "true",
  );

  if (!onboarded) {
    return <Onboarding onComplete={() => setOnboarded(true)} />;
  }

  return (
    <ErrorBoundary>
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
          <Route path="resume" element={<ResumeGenerator />} />
          <Route path="ats" element={<ATSDashboard />} />
          <Route path="documents" element={<div className="p-8 text-text-secondary">Document Vault — coming soon</div>} />
          <Route path="settings/updates" element={<UpdateSettings />} />
          <Route path="settings" element={<div className="p-8 text-text-secondary">Settings — coming soon</div>} />
          <Route path="help" element={<Feedback />} />
          <Route path="about" element={<AboutPage />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  );
}

export default App;
