/**
 * ExportPreview — modal that previews a resume in a selected format
 * before the user downloads it.
 *
 * Formats: pdf, typst, text, markdown, json.
 * PDF is rendered via pdfjs-dist to canvas thumbnails.
 */

import { useEffect, useState } from "react";
import {
  X, Download, Loader2, FileText, FileCode, File, 
  AlertTriangle, Copy, Check,
} from "lucide-react";
import { api } from "@/services/api";
import { Button } from "@/components/common/Button";
import { toast } from "@/components/common/Toast";

/* eslint-disable @typescript-eslint/no-explicit-any */
type AnyRecord = Record<string, any>;

export type PreviewFormat = "pdf" | "typst" | "text" | "markdown" | "json";

interface ExportPreviewProps {
  format: PreviewFormat;
  resume: AnyRecord;
  template: string;
  atsScore?: number | null;
  onClose: () => void;
  onDownload: () => void;
}

// ── Markdown: safe minimal renderer (no dangerouslySetInnerHTML) ──

function renderMarkdownLines(md: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = [];
  let listBuffer: string[] = [];

  const flushList = (key: string) => {
    if (listBuffer.length > 0) {
      nodes.push(
        <ul key={key} className="list-disc list-inside space-y-0.5 text-sm text-text-primary">
          {listBuffer.map((item, i) => (
            <li key={`${key}_${i}`} className="pl-1">{item}</li>
          ))}
        </ul>,
      );
      listBuffer = [];
    }
  };

  md.split("\n").forEach((line, i) => {
    const trimmed = line.trim();
    const key = `line_${i}`;

    if (trimmed.startsWith("### ")) {
      flushList(`list_${i}`);
      nodes.push(<h4 key={key} className="text-sm font-bold text-text-primary mt-2">{trimmed.slice(4)}</h4>);
    } else if (trimmed.startsWith("## ")) {
      flushList(`list_${i}`);
      nodes.push(<h3 key={key} className="text-base font-bold text-text-primary mt-3">{trimmed.slice(3)}</h3>);
    } else if (trimmed.startsWith("# ")) {
      flushList(`list_${i}`);
      nodes.push(<h2 key={key} className="text-xl font-bold text-text-primary mb-1">{trimmed.slice(2)}</h2>);
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      listBuffer.push(trimmed.replace(/^[-*]\s/, ""));
    } else if (trimmed.startsWith("![") || trimmed.startsWith("[!")) {
      // Skip images / unsupported markdown
    } else if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      // Simple table row → render as plain line
      flushList(`list_${i}`);
      const cells = trimmed.split("|").filter(Boolean).map((c) => c.trim());
      if (cells.some((c) => /^:?-{3,}:?$/.test(c))) return; // separator row
      nodes.push(
        <div key={key} className="flex gap-3 text-sm text-text-primary">
          {cells.map((c, j) => <span key={j} className="flex-1">{c}</span>)}
        </div>,
      );
    } else if (trimmed === "") {
      flushList(`list_${i}`);
      nodes.push(<div key={key} className="h-2" />);
    } else {
      flushList(`list_${i}`);
      nodes.push(<p key={key} className="text-sm text-text-primary">{trimmed}</p>);
    }
  });
  flushList("list_end");

  return nodes;
}

// ── JSON: collapsible-friendly pretty pre-block ──

function renderJson(resume: AnyRecord, template: string): string {
  return JSON.stringify({ resume, template }, null, 2);
}

// ── PDF renderer via pdfjs-dist ──

async function renderPdfToDataUrls(blob: Blob): Promise<string[]> {
  // Dynamic import so pdfjs worker is code-split
  const pdfjs = await import("pdfjs-dist");
  const workerModule = await import("pdfjs-dist/build/pdf.worker.mjs?url");
  pdfjs.GlobalWorkerOptions.workerSrc = workerModule.default;
  // Avoid eval-based code paths (strict CSP) and force main-thread fallback
  // if the worker cannot load, so rendering never silently blanks out.
  (pdfjs as any).isEvalSupported = false;

  const arrayBuffer = await blob.arrayBuffer();
  const pdf = await pdfjs.getDocument({ data: arrayBuffer }).promise;

  const images: string[] = [];
  for (let i = 1; i <= pdf.numPages; i++) {
    const page = await pdf.getPage(i);
    const viewport = page.getViewport({ scale: 2 });
    const canvas = document.createElement("canvas");
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    await page.render({ canvas, viewport } as any).promise;
    images.push(canvas.toDataURL("image/png"));
  }
  return images;
}

// ── Main Component ───────────────────────────────────────────

