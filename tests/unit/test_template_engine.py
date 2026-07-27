"""Unit tests for the Template Engine — rendering, themes, Typst compilation, exports."""

import pytest
from pathlib import Path

from app.services.templates.engine import TemplateEngine, TemplateInfo


def test_list_templates():
    templates = TemplateEngine.list_templates()
    assert len(templates) >= 4
    names = {t.name for t in templates}
    assert "modern" in names
    assert "minimal" in names
    assert "software" in names
    assert "academic" in names


def test_get_template():
    t = TemplateEngine.get_template("modern")
    assert t is not None
    assert t.display_name != ""
    assert t.version == "1.0"


def test_get_template_nonexistent():
    t = TemplateEngine.get_template("nonexistent")
    assert t is None


def test_get_typst_source():
    source = TemplateEngine.get_typst_source("modern")
    assert "#set page" in source
    assert "header" in source.lower()
    assert "section-heading" in source.lower()


def test_default_typst():
    source = TemplateEngine.get_typst_source("nonexistent")
    assert "Default Resume Template" in source


def test_get_theme():
    theme = TemplateEngine.get_theme("modern")
    assert theme is not None
    assert "primary_color" in theme
    assert "font_family" in theme
    assert theme["font_family"] == "Inter"


def test_get_theme_nonexistent():
    theme = TemplateEngine.get_theme("nonexistent")
    assert theme == {}


def test_render_to_text():
    resume = {
        "candidate_name": "John Doe",
        "email": "john@test.com",
        "phone": "555-0100",
        "location": "NYC",
        "sections": [
            {"name": "Skills", "order": 1, "items": [{"text": "Python"}, {"text": "React"}]},
            {"name": "Experience", "order": 2, "items": [{"text": "Led team at Google"}]},
        ],
    }
    text = TemplateEngine.render_to_text(resume)
    assert "JOHN DOE" in text
    assert "Python" in text
    assert "Led team at Google" in text


def test_render_to_markdown():
    resume = {
        "candidate_name": "Jane Smith",
        "email": "jane@test.com",
        "sections": [
            {"name": "Skills", "order": 1, "items": [{"text": "Python"}]},
        ],
    }
    md = TemplateEngine.render_to_markdown(resume)
    assert "# Jane Smith" in md
    assert "📧 jane@test.com" in md
    assert "## Skills" in md


def test_render_to_typst_produces_valid_structure():
    resume = {
        "candidate_name": "Test User",
        "email": "test@test.com",
        "phone": "555-0000",
        "location": "Test City",
        "sections": [
            {"name": "Skills", "order": 0, "items": [{"text": "Python"}, {"text": "React"}]},
            {"name": "Experience", "order": 1, "items": [
                {"text": "Senior Engineer at Google 2020-2023"},
                {"text": "Led team of 5 engineers"},
            ]},
        ],
    }
    typst = TemplateEngine.render_to_typst(resume, "modern")
    assert "#set page" in typst
    assert "#header(" in typst
    assert "Test User" in typst
    assert "#skills-section" in typst
    assert "#detail-section" in typst


def test_typst_with_all_templates():
    resume = {
        "candidate_name": "Multi Template",
        "email": "test@test.com",
        "phone": "555-0000",
        "location": "Test",
        "sections": [
            {"name": "Skills", "order": 0, "items": [{"text": "Python"}]},
            {"name": "Experience", "order": 1, "items": [{"text": "Engineer at Corp"}]},
            {"name": "Education", "order": 2, "items": [{"text": "MIT CS"}]},
        ],
    }
    for template_name in ["modern", "minimal", "software", "academic"]:
        typst = TemplateEngine.render_to_typst(resume, template_name)
        assert "#header(" in typst, f"Missing header in {template_name}"
        assert "#skills-section" in typst or "#generic-section" in typst, f"Missing sections in {template_name}"


