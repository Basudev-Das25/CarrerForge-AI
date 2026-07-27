import { useEffect, useState } from "react";
import { Plus, GraduationCap, Trash2, Edit3 } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Education as EducationType } from "@/types";

const emptyForm = { degree: "", field_of_study: "", institution: "", location: "", start_date: "", end_date: "", gpa: "", description: "", highlights: "" };

export default function Education() {
  const [items, setItems] = useState<EducationType[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);

  const load = () => api.listEducation().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const openNew = () => { setForm(emptyForm); setEditId(null); setModalOpen(true); };
  const openEdit = (edu: EducationType) => {
    setForm({
      degree: edu.degree, field_of_study: edu.field_of_study || "", institution: edu.institution,
      location: edu.location || "", start_date: edu.start_date, end_date: edu.end_date || "",
      gpa: edu.gpa?.toString() || "", description: edu.description || "", highlights: edu.highlights.join("\n"),
    });
    setEditId(edu.id);
    setModalOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const data = {
        degree: form.degree,
        institution: form.institution,
        start_date: form.start_date,
        field_of_study: form.field_of_study || null,
        location: form.location || null,
        end_date: form.end_date || null,
        gpa: form.gpa ? parseFloat(form.gpa) : null,
        description: form.description || null,
        highlights: form.highlights.split("\n").filter(Boolean),
      };
      if (editId) {
        await api.updateEducation(editId, data);
        toast.success("Education updated");
      } else {
        await api.createEducation(data);
        toast.success("Education added");
      }
      setModalOpen(false);
      load();
    } catch {
      toast.error("Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this education?")) return;
    try {
      await api.deleteEducation(id);
      toast.success("Deleted");
      load();
    } catch {
      toast.error("Failed to delete");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Education</h1>
          <p className="mt-1 text-sm text-text-secondary">Your academic background</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Education</Button>
      </div>

      {loading ? (
        <div className="space-y-4">{[...Array(3)].map((_, i) => <div key={i} className="h-24 shimmer rounded-xl" />)}</div>
      ) : items.length === 0 ? (
        <EmptyState icon={<GraduationCap className="h-8 w-8" />} title="No education added" description="Add your degrees and academic achievements" action={<Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Education</Button>} />
      ) : (
        <div className="space-y-3">
          {items.map((edu) => (
            <div key={edu.id} className="card-hover group">
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-400">
                    <GraduationCap className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-text-primary">{edu.degree}{edu.field_of_study ? ` in ${edu.field_of_study}` : ""}</h3>
                    <p className="text-sm text-text-secondary">{edu.institution}</p>
                    <p className="text-xs text-text-tertiary mt-1">{edu.start_date} — {edu.end_date || "Present"}{edu.gpa ? ` · GPA: ${edu.gpa}` : ""}</p>
                    {edu.highlights.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {edu.highlights.map((h, i) => <li key={i} className="text-xs text-text-secondary">• {h}</li>)}
                      </ul>
                    )}
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => openEdit(edu)} className="rounded p-1.5 hover:bg-surface-2"><Edit3 className="h-4 w-4 text-text-tertiary" /></button>
                  <button onClick={() => handleDelete(edu.id)} className="rounded p-1.5 hover:bg-red-50"><Trash2 className="h-4 w-4 text-red-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Education" : "Add Education"} size="lg">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input label="Degree *" value={form.degree} onChange={update("degree")} placeholder="B.S. Computer Science" />
            <Input label="Field of Study" value={form.field_of_study} onChange={update("field_of_study")} placeholder="Computer Science" />
          </div>
          <Input label="Institution *" value={form.institution} onChange={update("institution")} placeholder="MIT" />
          <Input label="Location" value={form.location} onChange={update("location")} placeholder="Cambridge, MA" />
          <div className="grid grid-cols-2 gap-4">
            <Input label="Start Date *" value={form.start_date} onChange={update("start_date")} placeholder="2018-09" hint="YYYY-MM" />
            <Input label="End Date" value={form.end_date} onChange={update("end_date")} placeholder="2022-06" hint="YYYY-MM or blank" />
          </div>
          <Input label="GPA" value={form.gpa} onChange={update("gpa")} placeholder="3.8" type="number" />
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Highlights</label>
            <textarea value={form.highlights} onChange={update("highlights")} rows={3} className="input resize-none" placeholder="One per line&#10;Dean's List 2020-2022&#10;Senior thesis on ML" />
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
