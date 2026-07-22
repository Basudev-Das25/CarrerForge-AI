"""Profile router — complete CRUD for all profile entities.

Every endpoint is scoped to a single user (user_id = "default" for local-first).
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.services.profile import ProfileService
from app.models.schemas import (
    UserCreate, UserUpdate, UserResponse,
    EducationCreate, EducationUpdate, EducationResponse,
    ExperienceCreate, ExperienceUpdate, ExperienceResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    SkillCreate, SkillUpdate, SkillResponse,
    CertificateCreate, CertificateUpdate, CertificateResponse,
    AchievementCreate, AchievementUpdate, AchievementResponse,
    LanguageCreate, LanguageUpdate, LanguageResponse,
    PublicationCreate, PublicationUpdate, PublicationResponse,
    AwardCreate, AwardUpdate, AwardResponse,
    SocialLinkCreate, SocialLinkUpdate, SocialLinkResponse,
    DashboardData,
)

router = APIRouter()

DEFAULT_USER_ID = "default"


def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(session=db, user_id=DEFAULT_USER_ID)


# ══════════════════════════════════════════════════════════════
# USER PROFILE
# ══════════════════════════════════════════════════════════════

@router.get("/profile", response_model=UserResponse)
async def get_profile(service: ProfileService = Depends(get_profile_service)):
    return await service.get_or_create_user()


@router.put("/profile", response_model=UserResponse)
async def update_profile(data: UserUpdate, service: ProfileService = Depends(get_profile_service)):
    return await service.update_profile(data.model_dump(exclude_unset=True))


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(service: ProfileService = Depends(get_profile_service)):
    return await service.get_dashboard_data()


@router.get("/completion")
async def get_completion(service: ProfileService = Depends(get_profile_service)):
    return {"completion": await service.calculate_profile_completion()}


@router.get("/search")
async def global_search(q: str = Query(..., min_length=1), service: ProfileService = Depends(get_profile_service)):
    return {"query": q, "results": await service.global_search(q)}


# ══════════════════════════════════════════════════════════════
# EDUCATION
# ══════════════════════════════════════════════════════════════

@router.get("/education", response_model=list[EducationResponse])
async def list_education(service: ProfileService = Depends(get_profile_service)):
    return await service.list_education()


@router.post("/education", response_model=EducationResponse, status_code=201)
async def create_education(data: EducationCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_education(data.model_dump())


@router.get("/education/{edu_id}", response_model=EducationResponse)
async def get_education(edu_id: str, service: ProfileService = Depends(get_profile_service)):
    edu = await service.get_education(edu_id)
    if edu is None:
        raise HTTPException(status_code=404, detail="Education not found")
    return edu


@router.put("/education/{edu_id}", response_model=EducationResponse)
async def update_education(edu_id: str, data: EducationUpdate, service: ProfileService = Depends(get_profile_service)):
    edu = await service.update_education(edu_id, data.model_dump(exclude_unset=True))
    if edu is None:
        raise HTTPException(status_code=404, detail="Education not found")
    return edu


@router.delete("/education/{edu_id}", status_code=204)
async def delete_education(edu_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_education(edu_id):
        raise HTTPException(status_code=404, detail="Education not found")


# ══════════════════════════════════════════════════════════════
# EXPERIENCE
# ══════════════════════════════════════════════════════════════

@router.get("/experience", response_model=list[ExperienceResponse])
async def list_experience(service: ProfileService = Depends(get_profile_service)):
    return await service.list_experience()


@router.post("/experience", response_model=ExperienceResponse, status_code=201)
async def create_experience(data: ExperienceCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_experience(data.model_dump())


@router.get("/experience/{exp_id}", response_model=ExperienceResponse)
async def get_experience(exp_id: str, service: ProfileService = Depends(get_profile_service)):
    exp = await service.get_experience(exp_id)
    if exp is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp


@router.put("/experience/{exp_id}", response_model=ExperienceResponse)
async def update_experience(exp_id: str, data: ExperienceUpdate, service: ProfileService = Depends(get_profile_service)):
    exp = await service.update_experience(exp_id, data.model_dump(exclude_unset=True))
    if exp is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp


@router.delete("/experience/{exp_id}", status_code=204)
async def delete_experience(exp_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_experience(exp_id):
        raise HTTPException(status_code=404, detail="Experience not found")


# ══════════════════════════════════════════════════════════════
# PROJECTS
# ══════════════════════════════════════════════════════════════

@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(service: ProfileService = Depends(get_profile_service)):
    return await service.list_projects()


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(data: ProjectCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_project(data.model_dump())


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, service: ProfileService = Depends(get_profile_service)):
    project = await service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectUpdate, service: ProfileService = Depends(get_profile_service)):
    project = await service.update_project(project_id, data.model_dump(exclude_unset=True))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_project(project_id):
        raise HTTPException(status_code=404, detail="Project not found")


# ══════════════════════════════════════════════════════════════
# SKILLS
# ══════════════════════════════════════════════════════════════

@router.get("/skills", response_model=list[SkillResponse])
async def list_skills(service: ProfileService = Depends(get_profile_service)):
    return await service.list_skills()


@router.post("/skills", response_model=SkillResponse, status_code=201)
async def create_skill(data: SkillCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_skill(data.model_dump())


@router.get("/skills/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str, service: ProfileService = Depends(get_profile_service)):
    skill = await service.get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: str, data: SkillUpdate, service: ProfileService = Depends(get_profile_service)):
    skill = await service.update_skill(skill_id, data.model_dump(exclude_unset=True))
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.delete("/skills/{skill_id}", status_code=204)
async def delete_skill(skill_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_skill(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")


# ══════════════════════════════════════════════════════════════
# CERTIFICATES
# ══════════════════════════════════════════════════════════════

@router.get("/certificates", response_model=list[CertificateResponse])
async def list_certificates(service: ProfileService = Depends(get_profile_service)):
    return await service.list_certificates()


@router.post("/certificates", response_model=CertificateResponse, status_code=201)
async def create_certificate(data: CertificateCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_certificate(data.model_dump())


@router.get("/certificates/{cert_id}", response_model=CertificateResponse)
async def get_certificate(cert_id: str, service: ProfileService = Depends(get_profile_service)):
    cert = await service.get_certificate(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.put("/certificates/{cert_id}", response_model=CertificateResponse)
async def update_certificate(cert_id: str, data: CertificateUpdate, service: ProfileService = Depends(get_profile_service)):
    cert = await service.update_certificate(cert_id, data.model_dump(exclude_unset=True))
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.delete("/certificates/{cert_id}", status_code=204)
async def delete_certificate(cert_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_certificate(cert_id):
        raise HTTPException(status_code=404, detail="Certificate not found")


# ══════════════════════════════════════════════════════════════
# ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════

@router.get("/achievements", response_model=list[AchievementResponse])
async def list_achievements(service: ProfileService = Depends(get_profile_service)):
    return await service.list_achievements()


@router.post("/achievements", response_model=AchievementResponse, status_code=201)
async def create_achievement(data: AchievementCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_achievement(data.model_dump())


@router.get("/achievements/{ach_id}", response_model=AchievementResponse)
async def get_achievement(ach_id: str, service: ProfileService = Depends(get_profile_service)):
    ach = await service.get_achievement(ach_id)
    if ach is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return ach


@router.put("/achievements/{ach_id}", response_model=AchievementResponse)
async def update_achievement(ach_id: str, data: AchievementUpdate, service: ProfileService = Depends(get_profile_service)):
    ach = await service.update_achievement(ach_id, data.model_dump(exclude_unset=True))
    if ach is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return ach


@router.delete("/achievements/{ach_id}", status_code=204)
async def delete_achievement(ach_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_achievement(ach_id):
        raise HTTPException(status_code=404, detail="Achievement not found")


# ══════════════════════════════════════════════════════════════
# LANGUAGES
# ══════════════════════════════════════════════════════════════

@router.get("/languages", response_model=list[LanguageResponse])
async def list_languages(service: ProfileService = Depends(get_profile_service)):
    return await service.list_languages()


@router.post("/languages", response_model=LanguageResponse, status_code=201)
async def create_language(data: LanguageCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_language(data.model_dump())


@router.get("/languages/{lang_id}", response_model=LanguageResponse)
async def get_language(lang_id: str, service: ProfileService = Depends(get_profile_service)):
    lang = await service.get_language(lang_id)
    if lang is None:
        raise HTTPException(status_code=404, detail="Language not found")
    return lang


@router.put("/languages/{lang_id}", response_model=LanguageResponse)
async def update_language(lang_id: str, data: LanguageUpdate, service: ProfileService = Depends(get_profile_service)):
    lang = await service.update_language(lang_id, data.model_dump(exclude_unset=True))
    if lang is None:
        raise HTTPException(status_code=404, detail="Language not found")
    return lang


@router.delete("/languages/{lang_id}", status_code=204)
async def delete_language(lang_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_language(lang_id):
        raise HTTPException(status_code=404, detail="Language not found")


# ══════════════════════════════════════════════════════════════
# PUBLICATIONS
# ══════════════════════════════════════════════════════════════

@router.get("/publications", response_model=list[PublicationResponse])
async def list_publications(service: ProfileService = Depends(get_profile_service)):
    return await service.list_publications()


@router.post("/publications", response_model=PublicationResponse, status_code=201)
async def create_publication(data: PublicationCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_publication(data.model_dump())


@router.get("/publications/{pub_id}", response_model=PublicationResponse)
async def get_publication(pub_id: str, service: ProfileService = Depends(get_profile_service)):
    pub = await service.get_publication(pub_id)
    if pub is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return pub


@router.put("/publications/{pub_id}", response_model=PublicationResponse)
async def update_publication(pub_id: str, data: PublicationUpdate, service: ProfileService = Depends(get_profile_service)):
    pub = await service.update_publication(pub_id, data.model_dump(exclude_unset=True))
    if pub is None:
        raise HTTPException(status_code=404, detail="Publication not found")
    return pub


@router.delete("/publications/{pub_id}", status_code=204)
async def delete_publication(pub_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_publication(pub_id):
        raise HTTPException(status_code=404, detail="Publication not found")


# ══════════════════════════════════════════════════════════════
# AWARDS
# ══════════════════════════════════════════════════════════════

@router.get("/awards", response_model=list[AwardResponse])
async def list_awards(service: ProfileService = Depends(get_profile_service)):
    return await service.list_awards()


@router.post("/awards", response_model=AwardResponse, status_code=201)
async def create_award(data: AwardCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_award(data.model_dump())


@router.get("/awards/{award_id}", response_model=AwardResponse)
async def get_award(award_id: str, service: ProfileService = Depends(get_profile_service)):
    award = await service.get_award(award_id)
    if award is None:
        raise HTTPException(status_code=404, detail="Award not found")
    return award


@router.put("/awards/{award_id}", response_model=AwardResponse)
async def update_award(award_id: str, data: AwardUpdate, service: ProfileService = Depends(get_profile_service)):
    award = await service.update_award(award_id, data.model_dump(exclude_unset=True))
    if award is None:
        raise HTTPException(status_code=404, detail="Award not found")
    return award


@router.delete("/awards/{award_id}", status_code=204)
async def delete_award(award_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_award(award_id):
        raise HTTPException(status_code=404, detail="Award not found")


# ══════════════════════════════════════════════════════════════
# SOCIAL LINKS
# ══════════════════════════════════════════════════════════════

@router.get("/social-links", response_model=list[SocialLinkResponse])
async def list_social_links(service: ProfileService = Depends(get_profile_service)):
    return await service.list_social_links()


@router.post("/social-links", response_model=SocialLinkResponse, status_code=201)
async def create_social_link(data: SocialLinkCreate, service: ProfileService = Depends(get_profile_service)):
    return await service.create_social_link(data.model_dump())


@router.get("/social-links/{link_id}", response_model=SocialLinkResponse)
async def get_social_link(link_id: str, service: ProfileService = Depends(get_profile_service)):
    link = await service.get_social_link(link_id)
    if link is None:
        raise HTTPException(status_code=404, detail="Social link not found")
    return link


@router.put("/social-links/{link_id}", response_model=SocialLinkResponse)
async def update_social_link(link_id: str, data: SocialLinkUpdate, service: ProfileService = Depends(get_profile_service)):
    link = await service.update_social_link(link_id, data.model_dump(exclude_unset=True))
    if link is None:
        raise HTTPException(status_code=404, detail="Social link not found")
    return link


@router.delete("/social-links/{link_id}", status_code=204)
async def delete_social_link(link_id: str, service: ProfileService = Depends(get_profile_service)):
    if not await service.delete_social_link(link_id):
        raise HTTPException(status_code=404, detail="Social link not found")
