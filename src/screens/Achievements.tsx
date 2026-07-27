import { useEffect, useState } from "react";
import { Plus, Trophy, Trash2, Edit3, ExternalLink } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Achievement } from "@/types";

const CATEGORIES = ["award", "publication", "patent", "speaking", "other"];
const emptyForm = { title: "", description: "", date: "", category: "", organization: "", url: "" };

export default function Achievements() {
  const [items, setItems] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [filter, setFilter] = useState("all");

  const load = () => api.listAchievements().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const filtered = filter === "all" ? items : items.filter((a) => a.category === filter);

  const openNew = () => { setForm(emptyForm); setEditId(null); setModalOpen(true); };
  const openEdit = (ach: Achievement) => {
    setForm({ title: ach.title, description: ach.description || "", date: ach.date || "", category: ach.category || "", organization: ach.organization || "", url: ach.url || "" });
    setEditId(ach.id); setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) { toast.error("Title is required"); return; }
    setSaving(true);
    try {
      const data = {
        title: form.title,
        description: form.description || null,
        date: form.date || null,
        category: form.category || null,
        organization: form.organization || null,
        url: form.url || null,
      };
      if (editId) { await api.updateAchievement(editId, data); toast.success("Updated"); }
      else { await api.createAchievement(data); toast.success("Added"); }
      setModalOpen(false); load();
    } catch { toast.error("Failed to save"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this achievement?")) return;
    try { await api.deleteAchievement(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  const categoryColor = (c?: string) => {
    if (c === "award") return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400";
    if (c === "publication") return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    if (c === "patent") return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400";
    if (c === "speaking") return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    return "bg-surface-2 text-text-secondary";
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Achievements</h1>
          <p className="mt-1 text-sm text-text-secondary">{items.length} achievements</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Achievement</Button>
      </div>

      <div className="flex gap-2">
        {["all", ...CATEGORIES].map((cat) => (
          <button key={cat} onClick={() => setFilter(cat)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${filter === cat ? "bg-brand-600 text-white" : "bg-surface-2 text-text-secondary hover:bg-surface-3"}`}>
            {cat === "all" ? "All" : cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-20 shimmer rounded-xl" />)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={<Trophy className="h-8 w-8" />} title="No achievements yet" description="Add your professional achievements" action={<Button onClick={openNew}>Add Achievement</Button>} />
      ) : (
        <div className="space-y-3">
          {filtered.map((ach) => (
            <div key={ach.id} className="card-hover group">
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400">
                    <Trophy className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-text-primary">{ach.title}</h3>
                      {ach.category && <span className={`badge text-2xs ${categoryColor(ach.category)}`}>{ach.category}</span>}
                    </div>
                    <div className="flex items-center gap-3 mt-1">
                      {ach.organization && <span className="text-sm text-text-secondary">{ach.organization}</span>}
                      {ach.date && <span className="text-xs text-text-tertiary">{ach.date}</span>}
                    </div>
                    {ach.description && <p className="mt-2 text-sm text-text-secondary line-clamp-2">{ach.description}</p>}
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {ach.url && <a href={ach.url} target="_blank" rel="noreferrer" className="rounded p-1.5 hover:bg-surface-2"><ExternalLink className="h-4 w-4 text-text-tertiary" /></a>}
                  <button onClick={() => openEdit(ach)} className="rounded p-1.5 hover:bg-surface-2"><Edit3 className="h-4 w-4 text-text-tertiary" /></button>
                  <button onClick={() => handleDelete(ach.id)} className="rounded p-1.5 hover:bg-red-50"><Trash2 className="h-4 w-4 text-red-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Achievement" : "Add Achievement"} size="lg">
        <div className="space-y-4">
          <Input label="Title *" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} placeholder="Best Paper Award" autoFocus />
          <div className="grid grid-cols-2 gap-4">
            <Input label="Organization" value={form.organization} onChange={(e) => setForm((f) => ({ ...f, organization: e.target.value }))} placeholder="IEEE" />
            <Input label="Date" value={form.date} onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))} placeholder="2024-06" hint="YYYY-MM" />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Category</label>
            <select value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} className="input">
              <option value="">Select...</option>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
            </select>
          </div>
          <Input label="URL" value={form.url} onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))} placeholder="https://..." />
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Description</label>
            <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={3} className="input resize-none" placeholder="Describe this achievement..." />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>{editId ? "Update" : "Add"}</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