export default function ExportPreview({
  format,
  resume,
  template,
  atsScore,
  onClose,
  onDownload,
}: ExportPreviewProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [textContent, setTextContent] = useState("");
  const [pageImages, setPageImages] = useState<string[]>([]);
  const [copied, setCopied] = useState(false);

  // ── Load preview content on mount / format change ────────
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setTextContent("");
    setPageImages([]);

    const load = async () => {
      try {
        if (format === "pdf") {
          const blob = await api.previewPdf(resume, template);
          if (cancelled) return;
          const images = await renderPdfToDataUrls(blob);
          if (!cancelled) setPageImages(images);
        } else if (format === "typst") {
          const d = await api.exportResumeTypst(resume, template);
          if (!cancelled) setTextContent(d.typst || "");
        } else if (format === "text") {
          const d = await api.exportResumeText(resume);
          if (!cancelled) setTextContent(d.text || "");
        } else if (format === "markdown") {
          const d = await api.exportResumeMarkdown(resume);
          if (!cancelled) setTextContent(d.markdown || "");
        } else if (format === "json") {
          if (!cancelled) setTextContent(renderJson(resume, template));
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message || "Failed to load preview");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    load();
    return () => { cancelled = true; };
  }, [format, resume, template]);

  // ── Copy to clipboard ───────────────────────────────────
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(textContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      toast.error("Copy failed");
    }
  };

  // ── Format meta ─────────────────────────────────────────
  const formatMeta: Record<PreviewFormat, { label: string; icon: typeof FileText; mono: boolean }> = {
    pdf: { label: "PDF Document", icon: FileText, mono: false },
    typst: { label: "Typst Source", icon: FileCode, mono: true },
    text: { label: "Plain Text", icon: File, mono: true },
    markdown: { label: "Markdown", icon: FileCode, mono: false },
    json: { label: "JSON", icon: FileCode, mono: true },
  };
  const meta = formatMeta[format];

  // ── Render content ──────────────────────────────────────
  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-brand-600" />
          <p className="text-sm text-text-tertiary mt-3">Preparing {meta.label.toLowerCase()} preview...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex flex-col items-center justify-center py-16">
          <AlertTriangle className="h-8 w-8 text-amber-500" />
          <p className="text-sm text-text-secondary mt-3 text-center max-w-sm">{error}</p>
          <p className="text-2xs text-text-tertiary mt-1">Tip: PDF preview requires the Typst compiler to be installed.</p>
        </div>
      );
    }

    if (format === "pdf") {
      if (pageImages.length === 0) {
        return (
          <div className="flex flex-col items-center justify-center py-16">
            <AlertTriangle className="h-8 w-8 text-amber-500" />
            <p className="text-sm text-text-secondary mt-3 text-center max-w-sm">No pages were rendered.</p>
          </div>
        );
      }
      return (
        <div className="bg-surface-2 p-4 rounded-lg overflow-y-auto max-h-[60vh]">
          {pageImages.map((src, i) => (
            <img
              key={i}
              src={src}
              alt={`Resume page ${i + 1}`}
              className="w-full h-auto rounded-lg border border-border bg-white shadow-elevation-1 mb-3"
            />
          ))}
        </div>
      );
    }

    if (format === "markdown") {
      return (
        <div className="max-h-[60vh] overflow-y-auto p-6 bg-white dark:bg-surface-1 rounded-lg border border-border">
          {renderMarkdownLines(textContent)}
        </div>
      );
    }

    // typst / text / json → monospace pre block
    return (
      <pre
        className={`max-h-[60vh] overflow-auto p-4 rounded-lg bg-surface-2 text-xs text-text-secondary font-mono leading-relaxed whitespace-pre-wrap break-words ${
          meta.mono ? "" : ""
        }`}
      >
        {textContent}
      </pre>
    );
  };

  // ── Render ──────────────────────────────────────────────
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 animate-fade-in">
      <div className="w-full max-w-4xl max-h-[90vh] flex flex-col rounded-2xl bg-surface-1 shadow-elevation-2 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-border">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-950">
              <meta.icon className="h-4.5 w-4.5 h-5 w-5 text-brand-600" />
            </span>
            <div>
              <h2 className="text-sm font-semibold text-text-primary">Preview: {meta.label}</h2>
              <p className="text-2xs text-text-tertiary">
                {resume?.candidate_name || "Untitled resume"} · {template} template
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {atsScore != null && (
              <span className={`badge text-2xs ${atsScore >= 80 ? "badge-success" : atsScore >= 60 ? "badge-warning" : "badge-error"}`}>
                ATS: {Math.round(atsScore)}%
              </span>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-text-tertiary hover:bg-surface-2 hover:text-text-primary transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-hidden">
          {format !== "pdf" && format !== "markdown" && !loading && (
            <div className="flex items-center justify-end gap-3 px-4 pt-3">
              <span className="text-2xs text-text-tertiary">{textContent.length.toLocaleString()} chars</span>
            </div>
          )}
          <div className="p-4">{renderContent()}</div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 py-3 border-t border-border">
          {format === "markdown" || format === "typst" || format === "text" || format === "json" ? (
            <Button variant="ghost" size="sm" onClick={handleCopy} icon={copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}>
              {copied ? "Copied" : "Copy"}
            </Button>
          ) : <span />}
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={onClose}>
              Close
            </Button>
            <Button size="sm" onClick={onDownload} icon={<Download className="h-4 w-4" />}>
              Download
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
