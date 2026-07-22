import { useEffect, useState } from "react";
import { Plus, LinkIcon, Trash2, Edit3, ExternalLink } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { SocialLink } from "@/types";

const PLATFORMS = ["LinkedIn", "GitHub", "Twitter", "Portfolio", "YouTube", "Medium", "Dev.to", "Dribbble", "Behance", "Instagram", "Other"];
const emptyForm = { platform: "", url: "", username: "", display_name: "" };

export default function Links() {
  const [items, setItems] = useState<SocialLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = () => api.listSocialLinks().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const openNew = () => { setForm(emptyForm); setEditId(null); setModalOpen(true); };
  const openEdit = (link: SocialLink) => {
    setForm({ platform: link.platform, url: link.url, username: link.username || "", display_name: link.display_name || "" });
    setEditId(link.id); setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.platform.trim() || !form.url.trim()) { toast.error("Platform and URL are required"); return; }
    setSaving(true);
    try {
      if (editId) { await api.updateSocialLink(editId, form); toast.success("Updated"); }
      else { await api.createSocialLink(form); toast.success("Added"); }
      setModalOpen(false); load();
    } catch { toast.error("Failed to save"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this link?")) return;
    try { await api.deleteSocialLink(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Social Links</h1>
          <p className="mt-1 text-sm text-text-secondary">{items.length} links</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Link</Button>
      </div>

      {loading ? (
        <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-16 shimmer rounded-xl" />)}</div>
      ) : items.length === 0 ? (
        <EmptyState icon={<LinkIcon className="h-8 w-8" />} title="No social links" description="Add links to your professional profiles" action={<Button onClick={openNew}>Add Link</Button>} />
      ) : (
        <div className="space-y-3">
          {items.map((link) => (
            <div key={link.id} className="card-hover group">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-cyan-50 text-cyan-600 dark:bg-cyan-950 dark:text-cyan-400">
                    <LinkIcon className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-text-primary">{link.platform}</h3>
                      {link.username && <span className="text-sm text-text-secondary">@{link.username}</span>}
                    </div>
                    <a href={link.url} target="_blank" rel="noreferrer" className="text-xs text-brand-600 hover:underline flex items-center gap-1 mt-0.5">
                      {link.url} <ExternalLink className="h-3 w-3" />
                    </a>
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => openEdit(link)} className="rounded p-1.5 hover:bg-surface-2"><Edit3 className="h-4 w-4 text-text-tertiary" /></button>
                  <button onClick={() => handleDelete(link.id)} className="rounded p-1.5 hover:bg-red-50"><Trash2 className="h-4 w-4 text-red-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Link" : "Add Link"} size="md">
        <div className="space-y-4">
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Platform *</label>
            <select value={form.platform} onChange={(e) => setForm((f) => ({ ...f, platform: e.target.value }))} className="input">
              <option value="">Select...</option>
              {PLATFORMS.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <Input label="URL *" value={form.url} onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))} placeholder="https://linkedin.com/in/yourprofile" autoFocus />
          <Input label="Username" value={form.username} onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))} placeholder="yourusername" />
          <Input label="Display Name" value={form.display_name} onChange={(e) => setForm((f) => ({ ...f, display_name: e.target.value }))} placeholder="Your Name" />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>{editId ? "Update" : "Add"}</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
