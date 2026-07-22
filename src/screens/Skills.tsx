import { useEffect, useState } from "react";
import { Plus, Wrench, Trash2, Star } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Skill } from "@/types";

const CATEGORIES = ["programming", "framework", "tool", "soft", "domain"];
const LEVELS = ["beginner", "intermediate", "advanced", "expert"];

export default function Skills() {
  const [items, setItems] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ name: "", category: "", level: "", years_experience: "", is_primary: false });
  const [saving, setSaving] = useState(false);
  const [filter, setFilter] = useState<string>("all");

  const load = () => api.listSkills().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const filtered = filter === "all" ? items : items.filter((s) => s.category === filter);
  const grouped = CATEGORIES.reduce((acc, cat) => {
    acc[cat] = filtered.filter((s) => s.category === cat || (!s.category && cat === "tool"));
    return acc;
  }, {} as Record<string, Skill[]>);

  const handleSave = async () => {
    if (!form.name.trim()) { toast.error("Name is required"); return; }
    setSaving(true);
    try {
      const data = { ...form, years_experience: form.years_experience ? parseFloat(form.years_experience) : undefined };
      await api.createSkill(data);
      toast.success("Skill added");
      setModalOpen(false);
      setForm({ name: "", category: "", level: "", years_experience: "", is_primary: false });
      load();
    } catch { toast.error("Failed"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    try { await api.deleteSkill(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Skills</h1>
          <p className="mt-1 text-sm text-text-secondary">{items.length} skills in your arsenal</p>
        </div>
        <Button onClick={() => setModalOpen(true)} icon={<Plus className="h-4 w-4" />}>Add Skill</Button>
      </div>

      {/* Category Filters */}
      <div className="flex gap-2">
        {["all", ...CATEGORIES].map((cat) => (
          <button key={cat} onClick={() => setFilter(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${filter === cat ? "bg-brand-600 text-white" : "bg-surface-2 text-text-secondary hover:bg-surface-3"}`}>
            {cat === "all" ? "All" : cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="flex flex-wrap gap-2">{[...Array(12)].map((_, i) => <div key={i} className="h-8 w-24 shimmer rounded-full" />)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={<Wrench className="h-8 w-8" />} title="No skills yet" description="Add your technical and soft skills" action={<Button onClick={() => setModalOpen(true)}>Add Skills</Button>} />
      ) : filter === "all" ? (
        CATEGORIES.map((cat) => grouped[cat]?.length > 0 ? (
          <div key={cat}>
            <h3 className="text-sm font-medium text-text-tertiary uppercase tracking-wider mb-2">{cat}</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              {grouped[cat].map((skill) => (
                <span key={skill.id} className="group inline-flex items-center gap-1.5 rounded-full bg-surface-2 px-3 py-1.5 text-sm text-text-primary border border-border hover:border-brand-300 transition-colors">
                  {skill.is_primary && <Star className="h-3 w-3 text-amber-500 fill-amber-500" />}
                  {skill.name}
                  {skill.level && <span className="text-2xs text-text-tertiary ml-1">· {skill.level}</span>}
                  <button onClick={() => handleDelete(skill.id)} className="ml-1 opacity-0 group-hover:opacity-100 text-text-tertiary hover:text-red-500 transition-opacity">
                    <Trash2 className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        )) : null
      ) : (
        <div className="flex flex-wrap gap-2">
          {filtered.map((skill) => (
            <span key={skill.id} className="group inline-flex items-center gap-1.5 rounded-full bg-surface-2 px-3 py-1.5 text-sm text-text-primary border border-border">
              {skill.is_primary && <Star className="h-3 w-3 text-amber-500 fill-amber-500" />}
              {skill.name}
              <button onClick={() => handleDelete(skill.id)} className="ml-1 opacity-0 group-hover:opacity-100 text-text-tertiary hover:text-red-500"><Trash2 className="h-3 w-3" /></button>
            </span>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Add Skill" size="sm">
        <div className="space-y-4">
          <Input label="Skill Name *" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="Python" autoFocus />
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text-primary">Category</label>
              <select value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} className="input">
                <option value="">Select...</option>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text-primary">Level</label>
              <select value={form.level} onChange={(e) => setForm((f) => ({ ...f, level: e.target.value }))} className="input">
                <option value="">Select...</option>
                {LEVELS.map((l) => <option key={l} value={l}>{l.charAt(0).toUpperCase() + l.slice(1)}</option>)}
              </select>
            </div>
          </div>
          <Input label="Years of Experience" value={form.years_experience} onChange={(e) => setForm((f) => ({ ...f, years_experience: e.target.value }))} type="number" placeholder="3" />
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.is_primary} onChange={(e) => setForm((f) => ({ ...f, is_primary: e.target.checked }))} className="rounded border-border" />
            <span className="text-sm text-text-primary">Primary skill</span>
          </label>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>Add</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
