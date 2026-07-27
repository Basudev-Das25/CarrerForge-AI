import { useState } from "react";
import {
  ChevronRight,
  ChevronLeft,
  Check,
  Sparkles,
  Shield,
  Zap,
  FileText,
  Key,
} from "lucide-react";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { toast } from "@/components/common/Toast";

/* eslint-disable @typescript-eslint/no-explicit-any */

const PROVIDERS = [
  { id: "openai", name: "OpenAI", desc: "GPT-4o, GPT-4o-mini", key_field: "OPENAI_API_KEY" },
  { id: "claude", name: "Claude", desc: "Claude Sonnet, Opus", key_field: "ANTHROPIC_API_KEY" },
  { id: "openrouter", name: "OpenRouter", desc: "Multi-model gateway", key_field: "OPENROUTER_API_KEY" },
  { id: "ollama", name: "Ollama", desc: "Local models (no key)", key_field: "" },
  { id: "grok", name: "Grok", desc: "xAI models", key_field: "GROK_API_KEY" },
  { id: "huggingface", name: "HuggingFace", desc: "Free tier available", key_field: "HUGGINGFACE_API_KEY" },
];

interface Props {
  onComplete: () => void;
}

export default function Onboarding({ onComplete }: Props) {
  const [step, setStep] = useState(0);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [template, setTemplate] = useState("modern");

  const totalSteps = 4;

  const next = () => {
    if (step === 1 && !selectedProvider) { toast.error("Select a provider"); return; }
    if (step < totalSteps - 1) setStep(step + 1);
    else finish();
  };

  const back = () => { if (step > 0) setStep(step - 1); };

  const finish = async () => {
    try {
      // Save onboarding state
      localStorage.setItem("careerforge_onboarding_complete", "true");
      if (selectedProvider && apiKey) {
        localStorage.setItem(`careerforge_provider_${selectedProvider}`, apiKey);
        // Persist API key to backend so orchestrator can use it
        const payload: Record<string, string> = { ai_provider: selectedProvider };
        payload[`${selectedProvider}_api_key`] = apiKey;
        await fetch("http://127.0.0.1:8000/api/v1/config/ai", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
      }
      toast.success("Welcome to CareerForge AI!");
      onComplete();
    } catch {
      toast.error("Setup failed — you can configure settings later");
      onComplete();
    }
  };

  // Step 0: Welcome
  if (step === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-0">
        <div className="max-w-lg text-center space-y-8 animate-fade-in">
          <div className="flex justify-center">
            <div className="h-20 w-20 rounded-2xl bg-brand-600 flex items-center justify-center shadow-lg">
              <FileText className="h-10 w-10 text-white" />
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-text-primary">Welcome to CareerForge AI</h1>
            <p className="mt-3 text-text-secondary text-lg">The AI-powered career intelligence platform</p>
          </div>
          <div className="grid grid-cols-3 gap-6 text-left">
            <div className="card text-center space-y-2">
              <Shield className="h-8 w-8 text-brand-600 mx-auto" />
              <h3 className="font-medium text-text-primary text-sm">Local-First</h3>
              <p className="text-xs text-text-tertiary">All data stays on your device. No cloud storage.</p>
            </div>
            <div className="card text-center space-y-2">
              <Zap className="h-8 w-8 text-brand-600 mx-auto" />
              <h3 className="font-medium text-text-primary text-sm">AI-Powered</h3>
              <p className="text-xs text-text-tertiary">Generate resumes with evidence-backed AI.</p>
            </div>
            <div className="card text-center space-y-2">
              <Sparkles className="h-8 w-8 text-brand-600 mx-auto" />
              <h3 className="font-medium text-text-primary text-sm">ATS Optimized</h3>
              <p className="text-xs text-text-tertiary">Beat applicant tracking systems.</p>
            </div>
          </div>
          <Button size="lg" onClick={next} icon={<ChevronRight className="h-4 w-4" />}>
            Get Started
          </Button>
        </div>
      </div>
    );
  }

  // Step 1: Choose AI Provider
  if (step === 1) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-0">
        <div className="max-w-2xl w-full space-y-8 animate-fade-in">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-text-primary">Choose AI Provider</h1>
            <p className="mt-2 text-text-secondary">Select the AI service you want to use for resume generation</p>
          </div>
          <div className="grid grid-cols-3 gap-4">
            {PROVIDERS.map((p) => (
              <button key={p.id} onClick={() => { setSelectedProvider(p.id); setApiKey(""); }}
                className={`card text-left transition-all ${selectedProvider === p.id ? "ring-2 ring-brand-600 border-brand-600" : "hover:shadow-elevation-2"}`}>
                <h3 className="font-semibold text-text-primary text-sm">{p.name}</h3>
                <p className="text-xs text-text-tertiary mt-1">{p.desc}</p>
              </button>
            ))}
          </div>
          {selectedProvider && (
            <div className="card space-y-4 animate-fade-in">
              <h3 className="section-title flex items-center gap-2">
                <Key className="h-4 w-4" /> Configure {PROVIDERS.find((p) => p.id === selectedProvider)?.name}
              </h3>
              {PROVIDERS.find((p) => p.id === selectedProvider)?.key_field ? (
                <Input label="API Key" type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)}
                  placeholder={`Enter your ${selectedProvider.toUpperCase()} API key`} />
              ) : (
                <p className="text-sm text-text-secondary">
                  Ollama runs locally — no API key needed. Install from{' '}
                  <a href="https://ollama.ai" target="_blank" className="text-brand-600 hover:underline">ollama.ai</a>
                </p>
              )}
            </div>
          )}
          <div className="flex justify-between">
            <Button variant="secondary" onClick={back} icon={<ChevronLeft className="h-4 w-4" />}>Back</Button>
            <Button onClick={next}>Next</Button>
          </div>
        </div>
      </div>
    );
  }

  // Step 2: Choose Template
  if (step === 2) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-0">
        <div className="max-w-2xl w-full space-y-8 animate-fade-in">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-text-primary">Choose Default Template</h1>
            <p className="mt-2 text-text-secondary">You can change this later</p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {["modern", "minimal", "software", "academic"].map((t) => (
              <button key={t} onClick={() => setTemplate(t)}
                className={`card text-center py-8 transition-all ${template === t ? "ring-2 ring-brand-600 border-brand-600" : "hover:shadow-elevation-2"}`}>
                <FileText className="h-8 w-8 text-text-tertiary mx-auto mb-2" />
                <h3 className="font-semibold text-text-primary capitalize">{t}</h3>
                <p className="text-xs text-text-tertiary mt-1">
                  {t === "modern" ? "Clean, modern professional" : t === "minimal" ? "Minimalist, content-forward" : t === "software" ? "Technical with skills grid" : "Formal academic CV"}
                </p>
              </button>
            ))}
          </div>
          <div className="flex justify-between">
            <Button variant="secondary" onClick={back} icon={<ChevronLeft className="h-4 w-4" />}>Back</Button>
            <Button onClick={next}>Next</Button>
          </div>
        </div>
      </div>
    );
  }

  // Step 3: Finish
  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-0">
      <div className="max-w-lg text-center space-y-8 animate-fade-in">
        <div className="flex justify-center">
          <div className="h-20 w-20 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center">
            <Check className="h-10 w-10 text-green-600" />
          </div>
        </div>
        <div>
          <h1 className="text-3xl font-bold text-text-primary">You're All Set!</h1>
          <p className="mt-3 text-text-secondary">CareerForge AI is configured and ready to use</p>
        </div>
        <div className="card text-left space-y-3">
          <div className="flex items-center gap-3">
            <span className="badge badge-success text-xs">✓</span>
            <span className="text-sm text-text-secondary">Provider: {selectedProvider || "Ollama (local)"}</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="badge badge-success text-xs">✓</span>
            <span className="text-sm text-text-secondary">Template: {template}</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="badge badge-success text-xs">✓</span>
            <span className="text-sm text-text-secondary">Local-first, private, and ready</span>
          </div>
        </div>
        <Button size="lg" onClick={finish} icon={<Sparkles className="h-4 w-4" />}>
          Launch CareerForge AI
        </Button>
      </div>
    </div>
  );
}
