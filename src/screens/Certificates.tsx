import { useEffect, useState } from "react";
import { Plus, Award, Trash2, Edit3, ExternalLink } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Certificate } from "@/types";

const VERIFICATION = ["unverified", "pending", "verified", "expired"];
const emptyForm = { title: "", issuer: "", issue_date: "", expiry_date: "", credential_id: "", credential_url: "", skills: "", level: "", tags: "", verification_status: "unverified" };

export default function Certificates() {
  const [items, setItems] = useState<Certificate[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = () => api.listCertificates().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const openNew = () => { setForm(emptyForm); setEditId(null); setModalOpen(true); };
  const openEdit = (cert: Certificate) => {
    setForm({
      title: cert.title, issuer: cert.issuer, issue_date: cert.issue_date || "", expiry_date: cert.expiry_date || "",
      credential_id: cert.credential_id || "", credential_url: cert.credential_url || "",
      skills: cert.skills.join(", "), level: cert.level || "", tags: cert.tags.join(", "),
      verification_status: cert.verification_status,
    });
    setEditId(cert.id); setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.title.trim() || !form.issuer.trim()) { toast.error("Title and issuer are required"); return; }
    setSaving(true);
    try {
      const data = { ...form, skills: form.skills.split(",").map((s) => s.trim()).filter(Boolean), tags: form.tags.split(",").map((s) => s.trim()).filter(Boolean) };
      if (editId) { await api.updateCertificate(editId, data); toast.success("Updated"); }
      else { await api.createCertificate(data); toast.success("Added"); }
      setModalOpen(false); load();
    } catch { toast.error("Failed to save"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this certificate?")) return;
    try { await api.deleteCertificate(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  const verifyColor = (v: string) => {
    if (v === "verified") return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    if (v === "expired") return "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400";
    if (v === "pending") return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400";
    return "bg-surface-2 text-text-secondary";
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Certificates</h1>
          <p className="mt-1 text-sm text-text-secondary">{items.length} certifications</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Certificate</Button>
      </div>

      {loading ? (
        <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-20 shimmer rounded-xl" />)}</div>
      ) : items.length === 0 ? (
        <EmptyState icon={<Award className="h-8 w-8" />} title="No certificates yet" description="Add your professional certifications" action={<Button onClick={openNew}>Add Certificate</Button>} />
      ) : (
        <div className="space-y-3">
          {items.map((cert) => (
            <div key={cert.id} className="card-hover group">
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
                    <Award className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-text-primary">{cert.title}</h3>
                      <span className={`badge text-2xs ${verifyColor(cert.verification_status)}`}>{cert.verification_status}</span>
                    </div>
                    <p className="text-sm text-text-secondary">{cert.issuer}</p>
                    <div className="flex items-center gap-3 mt-1 text-xs text-text-tertiary">
                      {cert.issue_date && <span>Issued: {cert.issue_date}</span>}
                      {cert.expiry_date && <span>Expires: {cert.expiry_date}</span>}
                      {cert.level && <span>Level: {cert.level}</span>}
                    </div>
                    {cert.skills.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {cert.skills.map((s, i) => <span key={i} className="badge-info text-2xs">{s}</span>)}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {cert.credential_url && <a href={cert.credential_url} target="_blank" rel="noreferrer" className="rounded p-1.5 hover:bg-surface-2"><ExternalLink className="h-4 w-4 text-text-tertiary" /></a>}
                  <button onClick={() => openEdit(cert)} className="rounded p-1.5 hover:bg-surface-2"><Edit3 className="h-4 w-4 text-text-tertiary" /></button>
                  <button onClick={() => handleDelete(cert.id)} className="rounded p-1.5 hover:bg-red-50"><Trash2 className="h-4 w-4 text-red-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Certificate" : "Add Certificate"} size="lg">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input label="Title *" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} placeholder="AWS Solutions Architect" autoFocus />
            <Input label="Issuer *" value={form.issuer} onChange={(e) => setForm((f) => ({ ...f, issuer: e.target.value }))} placeholder="Amazon Web Services" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input label="Issue Date" value={form.issue_date} onChange={(e) => setForm((f) => ({ ...f, issue_date: e.target.value }))} placeholder="2024-01" hint="YYYY-MM" />
            <Input label="Expiry Date" value={form.expiry_date} onChange={(e) => setForm((f) => ({ ...f, expiry_date: e.target.value }))} placeholder="2027-01" hint="YYYY-MM" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input label="Credential ID" value={form.credential_id} onChange={(e) => setForm((f) => ({ ...f, credential_id: e.target.value }))} placeholder="ABC123XYZ" />
            <Input label="Credential URL" value={form.credential_url} onChange={(e) => setForm((f) => ({ ...f, credential_url: e.target.value }))} placeholder="https://..." />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input label="Level" value={form.level} onChange={(e) => setForm((f) => ({ ...f, level: e.target.value }))} placeholder="Associate" />
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text-primary">Verification</label>
              <select value={form.verification_status} onChange={(e) => setForm((f) => ({ ...f, verification_status: e.target.value }))} className="input">
                {VERIFICATION.map((v) => <option key={v} value={v}>{v.charAt(0).toUpperCase() + v.slice(1)}</option>)}
              </select>
            </div>
          </div>
          <Input label="Skills" value={form.skills} onChange={(e) => setForm((f) => ({ ...f, skills: e.target.value }))} placeholder="AWS, Cloud, Networking" hint="Comma-separated" />
          <Input label="Tags" value={form.tags} onChange={(e) => setForm((f) => ({ ...f, tags: e.target.value }))} placeholder="cloud, infrastructure" hint="Comma-separated" />
          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSave} loading={saving}>{editId ? "Update" : "Add"}</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
