"""Profile router — complete CRUD for all profile entities.

Every endpoint is scoped to a single user (user_id = "default" for local-first).
"""

from fastapi import APIRouter, Depends, HTTPException
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
    DashboardData,
)

router = APIRouter()

# For local-first, user_id is always "default"
DEFAULT_USER_ID = "default"


def get_profile_service(db: AsyncSession = Depends(get_db)) -> ProfileService:
    return ProfileService(session=db, user_id=DEFAULT_USER_ID)


# ══════════════════════════════════════════════════════════════
# USER PROFILE
# ══════════════════════════════════════════════════════════════

@router.get("/profile", response_model=UserResponse)
async def get_profile(service: ProfileService = Depends(get_profile_service)):
    user = await service.get_or_create_user()
    return user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    user = await service.update_profile(data.model_dump(exclude_unset=True))
    return user


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(service: ProfileService = Depends(get_profile_service)):
    return await service.get_dashboard_data()


@router.get("/completion")
async def get_completion(service: ProfileService = Depends(get_profile_service)):
    return {"completion": await service.calculate_profile_completion()}


# ══════════════════════════════════════════════════════════════
# EDUCATION
# ══════════════════════════════════════════════════════════════

@router.get("/education", response_model=list[EducationResponse])
async def list_education(service: ProfileService = Depends(get_profile_service)):
    return await service.list_education()


@router.post("/education", response_model=EducationResponse, status_code=201)
async def create_education(
    data: EducationCreate,
    service: ProfileService = Depends(get_profile_service),
):
    return await service.create_education(data.model_dump())


@router.get("/education/{edu_id}", response_model=EducationResponse)
async def get_education(edu_id: str, service: ProfileService = Depends(get_profile_service)):
    edu = await service.get_education(edu_id)
    if edu is None:
        raise HTTPException(status_code=404, detail="Education not found")
    return edu


