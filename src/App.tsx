import { Routes, Route } from "react-router-dom";
import { useState, useEffect, Suspense, lazy } from "react";
import { AppLayout } from "./components/layout/AppLayout";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import Onboarding from "./screens/Onboarding/index";
const Dashboard = lazy(() => import("./screens/Dashboard"));
const Profile = lazy(() => import("./screens/Profile"));
const Education = lazy(() => import("./screens/Education"));
const Experience = lazy(() => import("./screens/Experience"));
const Projects = lazy(() => import("./screens/Projects"));
const Skills = lazy(() => import("./screens/Skills"));
const Certificates = lazy(() => import("./screens/Certificates"));
const Achievements = lazy(() => import("./screens/Achievements"));
const Languages = lazy(() => import("./screens/Languages"));
const Publications = lazy(() => import("./screens/Publications"));
const Awards = lazy(() => import("./screens/Awards"));
const Links = lazy(() => import("./screens/Links"));
const ResumeGenerator = lazy(() => import("./screens/ResumeGenerator"));
const ResumeStudio = lazy(() => import("./screens/ResumeStudio"));
const DocumentVault = lazy(() => import("./screens/DocumentVault"));
const ATSDashboard = lazy(() => import("./screens/ATSDashboard"));
const UpdateSettings = lazy(() => import("./screens/UpdateSettings"));
const Settings = lazy(() => import("./screens/Settings"));
const Feedback = lazy(() => import("./screens/Feedback"));

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

function LoadingScreen({ message }: { message: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-0">
      <div className="text-center space-y-6">
        <div className="flex justify-center">
          <div className="h-16 w-16 rounded-2xl bg-brand-600 flex items-center justify-center shadow-lg animate-pulse">
            <span className="text-white text-2xl font-bold">CF</span>
          </div>
        </div>
        <div>
          <h1 className="text-xl font-bold text-text-primary">CareerForge AI</h1>
          <p className="mt-2 text-sm text-text-secondary">{message}</p>
        </div>
        <div className="flex justify-center">
          <div className="h-1 w-32 rounded-full bg-surface-2 overflow-hidden">
            <div className="h-full rounded-full bg-brand-500 animate-pulse" style={{ width: "60%" }} />
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const [onboarded, setOnboarded] = useState(
    () => localStorage.getItem("careerforge_onboarding_complete") === "true",
  );
  const [backendReady, setBackendReady] = useState(false);
  const [backendMessage, setBackendMessage] = useState("Starting backend...");

  useEffect(() => {
    let attempts = 0;
    const maxAttempts = 60; // 60 seconds total
    let backendRequested = false;
    let cancelled = false;

    const poll = async () => {
      let tauriCore: typeof import("@tauri-apps/api/core") | null = null;
      try {
        tauriCore = await import("@tauri-apps/api/core");
      } catch {
        // Tauri not available (web mode)
      }

      while (!cancelled && attempts < maxAttempts) {
        attempts++;

        try {
          // Call the Tauri health command first - this is more reliable in production
          if (!tauriCore) throw new Error("Tauri not available");
          const health = await tauriCore.invoke<string>("get_health");
          const healthData = JSON.parse(health);
          if (healthData?.status === "ok" || healthData?.status === "healthy") {
            setBackendReady(true);
            return;
          }
        } catch {
          // Tauri command failed or not available, try direct API health check
          try {
            const resp = await fetch("http://127.0.0.1:8000/api/v1/health");
            if (resp.ok) {
              const data = await resp.json();
              if (data?.status === "healthy" || data?.status === "ok") {
                setBackendReady(true);
                return;
              }
            }
          } catch {
            // Both health checks failed
          }
        }

        // After a few failed attempts, ask Tauri to start the backend
        if (attempts === 3 && !backendRequested) {
          backendRequested = true;
          setBackendMessage("Starting backend...");
          try {
            if (tauriCore) {
              await tauriCore.invoke("start_backend");
            }
          } catch {
            // start_backend failed — keep polling, maybe it's already running
          }
        }

        setBackendMessage(`Waiting for backend... (${attempts}/${maxAttempts})`);
        await new Promise((r) => setTimeout(r, 1000));
      }

      if (!cancelled) {
        // Read the startup log to show the user what failed
        let logDetail = "";
        try {
          if (tauriCore) {
            logDetail = await tauriCore.invoke<string>("get_backend_log").catch(() => "");
          }
        } catch {
          // invoke not available (web mode)
        }
        setBackendMessage(
          logDetail
            ? `Backend failed to start. Log:\n${logDetail.slice(-800)}`
            : "Backend not available. Check backend-startup.log next to the .exe for details.",
        );
      }
    };

    poll();
    return () => { cancelled = true; };
  }, []);

  if (!onboarded) {
    return <Onboarding onComplete={() => setOnboarded(true)} />;
  }

  if (!backendReady) {
    return <LoadingScreen message={backendMessage} />;
  }

  return (
    <ErrorBoundary>
      <Suspense fallback={<div className="flex items-center justify-center p-8"><div className="h-8 w-8 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" /></div>}>
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
            <Route path="resume" element={<ResumeStudio />} />
            <Route path="resume/legacy" element={<ResumeGenerator />} />
            <Route path="ats" element={<ATSDashboard />} />
            <Route path="documents" element={<DocumentVault />} />
            <Route path="settings/updates" element={<UpdateSettings />} />
            <Route path="settings" element={<Settings />} />
            <Route path="help" element={<Feedback />} />
            <Route path="feedback" element={<Feedback />} />
            <Route path="about" element={<AboutPage />} />
          </Route>
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
}

export default App;
