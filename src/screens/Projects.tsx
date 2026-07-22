import { useEffect, useState } from "react";
import { Plus, Code, Trash2, Edit3, ExternalLink, Star, GitBranch } from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { Input } from "@/components/common/Input";
import { Modal } from "@/components/common/Modal";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { Project } from "@/types";

const STATUSES = ["planning", "in-progress", "completed", "archived"];
const DIFFICULTIES = ["beginner", "intermediate", "advanced", "expert"];

const emptyForm = {
  name: "", description: "", role: "", repo_url: "", live_url: "",
  tech_stack: "", industry: "", category: "", team_size: "",
  difficulty: "", tags: "", keywords: "", responsibilities: "",
  impact_metrics: "", skills_used: "", highlights: "",
  visibility: "private", status: "completed", start_date: "", end_date: "",
  is_featured: false,
};

export default function Projects() {
  const [items, setItems] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [filter, setFilter] = useState("all");

  const load = () => api.listProjects().then(setItems).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const filtered = filter === "all" ? items : items.filter((p) => p.status === filter);

  const openNew = () => { setForm(emptyForm); setEditId(null); setModalOpen(true); };
  const openEdit = (proj: Project) => {
    setForm({
      name: proj.name, description: proj.description || "", role: proj.role || "",
      repo_url: proj.repo_url || "", live_url: proj.live_url || "",
      tech_stack: proj.tech_stack.join(", "), industry: proj.industry || "",
      category: proj.category || "", team_size: proj.team_size?.toString() || "",
      difficulty: proj.difficulty || "", tags: proj.tags.join(", "),
      keywords: proj.keywords.join(", "), responsibilities: proj.responsibilities.join("\n"),
      impact_metrics: proj.impact_metrics.join("\n"), skills_used: proj.skills_used.join(", "),
      highlights: proj.highlights.join("\n"), visibility: proj.visibility,
      status: proj.status, start_date: proj.start_date || "", end_date: proj.end_date || "",
      is_featured: proj.is_featured,
    });
    setEditId(proj.id); setModalOpen(true);
  };

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  const handleSave = async () => {
    if (!form.name.trim()) { toast.error("Name is required"); return; }
    setSaving(true);
    try {
      const data = {
        ...form,
        tech_stack: form.tech_stack.split(",").map((s) => s.trim()).filter(Boolean),
        tags: form.tags.split(",").map((s) => s.trim()).filter(Boolean),
        keywords: form.keywords.split(",").map((s) => s.trim()).filter(Boolean),
        skills_used: form.skills_used.split(",").map((s) => s.trim()).filter(Boolean),
        responsibilities: form.responsibilities.split("\n").filter(Boolean),
        impact_metrics: form.impact_metrics.split("\n").filter(Boolean),
        highlights: form.highlights.split("\n").filter(Boolean),
        team_size: form.team_size ? parseInt(form.team_size) : undefined,
      };
      if (editId) { await api.updateProject(editId, data); toast.success("Updated"); }
      else { await api.createProject(data); toast.success("Added"); }
      setModalOpen(false); load();
    } catch { toast.error("Failed to save"); } finally { setSaving(false); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this project?")) return;
    try { await api.deleteProject(id); toast.success("Deleted"); load(); } catch { toast.error("Failed"); }
  };

  const statusColor = (s: string) => {
    if (s === "completed") return "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400";
    if (s === "in-progress") return "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400";
    if (s === "planning") return "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400";
    return "bg-surface-2 text-text-secondary";
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Projects</h1>
          <p className="mt-1 text-sm text-text-secondary">{items.length} projects</p>
        </div>
        <Button onClick={openNew} icon={<Plus className="h-4 w-4" />}>Add Project</Button>
      </div>

      <div className="flex gap-2">
        {["all", ...STATUSES].map((s) => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${filter === s ? "bg-brand-600 text-white" : "bg-surface-2 text-text-secondary hover:bg-surface-3"}`}>
            {s === "all" ? "All" : s.charAt(0).toUpperCase() + s.slice(1).replace("-", " ")}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-28 shimmer rounded-xl" />)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={<Code className="h-8 w-8" />} title="No projects yet" description="Add your projects to showcase your work" action={<Button onClick={openNew}>Add Project</Button>} />
      ) : (
        <div className="space-y-3">
          {filtered.map((proj) => (
            <div key={proj.id} className="card-hover group">
              <div className="flex items-start justify-between">
                <div className="flex gap-4">
                  <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-violet-50 text-violet-600 dark:bg-violet-950 dark:text-violet-400">
                    <Code className="h-6 w-6" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-text-primary">{proj.name}</h3>
                      {proj.is_featured && <Star className="h-3.5 w-3.5 text-amber-500 fill-amber-500" />}
                      <span className={`badge text-2xs ${statusColor(proj.status)}`}>{proj.status}</span>
                    </div>
                    {proj.description && <p className="mt-1 text-sm text-text-secondary line-clamp-2">{proj.description}</p>}
                    {proj.role && <p className="text-xs text-text-tertiary mt-1">Role: {proj.role}</p>}
                    {proj.tech_stack.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {proj.tech_stack.slice(0, 6).map((t, i) => <span key={i} className="badge-info text-2xs">{t}</span>)}
                        {proj.tech_stack.length > 6 && <span className="badge text-2xs bg-surface-2 text-text-tertiary">+{proj.tech_stack.length - 6}</span>}
                      </div>
                    )}
                    <div className="flex items-center gap-4 mt-2 text-xs text-text-tertiary">
                      {proj.start_date && <span>{proj.start_date} — {proj.end_date || "Present"}</span>}
                      {proj.team_size && <span>Team: {proj.team_size}</span>}
                      {proj.difficulty && <span className="capitalize">{proj.difficulty}</span>}
                    </div>
                  </div>
                </div>
                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  {proj.repo_url && <a href={proj.repo_url} target="_blank" rel="noreferrer" className="rounded p-1.5 hover:bg-surface-2"><GitBranch className="h-4 w-4 text-text-tertiary" /></a>}
                  {proj.live_url && <a href={proj.live_url} target="_blank" rel="noreferrer" className="rounded p-1.5 hover:bg-surface-2"><ExternalLink className="h-4 w-4 text-text-tertiary" /></a>}
                  <button onClick={() => openEdit(proj)} className="rounded p-1.5 hover:bg-surface-2"><Edit3 className="h-4 w-4 text-text-tertiary" /></button>
                  <button onClick={() => handleDelete(proj.id)} className="rounded p-1.5 hover:bg-red-50"><Trash2 className="h-4 w-4 text-red-500" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={editId ? "Edit Project" : "Add Project"} size="lg">
        <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
          <div className="grid grid-cols-2 gap-4">
            <Input label="Project Name *" value={form.name} onChange={update("name")} placeholder="CareerForge AI" autoFocus />
            <Input label="Role" value={form.role} onChange={update("role")} placeholder="Lead Developer" />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Description</label>
            <textarea value={form.description} onChange={update("description")} rows={3} className="input resize-none" placeholder="Brief description of the project..." />
          </div>
          <Input label="Tech Stack" value={form.tech_stack} onChange={update("tech_stack")} placeholder="React, TypeScript, FastAPI" hint="Comma-separated" />
          <div className="grid grid-cols-2 gap-4">
            <Input label="GitHub URL" value={form.repo_url} onChange={update("repo_url")} placeholder="https://github.com/..." />
            <Input label="Live Demo" value={form.live_url} onChange={update("live_url")} placeholder="https://..." />
          </div>
          <div className="grid grid-cols-3 gap-4">
            <Input label="Industry" value={form.industry} onChange={update("industry")} placeholder="Tech" />
            <Input label="Category" value={form.category} onChange={update("category")} placeholder="Web App" />
            <Input label="Team Size" value={form.team_size} onChange={update("team_size")} type="number" placeholder="5" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text-primary">Status</label>
              <select value={form.status} onChange={update("status")} className="input">
                {STATUSES.map((s) => <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1).replace("-", " ")}</option>)}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text-primary">Difficulty</label>
              <select value={form.difficulty} onChange={update("difficulty")} className="input">
                <option value="">Select...</option>
                {DIFFICULTIES.map((d) => <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>)}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input label="Start Date" value={form.start_date} onChange={update("start_date")} placeholder="2024-01" hint="YYYY-MM" />
            <Input label="End Date" value={form.end_date} onChange={update("end_date")} placeholder="2024-06" hint="YYYY-MM" />
          </div>
          <Input label="Tags" value={form.tags} onChange={update("tags")} placeholder="web, ai, fullstack" hint="Comma-separated" />
          <Input label="Skills Used" value={form.skills_used} onChange={update("skills_used")} placeholder="Python, React" hint="Comma-separated" />
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Highlights</label>
            <textarea value={form.highlights} onChange={update("highlights")} rows={3} className="input resize-none" placeholder="One per line" />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Impact Metrics</label>
            <textarea value={form.impact_metrics} onChange={update("impact_metrics")} rows={2} className="input resize-none" placeholder="One per line&#10;10k+ users&#10;99.9% uptime" />
          </div>
          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text-primary">Responsibilities</label>
            <textarea value={form.responsibilities} onChange={update("responsibilities")} rows={2} className="input resize-none" placeholder="One per line" />
          </div>
          <label className="flex items-center gap-2 cursor-pointer">
            <input type="checkbox" checked={form.is_featured} onChange={(e) => setForm((f) => ({ ...f, is_featured: e.target.checked }))} className="rounded border-border" />
            <span className="text-sm text-text-primary">Featured project</span>
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
