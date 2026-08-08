/**
 * Document Vault — upload, search, and manage source documents.
 *
 * Supports drag-and-drop multi-file upload, category filtering,
 * semantic search, OCR status tracking, and deletion.
 */

import { useEffect, useState, useCallback, useRef } from "react";
import {
  FolderOpen, Upload, FileText, File, Search, Trash2,
  Sparkles, CheckCircle2, Loader2, X,
} from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { EmptyState } from "@/components/common/EmptyState";
import { toast } from "@/components/common/Toast";
import type { OriginalDocument } from "@/types";

/* eslint-disable @typescript-eslint/no-explicit-any */

// ── Types & Constants ────────────────────────────────────────

const CATEGORIES = [
  { id: "all", label: "All", icon: FolderOpen },
  { id: "resume", label: "Resumes", icon: FileText },
  { id: "certificate", label: "Certificates", icon: CheckCircle2 },
  { id: "reference", label: "References", icon: File },
  { id: "other", label: "Other", icon: File },
] as const;

type CategoryId = (typeof CATEGORIES)[number]["id"];

const ACCEPTED_TYPES = [".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"];

// ── Helpers ──────────────────────────────────────────────────

function formatFileSize(bytes?: number): string {
  if (bytes == null) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso?: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString();
}

function getFileIcon(name: string) {
  const ext = name.split(".").pop()?.toLowerCase() || "";
  if (ext === "pdf") return <FileText className="h-8 w-8 text-red-500" />;
  if (["docx", "doc"].includes(ext)) return <FileText className="h-8 w-8 text-blue-500" />;
  if (["png", "jpg", "jpeg", "gif", "webp"].includes(ext)) return <File className="h-8 w-8 text-purple-500" />;
  if (ext === "txt") return <FileText className="h-8 w-8 text-gray-500" />;
  return <File className="h-8 w-8 text-text-tertiary" />;
}

function categoryBadge(category?: string) {
  switch (category) {
    case "resume": return <span className="badge badge-success text-2xs">Resume</span>;
    case "certificate": return <span className="badge badge-info text-2xs">Certificate</span>;
    case "reference": return <span className="badge badge-warning text-2xs">Reference</span>;
    default: return <span className="badge text-2xs bg-surface-2 text-text-tertiary">Other</span>;
  }
}

// ── Main Component ───────────────────────────────────────────

