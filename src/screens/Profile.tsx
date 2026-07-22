import { useEffect, useState } from "react";
import { Save, User as UserIcon } from "lucide-react";
import { api } from "@/services/api";
import { Input } from "@/components/common/Input";
import { Button } from "@/components/common/Button";
import { toast } from "@/components/common/Toast";

interface ProfileData {
  id?: string;
  full_name: string;
  email: string;
  phone: string;
  location: string;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  summary: string;
}

const empty: ProfileData = {
  full_name: "", email: "", phone: "", location: "",
  linkedin_url: "", github_url: "", portfolio_url: "", summary: "",
};

export default function Profile() {
  const [form, setForm] = useState<ProfileData>(empty);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getProfile()
      .then((p) => setForm({
        full_name: p.full_name || "",
        email: p.email || "",
        phone: p.phone || "",
        location: p.location || "",
        linkedin_url: p.linkedin_url || "",
        github_url: p.github_url || "",
        portfolio_url: p.portfolio_url || "",
        summary: p.summary || "",
      }))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const update = (field: keyof ProfileData) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
      setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.updateProfile(form);
      toast.success("Profile saved");
    } catch {
      toast.error("Failed to save profile");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="space-y-4">{[...Array(6)].map((_, i) => <div key={i} className="h-16 shimmer rounded-xl" />)}</div>;
  }

  return (
    <div className="max-w-2xl space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Personal Information</h1>
          <p className="mt-1 text-sm text-text-secondary">Your basic professional details</p>
        </div>
        <Button onClick={handleSave} loading={saving} icon={<Save className="h-4 w-4" />}>
          Save
        </Button>
      </div>

      {/* Avatar */}
      <div className="flex items-center gap-4">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-surface-2 text-text-tertiary">
          <UserIcon className="h-10 w-10" />
        </div>
        <div>
          <p className="font-medium text-text-primary">{form.full_name || "Your Name"}</p>
          <p className="text-sm text-text-secondary">{form.email || "email@example.com"}</p>
        </div>
      </div>

      {/* Basic Info */}
      <div className="card space-y-4">
        <h3 className="section-title">Basic Information</h3>
        <div className="grid grid-cols-2 gap-4">
          <Input label="Full Name" value={form.full_name} onChange={update("full_name")} placeholder="Alex Rivera" />
          <Input label="Email" type="email" value={form.email} onChange={update("email")} placeholder="alex@example.com" />
          <Input label="Phone" value={form.phone} onChange={update("phone")} placeholder="+1-555-0100" />
          <Input label="Location" value={form.location} onChange={update("location")} placeholder="San Francisco, CA" />
        </div>
      </div>

      {/* Links */}
      <div className="card space-y-4">
        <h3 className="section-title">Online Presence</h3>
        <div className="space-y-4">
          <Input label="LinkedIn URL" value={form.linkedin_url} onChange={update("linkedin_url")} placeholder="https://linkedin.com/in/yourprofile" />
          <Input label="GitHub URL" value={form.github_url} onChange={update("github_url")} placeholder="https://github.com/yourusername" />
          <Input label="Portfolio URL" value={form.portfolio_url} onChange={update("portfolio_url")} placeholder="https://yoursite.com" />
        </div>
      </div>

      {/* Summary */}
      <div className="card space-y-4">
        <h3 className="section-title">Professional Summary</h3>
        <p className="text-xs text-text-tertiary">A brief overview of your professional background. This appears at the top of your resume.</p>
        <textarea
          value={form.summary}
          onChange={update("summary")}
          rows={5}
          className="input resize-none"
          placeholder="Senior software engineer with 8+ years of experience building scalable distributed systems..."
        />
        <p className="text-xs text-text-tertiary text-right">{form.summary.length} / 500 characters</p>
      </div>
    </div>
  );
}
