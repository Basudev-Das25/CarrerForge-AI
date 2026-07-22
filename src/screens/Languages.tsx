import { useEffect, useState } from "react";
import { Plus, Trash2, Edit3, Globe } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Language } from "@/types";

const PROFICIENCIES = ["native", "fluent", "advanced", "intermediate", "beginner"];
const emptyForm = { name: "", proficiency: "", years: "", is_native: false };

export default function Languages() {
  const [items, setItems] = useState<Language[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = () => api.listLanguages().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const openNew = () => { setForm(emptyForm); setEditId(null); setModalOpen(true); };
  const openEdit = (lang: Language) => {
    setForm({ name: lang.name, proficiency: lang.proficiency || "", years: lang.years?.toString() || "", is_native: lang.is_native });
    setEditId(lang.id); setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.name.trim()) { toast.error("Name is required"); return; }
    setSaving(true);
    try {
      const data = { ...form, years: form.years ? parseFloat(form.years) : undefined };
      if (editId) { await api.updateLanguage(editId, data); toast.success("Updated"); }
      else { await api.createLanguage(data); toast.success("Added"); }
      setModalOpen(false); load();
    } catch { toast.error("Failed to save"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this language?")) return;
    try { await api.deleteLanguage(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  const proficiencyColor = (p?: string) => {
    if (p === "native") return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    if (p === "fluent") return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    if (p === "advanced") return "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400";
    if (p === "intermediate") return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400";
    return "bg-surface-2 text-text-secondary";
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Languages</h1>
          <p className="mt-1 text-sm text-text-secondary">{items.length} languages spoken</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Language</Button>
      </div>

      {loading ? (
        <div className="flex flex-wrap gap-2">{[...Array(6)].map((_, i) => <div key={i} className="h-10 w-28 shimmer rounded-full" />)}</div>
      ) : items.length === 0 ? (
        <EmptyState icon={<Globe className="h-8 w-8" />} title="No languages added" description="Add the languages you speak" action={<Button onClick={openNew}>Add Language</Button>} />
      ) : (
        <div className="flex flex-wrap gap-3">
          {items.map((lang) => (
            <div key={lang.id} className="group card-hover flex items-center gap-3 px-4 py-3">
              <Globe className="h-4 w-4 text-text-tertiary shrink-0" />
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-text-primary">{lang.name}</span>
                  {lang.is_native && <span className="text-2xs text-brand-600 font-medium">Native</span>}
                </div>
                <div className="flex items-center gap-2 mt-0.5">
                  {lang.proficiency && (
                    <span className={`badge text-2xs ${proficiencyColor(lang.proficiency)}`}>{lang.proficiency}</span>
                  )}
                  {lang.years && <span className="text-2xs text-text-tertiary">{lang.years}y</span>}
                </div>
              </div>
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                <button onClick={() => openEdit(lang)} className="rounded p-1 hover:bg-surface-2"><Edit3 className="h-3.5 w-3.5 text-text-tertiary" /></button>
                <button onClick={() => handleDelete(lang.id)} className="rounded p-1 hover:bg-red-50"><Trash2 className="h-3.5 w-3.5 text-red-500" /></button>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Language" : "Add Language"} size="sm">
        <div className="space-y-4">
          <Input label="Language *" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="English" autoFocus />
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Proficiency</label>
            <select value={form.proficiency} onChange={(e) => setForm((f) => ({ ...f, proficiency: e.target.value }))} className="input">
              <option value="">Select...</option>
              {PROFICIENCIES.map((p) => <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>)}
            </select>
          </div>
          <Input label="Years of Practice" value={form.years} onChange={(e) => setForm((f) => ({ ...f, years: e.target.value }))} type="number" placeholder="10" />
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.is_native} onChange={(e) => setForm((f) => ({ ...f, is_native: e.target.checked }))} className="rounded border-border" />
            <span className="text-sm text-text-primary">Native speaker</span>
          </label>
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>{editId ? "Update" : "Add"}</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