export default function DocumentVault() {
  // ── State ────────────────────────────────────────────────
  const [documents, setDocuments] = useState<OriginalDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [activeCategory, setActiveCategory] = useState<CategoryId>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[] | null>(null);
  const [searching, setSearching] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [pendingCategory, setPendingCategory] = useState("other");

  const fileInputRef = useRef<HTMLInputElement>(null);
  const searchTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Load documents on mount ──────────────────────────────
  const loadDocuments = useCallback(async () => {
    try {
      const docs = await api.listDocuments();
      setDocuments(docs || []);
    } catch {
      toast.error("Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
    return () => {
      if (searchTimerRef.current) clearTimeout(searchTimerRef.current);
    };
  }, [loadDocuments]);

  // ── Filtered documents ───────────────────────────────────
  const filteredDocs = activeCategory === "all"
    ? documents
    : documents.filter((d) => d.category === activeCategory);

  // ── Upload handlers ──────────────────────────────────────
  const handleFilesSelected = async (files: FileList | File[]) => {
    const fileArray = Array.from(files);
    if (fileArray.length === 0) return;

    // Validate types
    const invalid = fileArray.filter((f) => {
      const ext = `.${f.name.split(".").pop()?.toLowerCase()}`;
      return !ACCEPTED_TYPES.includes(ext);
    });
    if (invalid.length > 0) {
      toast.error(`Unsupported type: ${invalid[0].name}. Allowed: ${ACCEPTED_TYPES.join(", ")}`);
    }

    const valid = fileArray.filter((f) => {
      const ext = `.${f.name.split(".").pop()?.toLowerCase()}`;
      return ACCEPTED_TYPES.includes(ext);
    });
    if (valid.length === 0) return;

    setUploading(true);
    try {
      const result = await api.uploadMultiple(valid, pendingCategory === "other" ? undefined : pendingCategory);
      toast.success(`Uploaded ${result.uploaded} document(s)`);
      if (result.errors > 0) {
        toast.error(`${result.errors} document(s) failed`);
      }
      loadDocuments();
    } catch {
      toast.error("Upload failed");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // ── Drag & drop handlers ─────────────────────────────────
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files) handleFilesSelected(e.dataTransfer.files);
  };

  // ── Search handlers ──────────────────────────────────────
  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (searchTimerRef.current) clearTimeout(searchTimerRef.current);

    if (!query.trim()) {
      setSearchResults(null);
      setSearching(false);
      return;
    }

    setSearching(true);
    searchTimerRef.current = setTimeout(async () => {
      try {
        const result = await api.searchDocuments(query, 10);
        setSearchResults(result.results || []);
      } catch {
        setSearchResults([]);
      } finally {
        setSearching(false);
      }
    }, 400);
  };

  // ── Delete handler ───────────────────────────────────────
  const handleDelete = async (doc: OriginalDocument) => {
    if (!confirm(`Delete "${doc.original_name}"? This cannot be undone.`)) return;
    try {
      await api.deleteDocument(doc.id);
      toast.success("Document deleted");
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id));
    } catch {
      toast.error("Failed to delete document");
    }
  };

  // ── Render: Upload Zone ──────────────────────────────────
  const renderUploadZone = () => (
    <div
      onDragEnter={handleDragEnter}
      onDragOver={(e) => e.preventDefault()}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`card border-2 border-dashed transition-all cursor-pointer text-center p-8 ${
        dragActive
          ? "border-brand-500 bg-brand-50 dark:bg-brand-950/30"
          : "border-border hover:border-border-strong hover:bg-surface-1/50"
      }`}
    >
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={ACCEPTED_TYPES.join(",")}
        className="hidden"
        onChange={(e) => e.target.files && handleFilesSelected(e.target.files)}
      />
      <div className="flex flex-col items-center gap-3">
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 dark:bg-brand-950">
          {uploading ? (
            <Loader2 className="h-6 w-6 animate-spin text-brand-600" />
          ) : (
            <Upload className="h-6 w-6 text-brand-600" />
          )}
        </div>
        <div>
          <p className="text-sm font-medium text-text-primary">
            {uploading ? "Uploading..." : "Drop documents here or click to upload"}
          </p>
          <p className="text-2xs text-text-tertiary mt-1">
            PDF, DOCX, TXT, PNG, JPG — max 50MB each
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-2xs text-text-tertiary">Category:</label>
          <select
            value={pendingCategory}
            onChange={(e) => setPendingCategory(e.target.value)}
            onClick={(e) => e.stopPropagation()}
            className="input text-xs py-1 px-2 w-auto"
          >
            <option value="other">Other</option>
            <option value="resume">Resume</option>
            <option value="certificate">Certificate</option>
            <option value="reference">Reference</option>
          </select>
        </div>
      </div>
    </div>
  );

  // ── Render: Document Card ────────────────────────────────
  const renderDocumentCard = (doc: OriginalDocument) => (
    <div key={doc.id} className="card group relative overflow-hidden">
      <div className="flex items-start justify-between">
        {getFileIcon(doc.original_name)}
        <button
          onClick={() => handleDelete(doc)}
          className="opacity-0 group-hover:opacity-100 p-1 rounded text-text-tertiary hover:text-red-500 hover:bg-red-50 transition-all"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      </div>
      <div className="mt-3">
        <p className="text-sm font-medium text-text-primary truncate" title={doc.original_name}>
          {doc.original_name}
        </p>
        <div className="flex items-center gap-2 mt-1.5">
          {categoryBadge(doc.category)}
          {doc.ocr_performed && (
            <span className="badge badge-info text-2xs">OCR</span>
          )}
        </div>
      </div>
      <div className="mt-2 flex items-center justify-between text-2xs text-text-tertiary">
        <span>{formatFileSize(doc.file_size)}</span>
        <span>{formatDate(doc.created_at)}</span>
      </div>
    </div>
  );

  // ── Render: Search Results Panel ─────────────────────────
  const renderSearchResults = () => {
    if (searching) {
      return (
        <div className="card p-4 text-center">
          <Loader2 className="h-5 w-5 animate-spin text-brand-600 mx-auto" />
          <p className="text-xs text-text-tertiary mt-2">Searching documents...</p>
        </div>
      );
    }
    if (!searchResults) return null;
    if (searchResults.length === 0) {
      return (
        <div className="card p-4 text-center">
          <p className="text-sm text-text-tertiary">No matching documents found</p>
        </div>
      );
    }
    return (
      <div className="card space-y-2">
        <h3 className="section-title flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-brand-600" />
          Semantic Search Results ({searchResults.length})
        </h3>
        {searchResults.map((r, i) => (
          <div key={i} className="p-3 rounded-lg border border-border">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-text-primary">{r.document?.name}</p>
              <span className="text-2xs text-brand-600 font-medium">
                {Math.round((r.similarity || 0) * 100)}% match
              </span>
            </div>
            {categoryBadge(r.document?.category)}
            {r.text_preview && (
              <p className="text-2xs text-text-tertiary mt-1 line-clamp-2">{r.text_preview}</p>
            )}
          </div>
        ))}
      </div>
    );
  };

  // ── Main Render ──────────────────────────────────────────

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-text-primary">Document Vault</h1>
        <p className="mt-1 text-sm text-text-secondary">
          Store source documents — resumes, certificates, references — and search them semantically
        </p>
      </div>

      {/* Upload Zone */}
      {renderUploadZone()}

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-tertiary" />
        <input
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search documents semantically (e.g. 'cloud architecture experience')..."
          className="input pl-10"
        />
        {searchQuery && (
          <button
            onClick={() => { setSearchQuery(""); setSearchResults(null); }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-tertiary hover:text-text-primary"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {renderSearchResults()}

      {/* Category Filters */}
      <div className="flex gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors flex items-center gap-1.5 ${
              activeCategory === cat.id
                ? "bg-brand-600 text-white"
                : "bg-surface-2 text-text-secondary hover:bg-surface-3"
            }`}
          >
            <cat.icon className="h-3.5 w-3.5" />
            {cat.label}
            {cat.id !== "all" && (
              <span className="text-2xs opacity-70">
                {documents.filter((d) => d.category === cat.id).length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Document Grid */}
      {loading ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-36 shimmer rounded-xl" />
          ))}
        </div>
      ) : filteredDocs.length === 0 ? (
        <EmptyState
          icon={<FolderOpen className="h-8 w-8" />}
          title={activeCategory === "all" ? "No documents yet" : "No documents in this category"}
          description={
            activeCategory === "all"
              ? "Upload resumes, certificates, or references to build your document library"
              : "Upload a document and assign this category"
          }
          action={
            <Button onClick={() => fileInputRef.current?.click()} icon={<Upload className="h-4 w-4" />}>
              Upload Documents
            </Button>
          }
        />
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {filteredDocs.map(renderDocumentCard)}
        </div>
      )}
    </div>
  );
}
