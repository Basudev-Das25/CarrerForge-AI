import { useEffect, useState } from "react";
import { Plus, BookOpen, Trash2, Edit3, ExternalLink } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Publication } from "@/types";

const CATEGORIES = ["journal", "conference", "workshop", "preprint", "book", "other"];
const emptyForm = { title: "", authors: "", venue: "", date: "", url: "", doi: "", description: "", category: "" };

export default function Publications() {
  const [items, setItems] = useState<Publication[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [filter, setFilter] = useState("all");

  const load = () => api.listPublications().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const filtered = filter === "all" ? items : items.filter((p) => p.category === filter);

  const openNew = () => { setForm(emptyForm); setEditId(null); setModalOpen(true); };
  const openEdit = (pub: Publication) => {
    setForm({ title: pub.title, authors: pub.authors.join(", "), venue: pub.venue || "", date: pub.date || "", url: pub.url || "", doi: pub.doi || "", description: pub.description || "", category: pub.category || "" });
    setEditId(pub.id); setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.title.trim()) { toast.error("Title is required"); return; }
    setSaving(true);
    try {
      const data = {
        title: form.title,
        venue: form.venue || null,
        date: form.date || null,
        url: form.url || null,
        doi: form.doi || null,
        description: form.description || null,
        category: form.category || null,
        authors: form.authors.split(",").map((a) => a.trim()).filter(Boolean),
      };
      if (editId) { await api.updatePublication(editId, data); toast.success("Updated"); }
      else { await api.createPublication(data); toast.success("Added"); }
      setModalOpen(false); load();
    } catch { toast.error("Failed to save"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this publication?")) return;
    try { await api.deletePublication(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Publications</h1>
          <p className="mt-1 text-sm text-text-secondary">{items.length} publications</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Publication</Button>
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
        <EmptyState icon={<BookOpen className="h-8 w-8" />} title="No publications yet" description="Add your papers, articles, and publications" action={<Button onClick={openNew}>Add Publication</Button>} />
      ) : (
        <div className="space-y-3">
          {filtered.map((pub) => (
            <div key={pub.id} className="card-hover group">
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
                    <BookOpen className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{pub.title}</h3>
                    <p className="text-sm text-text-secondary">{pub.authors.join(", ")}</p>
                    <div className="flex items-center gap-3 mt-1">
                      {pub.venue && <span className="text-xs text-text-tertiary">{pub.venue}</span>}
                      {pub.date && <span className="text-xs text-text-tertiary">{pub.date}</span>}
                      {pub.category && <span className="badge-info text-2xs">{pub.category}</span>}
                    </div>
                    {pub.description && <p className="mt-2 text-sm text-text-secondary line-clamp-2">{pub.description}</p>}
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {pub.url && <a href={pub.url} target="_blank" rel="noreferrer" className="rounded p-1.5 hover:bg-surface-2"><ExternalLink className="h-4 w-4 text-text-tertiary" /></a>}
                  <button onClick={() => openEdit(pub)} className="rounded p-1.5 hover:bg-surface-2"><Edit3 className="h-4 w-4 text-text-tertiary" /></button>
                  <button onClick={() => handleDelete(pub.id)} className="rounded p-1.5 hover:bg-red-50"><Trash2 className="h-4 w-4 text-red-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Publication" : "Add Publication"} size="lg">
        <div className="space-y-4">
          <Input label="Title *" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} placeholder="Paper title" autoFocus />
          <Input label="Authors" value={form.authors} onChange={(e) => setForm((f) => ({ ...f, authors: e.target.value }))} placeholder="John Doe, Jane Smith" hint="Comma-separated" />
          <div className="grid grid-cols-2 gap-4">
            <Input label="Venue" value={form.venue} onChange={(e) => setForm((f) => ({ ...f, venue: e.target.value }))} placeholder="IEEE Conference 2024" />
            <Input label="Date" value={form.date} onChange={(e) => setForm((f) => ({ ...f, date: e.target.value }))} placeholder="2024-06" hint="YYYY-MM" />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Category</label>
            <select value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} className="input">
              <option value="">Select...</option>
              {CATEGORIES.map((c) => <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>)}
            </select>
          </div>
          <Input label="URL" value={form.url} onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))} placeholder="https://arxiv.org/abs/..." />
          <Input label="DOI" value={form.doi} onChange={(e) => setForm((f) => ({ ...f, doi: e.target.value }))} placeholder="10.1234/..." />
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Description</label>
            <textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} rows={3} className="input resize-none" placeholder="Brief description of the publication..." />
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
