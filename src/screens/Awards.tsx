import { useEffect, useState } from "react";
import { Plus, Trophy, Trash2, Edit3, ExternalLink } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Award } from "@/types";

const CATEGORIES = ["academic", "professional", "competition", "community", "other"];
const emptyForm = { title: "", issuer: "", date: "", category: "", description: "", url: "" };

export default function Awards() {
  const [items, setItems] = useState<Award[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [filter, setFilter] = useState("all");

  const load = () => api.listAwards().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const filtered = filter === "all" ? items : items.filter((a) => a.category === filter);

  const openNew = () => { setForm(emptyForm); setEditId(null); setModalOpen(true); };
  const openEdit = (award: Award) => {
    setForm({ title: award.title, issuer: award.issuer || "", date: award.date || "", category: award.category || "", description: award.description || "", url: award.url || "" });
    setEditId(award.id); setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) { toast.error("Title is required"); return; }
    setSaving(true);
    try {
      const data = {
        title: form.title,
        issuer: form.issuer || null,
        date: form.date || null,
        category: form.category || null,
        description: form.description || null,
        url: form.url || null,
      };
      if (editId) { await api.updateAward(editId, data); toast.success("Updated"); }
      else { await api.createAward(data); toast.success("Added"); }
      setModalOpen(false); load();
    } catch { toast.error("Failed to save"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this award?")) return;
    try { await api.deleteAward(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  const categoryColor = (c?: string) => {
    if (c === "academic") return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    if (c === "professional") return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400";
    if (c === "competition") return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400";
    return "bg-surface-2 text-text-secondary";
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Awards</h1>
          <p className="mt-1 text-sm text-text-secondary">{items.length} awards and honors</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Award</Button>
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
        <EmptyState icon={<Trophy className="h-8 w-8" />} title="No awards yet" description="Add your awards and honors" action={<Button onClick={openNew}>Add Award</Button>} />
      ) : (
        <div className="space-y-3">
          {filtered.map((award) => (
            <div key={award.id} className="card-hover group">
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400">
                    <Trophy className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{award.title}</h3>
                    <div className="flex items-center gap-3 mt-1">
                      {award.issuer && <span className="text-sm text-text-secondary">{award.issuer}</span>}
                      {award.date && <span className="text-xs text-text-tertiary">{award.date}</span>}
                      {award.category && <span className={`badge text-2xs ${categoryColor(award.category)}`}>{award.category}</span>}
                    </div>
                    {award.description && <p className="mt-2 text-sm text-text-secondary line-clamp-2">{award.description}</p>}
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {award.url && <a href={award.url} target="_blank" rel="noreferrer" className="rounded p-1.5 hover:bg-surface-2"><ExternalLink className="h-4 w-4 text-text-tertiary" /></a>}
                  <button onClick={() => openEdit(award)} className="rounded p-1.5 hover:bg-surface-2"><Edit3 className="h-4 w-4 text-text-tertiary" /></button>
                  <button onClick={() => handleDelete(award.id)} className="rounded p-1.5 hover:bg-red-50"><Trash2 className="h-4 w-4 text-red-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Award" : "Add Award"} size="lg">
        <div className="space-y-4">
          <Input label="Title *" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} placeholder="Best Paper Award" autoFocus />
          <div className="grid grid-cols-2 gap-4">
            <Input label="Issuer" value={form.issuer} onChange={(e) => setForm((f) => ({ ...f, issuer: e.target.value }))} placeholder="IEEE" />
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
            <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={3} className="input resize-none" placeholder="Describe the award..." />
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