@router.put("/education/{edu_id}", response_model=EducationResponse)
async def update_education(
    edu_id: str,
    data: EducationUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    edu = await service.update_education(edu_id, data.model_dump(exclude_unset=True))
    if edu is None:
        raise HTTPException(status_code=404, detail="Education not found")
    return edu


@router.delete("/education/{edu_id}", status_code=204)
async def delete_education(edu_id: str, service: ProfileService = Depends(get_profile_service)):
    deleted = await service.delete_education(edu_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Education not found")


# ══════════════════════════════════════════════════════════════
# EXPERIENCE
# ══════════════════════════════════════════════════════════════

@router.get("/experience", response_model=list[ExperienceResponse])
async def list_experience(service: ProfileService = Depends(get_profile_service)):
    return await service.list_experience()


@router.post("/experience", response_model=ExperienceResponse, status_code=201)
async def create_experience(
    data: ExperienceCreate,
    service: ProfileService = Depends(get_profile_service),
):
    return await service.create_experience(data.model_dump())


@router.get("/experience/{exp_id}", response_model=ExperienceResponse)
async def get_experience(exp_id: str, service: ProfileService = Depends(get_profile_service)):
    exp = await service.get_experience(exp_id)
    if exp is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp


@router.put("/experience/{exp_id}", response_model=ExperienceResponse)
async def update_experience(
    exp_id: str,
    data: ExperienceUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    exp = await service.update_experience(exp_id, data.model_dump(exclude_unset=True))
    if exp is None:
        raise HTTPException(status_code=404, detail="Experience not found")
    return exp


@router.delete("/experience/{exp_id}", status_code=204)
async def delete_experience(exp_id: str, service: ProfileService = Depends(get_profile_service)):
    deleted = await service.delete_experience(exp_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Experience not found")


# ══════════════════════════════════════════════════════════════
# PROJECTS
# ══════════════════════════════════════════════════════════════

@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(service: ProfileService = Depends(get_profile_service)):
    return await service.list_projects()


@router.post("/projects", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    service: ProfileService = Depends(get_profile_service),
):
    return await service.create_project(data.model_dump())


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, service: ProfileService = Depends(get_profile_service)):
    project = await service.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    project = await service.update_project(project_id, data.model_dump(exclude_unset=True))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str, service: ProfileService = Depends(get_profile_service)):
    deleted = await service.delete_project(project_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Project not found")


# ══════════════════════════════════════════════════════════════
# SKILLS
# ══════════════════════════════════════════════════════════════

@router.get("/skills", response_model=list[SkillResponse])
async def list_skills(service: ProfileService = Depends(get_profile_service)):
    return await service.list_skills()


@router.post("/skills", response_model=SkillResponse, status_code=201)
async def create_skill(
    data: SkillCreate,
    service: ProfileService = Depends(get_profile_service),
):
    return await service.create_skill(data.model_dump())


@router.get("/skills/{skill_id}", response_model=SkillResponse)
async def get_skill(skill_id: str, service: ProfileService = Depends(get_profile_service)):
    skill = await service.get_skill(skill_id)
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.put("/skills/{skill_id}", response_model=SkillResponse)
async def update_skill(
    skill_id: str,
    data: SkillUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    skill = await service.update_skill(skill_id, data.model_dump(exclude_unset=True))
    if skill is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@router.delete("/skills/{skill_id}", status_code=204)
async def delete_skill(skill_id: str, service: ProfileService = Depends(get_profile_service)):
    deleted = await service.delete_skill(skill_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Skill not found")


# ══════════════════════════════════════════════════════════════
# CERTIFICATES
# ══════════════════════════════════════════════════════════════

@router.get("/certificates", response_model=list[CertificateResponse])
async def list_certificates(service: ProfileService = Depends(get_profile_service)):
    return await service.list_certificates()


@router.post("/certificates", response_model=CertificateResponse, status_code=201)
async def create_certificate(
    data: CertificateCreate,
    service: ProfileService = Depends(get_profile_service),
):
    return await service.create_certificate(data.model_dump())


@router.get("/certificates/{cert_id}", response_model=CertificateResponse)
async def get_certificate(cert_id: str, service: ProfileService = Depends(get_profile_service)):
    cert = await service.get_certificate(cert_id)
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.put("/certificates/{cert_id}", response_model=CertificateResponse)
async def update_certificate(
    cert_id: str,
    data: CertificateUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    cert = await service.update_certificate(cert_id, data.model_dump(exclude_unset=True))
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.delete("/certificates/{cert_id}", status_code=204)
async def delete_certificate(cert_id: str, service: ProfileService = Depends(get_profile_service)):
    deleted = await service.delete_certificate(cert_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Certificate not found")


# ══════════════════════════════════════════════════════════════
# ACHIEVEMENTS
# ══════════════════════════════════════════════════════════════

@router.get("/achievements", response_model=list[AchievementResponse])
async def list_achievements(service: ProfileService = Depends(get_profile_service)):
    return await service.list_achievements()


@router.post("/achievements", response_model=AchievementResponse, status_code=201)
async def create_achievement(
    data: AchievementCreate,
    service: ProfileService = Depends(get_profile_service),
):
    return await service.create_achievement(data.model_dump())


@router.get("/achievements/{ach_id}", response_model=AchievementResponse)
async def get_achievement(ach_id: str, service: ProfileService = Depends(get_profile_service)):
    ach = await service.get_achievement(ach_id)
    if ach is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return ach


@router.put("/achievements/{ach_id}", response_model=AchievementResponse)
async def update_achievement(
    ach_id: str,
    data: AchievementUpdate,
    service: ProfileService = Depends(get_profile_service),
):
    ach = await service.update_achievement(ach_id, data.model_dump(exclude_unset=True))
    if ach is None:
        raise HTTPException(status_code=404, detail="Achievement not found")
    return ach


@router.delete("/achievements/{ach_id}", status_code=204)
async def delete_achievement(ach_id: str, service: ProfileService = Depends(get_profile_service)):
    deleted = await service.delete_achievement(ach_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Achievement not found")
