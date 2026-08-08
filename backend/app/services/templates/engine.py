"""Template Engine — renders canonical resume JSON into Typst, text, and Markdown.

Templates are stored in the templates/ directory and can be hot-swapped.
Each template has: template.typ, metadata.yaml, theme.json, readme.md
"""

from __future__ import annotations

import json
import structlog
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = structlog.get_logger("careerforge.templates")

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / "templates"


@dataclass
class TemplateInfo:
    """Metadata about a template."""
    name: str = ""
    display_name: str = ""
    description: str = ""
    author: str = ""
    version: str = "1.0"
    page_size: str = "letter"
    font_family: str = "Inter"
    font_size: int = 10
    supports_color: bool = True
    has_theme: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "author": self.author,
            "version": self.version,
            "page_size": self.page_size,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "supports_color": self.supports_color,
            "has_theme": self.has_theme,
        }


@dataclass
class CompileResult:
    """Result from Typst compilation."""
    success: bool
    typst_source: str = ""
    pdf_path: str = ""
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    page_count: int = 0

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "pdf_path": self.pdf_path,
            "errors": self.errors,
            "warnings": self.warnings,
            "page_count": self.page_count,
        }


class TemplateEngine:
    """Manages resume templates and renders them."""

    @staticmethod
    def list_templates() -> list[TemplateInfo]:
        """List all available templates."""
        if not TEMPLATES_DIR.exists():
            return []

        templates = []
        for template_dir in sorted(TEMPLATES_DIR.iterdir()):
            if not template_dir.is_dir():
                continue
            metadata_file = template_dir / "metadata.yaml"
            if not metadata_file.exists():
                continue

            temp_info = TemplateInfo(name=template_dir.name)
            temp_info.has_theme = (template_dir / "theme.json").exists()

            try:
                import yaml
                meta = yaml.safe_load(metadata_file.read_text(encoding="utf-8"))
                if meta:
                    temp_info = TemplateInfo(
                        name=template_dir.name,
                        display_name=meta.get("display_name", template_dir.name),
                        description=meta.get("description", ""),
                        author=meta.get("author", ""),
                        version=meta.get("version", "1.0"),
                        page_size=meta.get("page_size", "letter"),
                        font_family=meta.get("font_family", "Inter"),
                        font_size=meta.get("font_size", 10),
                        supports_color=meta.get("supports_color", True),
                        has_theme=(template_dir / "theme.json").exists(),
                    )
            except Exception:
                pass

            templates.append(temp_info)

        return templates

    @staticmethod
    def get_template(name: str) -> TemplateInfo | None:
        """Get a specific template by name."""
        for t in TemplateEngine.list_templates():
            if t.name == name:
                return t
        return None

    @staticmethod
    def get_template_path(name: str) -> Path:
        """Get the path to a template directory."""
        return TEMPLATES_DIR / name

    @staticmethod
    def get_theme(name: str) -> dict[str, Any]:
        """Get the theme configuration for a template."""
        theme_file = TEMPLATES_DIR / name / "theme.json"
        if not theme_file.exists():
            return {}
        try:
            return json.loads(theme_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @staticmethod
    def get_typst_source(name: str) -> str:
        """Get the Typst source for a template."""
        typst_file = TEMPLATES_DIR / name / "template.typ"
        if not typst_file.exists():
            return TemplateEngine._default_typst()
        return typst_file.read_text(encoding="utf-8")

    @staticmethod
    def render_to_typst(resume: dict[str, Any], template: str = "modern") -> str:
        """Render a canonical resume to Typst format using a template."""
        typst_source = TemplateEngine.get_typst_source(template)
        theme = TemplateEngine.get_theme(template)

        sections = resume.get("sections", [])
        candidate = {
            "name": resume.get("candidate_name", ""),
            "email": resume.get("email", ""),
            "phone": resume.get("phone", ""),
            "location": resume.get("location", ""),
            "linkedin": resume.get("linkedin_url", ""),
            "github": resume.get("github_url", ""),
            "portfolio": resume.get("portfolio_url", ""),
        }

        # Build the resume body in Typst
        body_parts = []

        # Header
        body_parts.append(f"""
// ── Header ─────────────────────────────────────────────
#header(
  {_esc(candidate["name"])},
  {_esc(candidate["email"])},
  {_esc(candidate["phone"])},
  {_esc(candidate["location"])},
  {_esc(candidate["linkedin"])},
  {_esc(candidate["github"])},
  {_esc(candidate["portfolio"])},
)
""")

        # Sections
        sorted_sections = sorted(sections, key=lambda s: s.get("order", 0))
        for section in sorted_sections:
            name = section.get("name", "")
            items = section.get("items", [])
            if not items:
                continue

            name_lower = name.lower()

            if name_lower == "skills":
                texts = [item.get("text", "") for item in items if item.get("text", "").strip()]
                if texts:
                    typst_items = ", ".join(f'{_esc(t)}' for t in texts)
                    body_parts.append(f"""
// ── Skills ──────────────────────────────────────────────
#skills-section(({typst_items},))
""")
            elif name_lower == "languages":
                texts = [item.get("text", "") for item in items if item.get("text", "").strip()]
                if texts:
                    typst_items = ", ".join(f'{_esc(t)}' for t in texts)
                    body_parts.append(f"""
// ── Languages ───────────────────────────────────────────
#languages-section(({typst_items},))
""")
            elif name_lower == "links":
                texts = [item.get("text", "") for item in items if item.get("text", "").strip()]
                if texts:
                    typst_items = ", ".join(f'{_esc(t)}' for t in texts)
                    body_parts.append(f"""
// ── Links ───────────────────────────────────────────────
#links-section(({typst_items},))
""")
            elif name_lower == "publications":
                texts = [item.get("text", "") for item in items if item.get("text", "").strip()]
                if texts:
                    typst_items = ", ".join(f'{_esc(t)}' for t in texts)
                    body_parts.append(f"""
// ── Publications ────────────────────────────────────────
#publications-section(({typst_items},))
""")
            elif name_lower == "awards":
                texts = [item.get("text", "") for item in items if item.get("text", "").strip()]
                if texts:
                    typst_items = ", ".join(f'{_esc(t)}' for t in texts)
                    body_parts.append(f"""
// ── Awards ──────────────────────────────────────────────
#awards-section(({typst_items},))
""")
            elif name_lower in ("experience", "projects", "education", "certificates", "achievements"):
                texts = [item.get("text", "") for item in items if item.get("text", "").strip()]
                if texts:
                    typst_items = ", ".join(f'{_esc(t)}' for t in texts)
                    body_parts.append(f"""
// ── {name} ──────────────────────────────────────────────
#detail-section({_esc(name)}, ({typst_items},))
""")
            else:
                texts = [item.get("text", "") for item in items if item.get("text", "").strip()]
                if texts:
                    typst_items = ", ".join(f'{_esc(t)}' for t in texts)
                    body_parts.append(f"""
// ── {name} ──────────────────────────────────────────────
#generic-section({_esc(name)}, ({typst_items},))
""")

        # Assemble: template source + body
        body = "\n".join(body_parts)

        result = f"""// ═══════════════════════════════════════════════════════
// CareerForge AI — Generated Resume
// Template: {template}
// Generated: {__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}
// ═══════════════════════════════════════════════════════

{typst_source}

// ═══════════════════════════════════════════════════════
// Resume Content
// ═══════════════════════════════════════════════════════

{body}
"""
        return result

    @staticmethod
    def render_to_text(resume: dict[str, Any]) -> str:
        """Render a canonical resume to plain text."""
        sections = resume.get("sections", [])
        candidate_name = resume.get("candidate_name", "")
        email = resume.get("email", "")
        phone = resume.get("phone", "")
        location = resume.get("location", "")
        linkedin = resume.get("linkedin_url", "")
        github = resume.get("github_url", "")

        lines = [
            candidate_name.upper(),
            f"{email} | {phone} | {location}",
        ]
        if linkedin:
            lines.append(f"LinkedIn: {linkedin}")
        if github:
            lines.append(f"GitHub: {github}")
        lines.append("=" * 60)
        lines.append("")

        for section in sections:
            name = section.get("name", "")
            items = section.get("items", [])
            if not items:
                continue
            lines.append(name.upper())
            lines.append("-" * 40)
            for item in items:
                bullet = item.get("text", "").strip()
                if bullet:
                    lines.append(f"  * {bullet}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def render_to_markdown(resume: dict[str, Any]) -> str:
        """Render a canonical resume to Markdown."""
        sections = resume.get("sections", [])
        candidate_name = resume.get("candidate_name", "")
        email = resume.get("email", "")
        phone = resume.get("phone", "")
        location = resume.get("location", "")
        linkedin = resume.get("linkedin_url", "")
        github = resume.get("github_url", "")
        portfolio = resume.get("portfolio_url", "")

        lines = [
            f"# {candidate_name}",
            "",
        ]

        contact = []
        if email:
            contact.append(f"📧 {email}")
        if phone:
            contact.append(f"📱 {phone}")
        if location:
            contact.append(f"📍 {location}")
        if linkedin:
            contact.append(f"[LinkedIn]({linkedin})")
        if github:
            contact.append(f"[GitHub]({github})")
        if portfolio:
            contact.append(f"[Portfolio]({portfolio})")
        if contact:
            lines.append(" | ".join(contact))
            lines.append("")

        for section in sections:
            name = section.get("name", "")
            items = section.get("items", [])
            if not items:
                continue
            lines.append(f"## {name}")
            lines.append("")
            for item in items:
                bullet = item.get("text", "").strip()
                if bullet:
                    lines.append(f"- {bullet}")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def compile_typst(typst_source: str, output_dir: str | None = None) -> CompileResult:
        """Compile Typst source to PDF. Returns the compilation result.
        
        Uses the Python typst library if available, falling back to
        the system-installed typst binary.
        """
        import subprocess
        import shutil

        # Try Python typst library first (bundled, no system dependency).
        # If it's not installed OR compilation fails at runtime (e.g. on
        # Windows the native extension can't enumerate fonts), fall back to
        # the system-installed typst binary.
        try:
            import typst
            result = TemplateEngine._compile_with_library(typst_source, output_dir)
            if result.success:
                return result
            logger.warning("typst.library_failed", error=result.errors[0].get("message") if result.errors else "unknown")
        except ImportError:
            logger.debug("typst.library_not_installed")
        except Exception as exc:
            logger.warning("typst.library_error", error=str(exc))

        # Fall back to system binary
        typst_cmd = shutil.which("typst")
        if not typst_cmd:
            return CompileResult(
                success=False,
                typst_source=typst_source,
                errors=[{"message": "Typst compiler not installed. Install the 'typst' pip package or install Typst from https://typst.app"}],
            )

        return TemplateEngine._compile_with_binary(typst_source, output_dir, typst_cmd)

    @staticmethod
    def validate_typst(typst_source: str) -> list[dict[str, Any]]:
        """Validate Typst source for syntax errors without full compilation."""
        errors = []
        lines = typst_source.split("\n")
        depth = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check bracket matching
            for ch in stripped:
                if ch == "[":
                    depth += 1
                elif ch == "]":
                    depth -= 1
                    if depth < 0:
                        errors.append({"line": i, "message": "Unexpected closing bracket ']'"})

            # Check for common issues
            if "#if" in stripped and ":" not in stripped:
                errors.append({"line": i, "message": "Missing ':' after #if condition"})

        if depth > 0:
            errors.append({"line": len(lines), "message": f"Unclosed bracket(s): {depth} unmatched '['"})

        return errors

    @staticmethod
    def _default_typst() -> str:
        """Return a default Typst template."""
        return """// CareerForge AI — Default Resume Template
#set page(paper: "us-letter", margin: (x: 0.7in, y: 0.5in))
#set text(font: ("Helvetica", "Arial"), size: 10pt)

#align(center)[
  #text(size: 20pt, weight: "bold")[CANDIDATE NAME]
  #v(4pt)
  #text(size: 9pt)[email | phone | location]
]

#line(length: 100%)
#v(8pt)

#text(size: 11pt, weight: "bold")[Section]
#line(length: 100%)
- Bullet point here
"""

    @staticmethod
    def _compile_with_library(typst_source: str, output_dir: str | None = None) -> CompileResult:
        """Compile Typst source using the Python typst library."""
        try:
            import typst
            import io

            # Compile to PDF bytes
            pdf_bytes = typst.compile(typst_source)

            # Save to output directory or temp
            if output_dir:
                out_path = Path(output_dir)
                out_path.mkdir(parents=True, exist_ok=True)
                pdf_path = out_path / "resume.pdf"
                pdf_path.write_bytes(pdf_bytes)
            else:
                with tempfile.TemporaryDirectory(prefix="careerforge_") as tmpdir:
                    pdf_path = Path(tmpdir) / "resume.pdf"
                    pdf_path.write_bytes(pdf_bytes)

            # Estimate page count (typst library doesn't expose page count directly)
            page_count = max(1, len(pdf_bytes) // 5000)  # rough estimate

            return CompileResult(
                success=True,
                typst_source=typst_source,
                pdf_path=str(pdf_path) if output_dir else str(pdf_path),
                page_count=page_count,
            )
        except Exception as e:
            return CompileResult(
                success=False,
                typst_source=typst_source,
                errors=[{"message": f"Typst library compilation error: {e}"}],
            )

    @staticmethod
    def _compile_with_binary(typst_source: str, output_dir: str | None, typst_cmd: str) -> CompileResult:
        """Compile Typst source using the system-installed typst binary."""
        import shutil
        import subprocess

        with tempfile.TemporaryDirectory(prefix="careerforge_") as tmpdir:
            tmpdir_path = Path(tmpdir)
            typst_file = tmpdir_path / "resume.typ"
            pdf_file = tmpdir_path / "resume.pdf"

            # Write Typst source
            typst_file.write_text(typst_source, encoding="utf-8")

            # Compile
            try:
                result = subprocess.run(
                    [typst_cmd, "compile", str(typst_file), str(pdf_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    errors = []
                    for line in result.stderr.strip().split("\n"):
                        if line.strip():
                            errors.append({"message": line.strip()})
                    return CompileResult(
                        success=False,
                        typst_source=typst_source,
                        errors=errors,
                    )

                # Copy PDF to output directory
                if output_dir:
                    out_path = Path(output_dir)
                    out_path.mkdir(parents=True, exist_ok=True)
                    dest = out_path / "resume.pdf"
                    shutil.copy2(str(pdf_file), str(dest))
                    pdf_path = str(dest)
                else:
                    pdf_path = str(pdf_file)

                # Count pages
                page_count = 1
                try:
                    import subprocess as sp
                    info = sp.run(
                        [typst_cmd, "query", str(typst_file), "page.number", "--field", "value"],
                        capture_output=True, text=True, timeout=10,
                    )
                    if info.returncode == 0 and info.stdout.strip():
                        page_count = len(info.stdout.strip().split("\n"))
                except Exception:
                    pass

                return CompileResult(
                    success=True,
                    typst_source=typst_source,
                    pdf_path=pdf_path,
                    page_count=max(page_count, 1),
                )

            except subprocess.TimeoutExpired:
                return CompileResult(
                    success=False,
                    typst_source=typst_source,
                    errors=[{"message": "Typst compilation timed out (30s limit)"}],
                )
            except Exception as e:
                return CompileResult(
                    success=False,
                    typst_source=typst_source,
                    errors=[{"message": f"Compilation error: {e}"}],
                )


def _esc(text: str) -> str:
    """Escape text as a Typst string literal, wrapped in double quotes.

    Inside Typst string literals ("...") only backslash and double-quote
    need escaping — markup characters like #, $, %, &, [, ], {, } are
    literal. The result is always quoted so it can be used directly as
    a function argument (e.g. #header("John Smith", ...)).
    """
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    return f'"{text}"'
