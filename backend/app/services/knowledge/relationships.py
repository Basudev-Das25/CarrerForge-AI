"""Relationship Discovery — automatically infer connections between entities.

Analyzes entity properties to discover implicit relationships that
aren't captured in the database schema.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.knowledge.graph import KnowledgeGraph, KnowledgeEdge

logger = logging.getLogger("careerforge.knowledge.relationships")


def discover_all_relationships(graph: KnowledgeGraph) -> int:
    """Run all relationship discovery algorithms. Returns count of edges added."""
    count = 0
    count += _discover_project_skill(graph)
    count += _discover_certificate_skill(graph)
    count += _discover_experience_project(graph)
    count += _discover_achievement_experience(graph)
    count += _discover_publication_skill(graph)
    count += _discover_award_achievement(graph)
    count += _discover_jd_skill(graph)
    count += _discover_resume_job(graph)
    count += _discover_ats_resume(graph)
    logger.info("relationships.discovered", total=count)
    return count


def _discover_project_skill(graph: KnowledgeGraph) -> int:
    """Project uses Skill — inferred from tech_stack, skills_used, keywords."""
    count = 0
    for project in graph.get_nodes_by_type("project"):
        skill_names = set()
        for field_name in ("tech_stack", "skills_used", "keywords", "tags"):
            items = project.properties.get(field_name, [])
            if isinstance(items, list):
                skill_names.update(str(item).lower().strip() for item in items)

        for skill in graph.get_nodes_by_type("skill"):
            if skill.properties.get("name", "").lower() in skill_names:
                _add_edge(graph, KnowledgeEdge(
                    source_type="project", source_id=project.entity_id,
                    target_type="skill", target_id=skill.entity_id,
                    relationship="uses", weight=0.9,
                ))
                count += 1
    return count


def _discover_certificate_skill(graph: KnowledgeGraph) -> int:
    """Certificate demonstrates Skill — inferred from skills field."""
    count = 0
    for cert in graph.get_nodes_by_type("certificate"):
        cert_skills = set()
        for s in cert.properties.get("skills", []):
            cert_skills.add(str(s).lower().strip())
        for t in cert.properties.get("tags", []):
            cert_skills.add(str(t).lower().strip())

        for skill in graph.get_nodes_by_type("skill"):
            if skill.properties.get("name", "").lower() in cert_skills:
                _add_edge(graph, KnowledgeEdge(
                    source_type="certificate", source_id=cert.entity_id,
                    target_type="skill", target_id=skill.entity_id,
                    relationship="demonstrates", weight=0.85,
                ))
                count += 1
    return count


def _discover_experience_project(graph: KnowledgeGraph) -> int:
    """Experience involved Project — inferred from shared companies, tech, dates."""
    count = 0
    for exp in graph.get_nodes_by_type("experience"):
        exp_company = str(exp.properties.get("company", "")).lower()
        exp_skills = set(str(s).lower() for s in exp.properties.get("skills_used", []))

        for project in graph.get_nodes_by_type("project"):
            proj_skills = set(str(s).lower() for s in project.properties.get("tech_stack", []))
            proj_skills.update(str(s).lower() for s in project.properties.get("skills_used", []))

            # Check for shared skills or company match
            overlap = exp_skills & proj_skills
            if len(overlap) >= 1:
                weight = min(0.5 + len(overlap) * 0.1, 0.95)
                _add_edge(graph, KnowledgeEdge(
                    source_type="experience", source_id=exp.entity_id,
                    target_type="project", target_id=project.entity_id,
                    relationship="involved_in", weight=weight,
                    metadata={"shared_skills": list(overlap)},
                ))
                count += 1
    return count


def _discover_achievement_experience(graph: KnowledgeGraph) -> int:
    """Achievement resulted from Experience — inferred from shared orgs and dates."""
    count = 0
    for ach in graph.get_nodes_by_type("achievement"):
        ach_org = str(ach.properties.get("organization", "")).lower()
        ach_date = str(ach.properties.get("date", ""))

        for exp in graph.get_nodes_by_type("experience"):
            exp_company = str(exp.properties.get("company", "")).lower()
            if ach_org and ach_org == exp_company:
                _add_edge(graph, KnowledgeEdge(
                    source_type="achievement", source_id=ach.entity_id,
                    target_type="experience", target_id=exp.entity_id,
                    relationship="resulted_from", weight=0.8,
                ))
                count += 1
            elif ach_date and ach_date >= str(exp.properties.get("start_date", "")) and ach_date <= str(exp.properties.get("end_date", "9999")):
                _add_edge(graph, KnowledgeEdge(
                    source_type="achievement", source_id=ach.entity_id,
                    target_type="experience", target_id=exp.entity_id,
                    relationship="coincides_with", weight=0.4,
                ))
                count += 1
    return count


def _discover_publication_skill(graph: KnowledgeGraph) -> int:
    """Publication demonstrates Skill — inferred from keywords and content."""
    count = 0
    for pub in graph.get_nodes_by_type("publication"):
        pub_text = str(pub.properties.get("title", "")).lower() + " " + str(pub.properties.get("description", "")).lower()
        pub_venue = str(pub.properties.get("venue", "")).lower()

        for skill in graph.get_nodes_by_type("skill"):
            skill_name = skill.properties.get("name", "").lower()
            if skill_name and skill_name in pub_text:
                _add_edge(graph, KnowledgeEdge(
                    source_type="publication", source_id=pub.entity_id,
                    target_type="skill", target_id=skill.entity_id,
                    relationship="demonstrates", weight=0.7,
                ))
                count += 1
    return count


def _discover_award_achievement(graph: KnowledgeGraph) -> int:
    """Award recognized Achievement — inferred from shared categories and orgs."""
    count = 0
    for award in graph.get_nodes_by_type("award"):
        award_org = str(award.properties.get("issuer", "")).lower()
        award_cat = str(award.properties.get("category", ""))

        for ach in graph.get_nodes_by_type("achievement"):
            ach_org = str(ach.properties.get("organization", "")).lower()
            ach_cat = str(ach.properties.get("category", ""))
            if award_org and award_org == ach_org:
                _add_edge(graph, KnowledgeEdge(
                    source_type="award", source_id=award.entity_id,
                    target_type="achievement", target_id=ach.entity_id,
                    relationship="recognizes", weight=0.75,
                ))
                count += 1
    return count


def _discover_jd_skill(graph: KnowledgeGraph) -> int:
    """JobDescription requires Skill — inferred from keywords and requirements."""
    count = 0
    for jd in graph.get_nodes_by_type("job_description"):
        jd_text = str(jd.properties.get("raw_text", "")).lower()
        jd_keywords = set(str(k).lower() for k in jd.properties.get("keywords", []))
        jd_requirements = set(str(r).lower() for r in jd.properties.get("requirements", []))

        for skill in graph.get_nodes_by_type("skill"):
            skill_name = skill.properties.get("name", "").lower()
            if skill_name in jd_keywords or skill_name in jd_requirements:
                _add_edge(graph, KnowledgeEdge(
                    source_type="job_description", source_id=jd.entity_id,
                    target_type="skill", target_id=skill.entity_id,
                    relationship="requires", weight=0.9,
                ))
                count += 1
            elif skill_name in jd_text:
                _add_edge(graph, KnowledgeEdge(
                    source_type="job_description", source_id=jd.entity_id,
                    target_type="skill", target_id=skill.entity_id,
                    relationship="mentions", weight=0.5,
                ))
                count += 1
    return count


def _discover_resume_job(graph: KnowledgeGraph) -> int:
    """ResumeVersion targets JobDescription."""
    count = 0
    for rv in graph.get_nodes_by_type("resume_version"):
        jd_id = rv.properties.get("job_description_id")
        if jd_id:
            _add_edge(graph, KnowledgeEdge(
                source_type="resume_version", source_id=rv.entity_id,
                target_type="job_description", target_id=str(jd_id),
                relationship="targets", weight=1.0,
            ))
            count += 1
    return count


def _discover_ats_resume(graph: KnowledgeGraph) -> int:
    """ATSReport evaluates ResumeVersion."""
    count = 0
    for ats in graph.get_nodes_by_type("ats_report"):
        rv_id = ats.properties.get("resume_version_id")
        if rv_id:
            _add_edge(graph, KnowledgeEdge(
                source_type="ats_report", source_id=ats.entity_id,
                target_type="resume_version", target_id=str(rv_id),
                relationship="evaluates", weight=1.0,
            ))
            count += 1
    return count


def _add_edge(graph: KnowledgeGraph, edge: KnowledgeEdge) -> None:
    """Add edge only if it doesn't already exist."""
    if edge.key not in graph._edges:
        graph.add_edge(edge)