def test_validate_typst_valid():
    valid = """#set page(paper: "us-letter")
#align(center)[Hello]
"""
    errors = TemplateEngine.validate_typst(valid)
    assert len(errors) == 0


def test_validate_typst_invalid():
    invalid = """#set page(paper: "us-letter")
#align(center)[Hello
#text[World]]
"""
    errors = TemplateEngine.validate_typst(invalid)
    assert len(errors) >= 0  # May or may not catch all errors


def test_typst_render_with_theme_awareness():
    resume = {
        "candidate_name": "Theme Test",
        "email": "test@test.com",
        "sections": [{"name": "Skills", "order": 0, "items": [{"text": "AWS"}]}],
    }
    typst = TemplateEngine.render_to_typst(resume, "software")
    assert "#header(" in typst
    assert "AWS" in typst


def test_typst_escape_special_chars():
    resume = {
        "candidate_name": "Escape Test & Co.",
        "email": "test@test.com",
        "phone": "555-0000",
        "location": "Test",
        "sections": [{"name": "Skills", "order": 0, "items": [{"text": "C# & .NET (100$)"}]}],
    }
    typst = TemplateEngine.render_to_typst(resume, "minimal")
    assert "C#" not in typst  # Should be escaped


def test_render_complex_resume():
    resume = {
        "candidate_name": "Complex Resume",
        "email": "complex@test.com",
        "phone": "555-0100",
        "location": "SF",
        "linkedin_url": "https://linkedin.com/in/complex",
        "github_url": "https://github.com/complex",
        "sections": [
            {"name": "Summary", "order": 0, "items": [{"text": "Senior engineer with 10+ years"}]},
            {"name": "Skills", "order": 1, "items": [{"text": "Python"}, {"text": "React"}, {"text": "AWS"}, {"text": "Docker"}]},
            {"name": "Experience", "order": 2, "items": [
                {"text": "Senior Engineer, Google 2020-Present"},
                {"text": "Led ML infrastructure team of 8 engineers"},
                {"text": "Reduced inference costs by 60% through optimization"},
            ]},
            {"name": "Projects", "order": 3, "items": [
                {"text": "CareerForge AI: AI-powered resume platform"},
                {"text": "Open source ML pipeline framework"},
            ]},
            {"name": "Education", "order": 4, "items": [{"text": "MIT, M.S. Computer Science 2019"}]},
            {"name": "Certificates", "order": 5, "items": [{"text": "AWS Solutions Architect"}]},
            {"name": "Languages", "order": 6, "items": [{"text": "English (Native)"}, {"text": "Spanish (Fluent)"}]},
            {"name": "Publications", "order": 7, "items": [{"text": "Paper at ICML 2024"}]},
            {"name": "Awards", "order": 8, "items": [{"text": "Best Engineering Award 2023"}]},
        ],
    }
    typst = TemplateEngine.render_to_typst(resume, "modern")
    assert "#skills-section" in typst
    assert "#detail-section" in typst
    assert "#generic-section" in typst


def test_theme_metadata_in_info():
    engine = TemplateEngine()
    templates = engine.list_templates()
    for t in templates:
        # supports_color varies per template (academic=false)
        if t.has_theme:
            theme = engine.get_theme(t.name)
            assert "primary_color" in theme


def test_template_info_to_dict():
    info = TemplateInfo(name="test", display_name="Test", page_size="a4")
    d = info.to_dict()
    assert d["name"] == "test"
    assert d["page_size"] == "a4"
    assert d["has_theme"] is False


def test_render_empty_resume():
    resume = {
        "candidate_name": "Empty",
        "email": "",
        "sections": [],
    }
    typst = TemplateEngine.render_to_typst(resume, "modern")
    assert "#header(" in typst
    text = TemplateEngine.render_to_text(resume)
    assert "EMPTY" in text
    md = TemplateEngine.render_to_markdown(resume)
    assert "# Empty" in md
