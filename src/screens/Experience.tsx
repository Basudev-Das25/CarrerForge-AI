import { useEffect, useState } from "react";
import { Plus, Briefcase, Trash2, Edit3 } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Experience as ExpType } from "@/types";

const empty = { company: "", title: "", location: "", employment_type: "", start_date: "", end_date: "", description: "", highlights: "", skills_used: "" };

export default function ExperienceScreen() {
  const [items, setItems] = useState<ExpType[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);

  const load = () => api.listExperience().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const openNew = () => { setForm(empty); setEditId(null); setModalOpen(true); };
  const openEdit = (exp: ExpType) => {
    setForm({
      company: exp.company, title: exp.title, location: exp.location || "",
      employment_type: exp.employment_type || "", start_date: exp.start_date, end_date: exp.end_date || "",
      description: exp.description || "", highlights: exp.highlights.join("\n"), skills_used: exp.skills_used.join(", "),
    });
    setEditId(exp.id); setModalOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const data = {
        ...form,
        highlights: form.highlights.split("\n").filter(Boolean),
        skills_used: form.skills_used.split(",").map((s) => s.trim()).filter(Boolean),
      };
      if (editId) { await api.updateExperience(editId, data); toast.success("Updated"); }
      else { await api.createExperience(data); toast.success("Added"); }
      setModalOpen(false); load();
    } catch { toast.error("Failed to save"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this experience?")) return;
    try { await api.deleteExperience(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Experience</h1>
          <p className="mt-1 text-sm text-text-secondary">Your professional work history</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Experience</Button>
      </div>

      {loading ? (
        <div className="space-y-4">{[...Array(3)].map((_, i) => <div key={i} className="h-24 shimmer rounded-xl" />)}</div>
      ) : items.length === 0 ? (
        <EmptyState icon={<Briefcase className="h-8 w-8" />} title="No experience added" description="Add your work history to build your resume" action={<Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Experience</Button>} />
      ) : (
        <div className="space-y-3">
          {items.map((exp) => (
            <div key={exp.id} className="card-hover group">
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
                    <Briefcase className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{exp.title}</h3>
                    <p className="text-sm text-text-secondary">{exp.company}{exp.location ? ` · ${exp.location}` : ""}</p>
                    <p className="text-xs text-text-tertiary mt-1">{exp.start_date} — {exp.end_date || "Present"}{exp.employment_type ? ` · ${exp.employment_type}` : ""}</p>
                    {exp.description && <p className="mt-2 text-sm text-text-secondary line-clamp-2">{exp.description}</p>}
                    {exp.highlights.length > 0 && (
                      <ul className="mt-2 space-y-1">{exp.highlights.slice(0, 3).map((h, i) => <li key={i} className="text-xs text-text-secondary">• {h}</li>)}</ul>
                    )}
                    {exp.skills_used.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {exp.skills_used.map((s, i) => <span key={i} className="badge-info">{s}</span>)}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => openEdit(exp)} className="rounded p-1.5 hover:bg-surface-2"><Edit3 className="h-4 w-4 text-text-tertiary" /></button>
                  <button onClick={() => handleDelete(exp.id)} className="rounded p-1.5 hover:bg-red-50"><Trash2 className="h-4 w-4 text-red-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Experience" : "Add Experience"} size="lg">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input label="Title *" value={form.title} onChange={update("title")} placeholder="Senior Software Engineer" />
            <Input label="Company *" value={form.company} onChange={update("company")} placeholder="Google" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input label="Location" value={form.location} onChange={update("location")} placeholder="Mountain View, CA" />
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text-primary">Employment Type</label>
              <select value={form.employment_type} onChange={update("employment_type")} className="input">
                <option value="">Select...</option>
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
                <option value="freelance">Freelance</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input label="Start Date *" value={form.start_date} onChange={update("start_date")} placeholder="2021-03" hint="YYYY-MM" />
            <Input label="End Date" value={form.end_date} onChange={update("end_date")} placeholder="2024-01" hint="YYYY-MM or blank" />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Description</label>
            <textarea value={form.description} onChange={update("description")} rows={3} className="input resize-none" placeholder="Brief description of your role..." />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Key Achievements</label>
            <textarea value={form.highlights} onChange={update("highlights")} rows={3} className="input resize-none" placeholder="One per line&#10;Increased revenue by 30%&#10;Led team of 5 engineers" />
          </div>
          <Input label="Skills Used" value={form.skills_used} onChange={update("skills_used")} placeholder="Python, React, AWS" hint="Comma-separated" />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>{editId ? "Update" : "Add"}</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
