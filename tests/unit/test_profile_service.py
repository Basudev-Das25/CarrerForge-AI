"""Unit tests for the ProfileService business logic layer."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class MockRepository:
    """Mock repository for testing service layer in isolation."""

    def __init__(self, items=None):
        self.items = items or []
        self._next_id = "test-id-001"

    async def get(self, id):
        for item in self.items:
            if item.id == id:
                return item
        return None

    async def list(self, filters=None, order_by=None, limit=100, offset=0):
        return self.items

    async def count(self, filters=None):
        return len(self.items)

    async def create(self, data):
        obj = MagicMock()
        for k, v in data.items():
            setattr(obj, k, v)
        obj.id = self._next_id
        self.items.append(obj)
        return obj

    async def update(self, id, data):
        obj = await self.get(id)
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
        return obj

    async def soft_delete(self, id):
        return await self.delete(id)

    async def delete(self, id):
        for i, item in enumerate(self.items):
            if item.id == id:
                self.items.pop(i)
                return True
        return False

    async def exists(self, id):
        return await self.get(id) is not None


def _make_user(user_id="default", full_name="Test User"):
    user = MagicMock()
    user.id = user_id
    user.full_name = full_name
    user.email = "test@example.com"
    user.phone = "+1-555-0100"
    user.location = "Test City"
    user.summary = "A professional with extensive experience in testing software."
    user.version = 1
    return user


def _make_skill(user_id="default", name="Python"):
    skill = MagicMock()
    skill.id = "skill-001"
    skill.user_id = user_id
    skill.name = name
    skill.category = "programming"
    skill.level = "advanced"
    skill.years_experience = 5.0
    skill.is_primary = True
    return skill


def _make_education(user_id="default"):
    edu = MagicMock()
    edu.id = "edu-001"
    edu.user_id = user_id
    edu.degree = "B.S. Computer Science"
    edu.field_of_study = "Computer Science"
    edu.institution = "MIT"
    edu.start_date = "2018-09"
    edu.end_date = "2022-06"
    return edu


def _make_experience(user_id="default"):
    exp = MagicMock()
    exp.id = "exp-001"
    exp.user_id = user_id
    exp.company = "Google"
    exp.title = "Software Engineer"
    exp.start_date = "2022-06"
    return exp


def _make_language(user_id="default", name="English"):
    lang = MagicMock()
    lang.id = "lang-001"
    lang.user_id = user_id
    lang.name = name
    lang.proficiency = "native"
    lang.is_native = True
    return lang


def _make_publication(user_id="default"):
    pub = MagicMock()
    pub.id = "pub-001"
    pub.user_id = user_id
    pub.title = "Test Paper"
    pub.authors = ["Author One"]
    pub.venue = "IEEE"
    return pub


def _make_award(user_id="default"):
    award = MagicMock()
    award.id = "award-001"
    award.user_id = user_id
    award.title = "Best Paper"
    award.issuer = "IEEE"
    return award


def _make_social_link(user_id="default"):
    link = MagicMock()
    link.id = "link-001"
    link.user_id = user_id
    link.platform = "GitHub"
    link.url = "https://github.com/test"
    link.username = "testuser"
    return link


@pytest.mark.asyncio
async def test_user_profile_operations():
    """Test user profile CRUD through the mock repository."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    # Mock all repositories
    user = _make_user()
    service.users = MockRepository([user])
    service.education = MockRepository()
    service.experience = MockRepository()
    service.projects = MockRepository()
    service.skills = MockRepository()
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository()
    service.publications = MockRepository()
    service.awards = MockRepository()
    service.social_links = MockRepository()
    service.documents = MockRepository()
    service.resumes = MockRepository()

    # Test get_or_create_user
    result = await service.get_or_create_user()
    assert result.id == "default"
    assert result.full_name == "Test User"

    # Test update_profile
    result = await service.update_profile({"full_name": "Updated Name"})
    assert result.full_name == "Updated Name"


@pytest.mark.asyncio
async def test_education_crud():
    """Test education CRUD operations."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    edu = _make_education()
    service.users = MockRepository([_make_user()])
    service.education = MockRepository([edu])
    service.experience = MockRepository()
    service.projects = MockRepository()
    service.skills = MockRepository()
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository()
    service.publications = MockRepository()
    service.awards = MockRepository()
    service.social_links = MockRepository()
    service.documents = MockRepository()
    service.resumes = MockRepository()

    # Test list
    items = await service.list_education()
    assert len(items) == 1
    assert items[0].degree == "B.S. Computer Science"

    # Test get
    item = await service.get_education("edu-001")
    assert item is not None
    assert item.institution == "MIT"

    # Test get non-existent
    item = await service.get_education("non-existent")
    assert item is None

    # Test create
    new_edu = await service.create_education({
        "degree": "M.S. AI",
        "institution": "Stanford",
        "start_date": "2022-09",
    })
    assert new_edu.user_id == "default"

    # Test update
    updated = await service.update_education("edu-001", {"gpa": 3.9})
    assert updated is not None

    # Test delete
    deleted = await service.delete_education("edu-001")
    assert deleted is True


@pytest.mark.asyncio
async def test_skill_crud():
    """Test skill CRUD operations."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    skill = _make_skill()
    service.users = MockRepository([_make_user()])
    service.education = MockRepository()
    service.experience = MockRepository()
    service.projects = MockRepository()
    service.skills = MockRepository([skill])
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository()
    service.publications = MockRepository()
    service.awards = MockRepository()
    service.social_links = MockRepository()
    service.documents = MockRepository()
    service.resumes = MockRepository()

    # Test list
    items = await service.list_skills()
    assert len(items) == 1
    assert items[0].name == "Python"

    # Test create
    new_skill = await service.create_skill({
        "name": "React",
        "category": "framework",
        "level": "advanced",
    })
    assert new_skill.user_id == "default"
    assert len(service.skills.items) == 2

    # Test update
    updated = await service.update_skill("skill-001", {"years_experience": 7.0})
    assert updated is not None

    # Test delete
    deleted = await service.delete_skill("skill-001")
    assert deleted is True


@pytest.mark.asyncio
async def test_language_crud():
    """Test language CRUD operations."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    lang = _make_language()
    service.users = MockRepository([_make_user()])
    service.education = MockRepository()
    service.experience = MockRepository()
    service.projects = MockRepository()
    service.skills = MockRepository()
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository([lang])
    service.publications = MockRepository()
    service.awards = MockRepository()
    service.social_links = MockRepository()
    service.documents = MockRepository()
    service.resumes = MockRepository()

    # Test list
    items = await service.list_languages()
    assert len(items) == 1
    assert items[0].name == "English"

    # Test create
    new_lang = await service.create_language({
        "name": "Spanish",
        "proficiency": "intermediate",
    })
    assert new_lang.user_id == "default"

    # Test get
    item = await service.get_language("lang-001")
    assert item is not None
    assert item.name == "English"

    # Test delete
    deleted = await service.delete_language("lang-001")
    assert deleted is True


@pytest.mark.asyncio
async def test_publication_crud():
    """Test publication CRUD operations."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    pub = _make_publication()
    service.users = MockRepository([_make_user()])
    service.education = MockRepository()
    service.experience = MockRepository()
    service.projects = MockRepository()
    service.skills = MockRepository()
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository()
    service.publications = MockRepository([pub])
    service.awards = MockRepository()
    service.social_links = MockRepository()
    service.documents = MockRepository()
    service.resumes = MockRepository()

    # Test create
    new_pub = await service.create_publication({
        "title": "Another Paper",
        "authors": ["Author Two"],
        "venue": "ACM",
    })
    assert new_pub.user_id == "default"

    # Test update
    updated = await service.update_publication("pub-001", {"doi": "10.1234/test"})
    assert updated is not None

    # Test delete
    deleted = await service.delete_publication("pub-001")
    assert deleted is True


@pytest.mark.asyncio
async def test_award_crud():
    """Test award CRUD operations."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    award = _make_award()
    service.users = MockRepository([_make_user()])
    service.education = MockRepository()
    service.experience = MockRepository()
    service.projects = MockRepository()
    service.skills = MockRepository()
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository()
    service.publications = MockRepository()
    service.awards = MockRepository([award])
    service.social_links = MockRepository()
    service.documents = MockRepository()
    service.resumes = MockRepository()

    # Test create
    new_award = await service.create_award({
        "title": "Innovation Award",
        "issuer": "Tech Corp",
    })
    assert new_award.user_id == "default"

    # Test delete
    deleted = await service.delete_award("award-001")
    assert deleted is True


@pytest.mark.asyncio
async def test_social_link_crud():
    """Test social link CRUD operations."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    link = _make_social_link()
    service.users = MockRepository([_make_user()])
    service.education = MockRepository()
    service.experience = MockRepository()
    service.projects = MockRepository()
    service.skills = MockRepository()
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository()
    service.publications = MockRepository()
    service.awards = MockRepository()
    service.social_links = MockRepository([link])
    service.documents = MockRepository()
    service.resumes = MockRepository()

    # Test list
    items = await service.list_social_links()
    assert len(items) == 1
    assert items[0].platform == "GitHub"

    # Test create
    new_link = await service.create_social_link({
        "platform": "LinkedIn",
        "url": "https://linkedin.com/in/test",
    })
    assert new_link.user_id == "default"

    # Test delete
    deleted = await service.delete_social_link("link-001")
    assert deleted is True


@pytest.mark.asyncio
async def test_profile_completion():
    """Test profile completion calculation."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    # Create a complete user
    user = _make_user()
    user.full_name = "Complete User"
    user.email = "complete@example.com"
    user.phone = "+1-555-0100"
    user.location = "Test City"
    user.summary = "A professional with extensive experience in testing software."

    service.users = MockRepository([user])
    service.education = MockRepository([_make_education()])
    service.experience = MockRepository([_make_experience()])
    service.skills = MockRepository([_make_skill()])
    service.projects = MockRepository()
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository([_make_language()])
    service.publications = MockRepository()
    service.awards = MockRepository()
    service.social_links = MockRepository()
    service.documents = MockRepository()
    service.resumes = MockRepository()

    completion = await service.calculate_profile_completion()
    assert completion >= 70.0  # Most fields filled


@pytest.mark.asyncio
async def test_dashboard_data():
    """Test dashboard data aggregation."""
    from app.services.profile import ProfileService

    session = AsyncMock()
    service = ProfileService(session=session, user_id="default")

    user = _make_user()
    service.users = MockRepository([user])
    service.education = MockRepository([_make_education()])
    service.experience = MockRepository([_make_experience()])
    service.skills = MockRepository([_make_skill()])
    service.projects = MockRepository()
    service.certificates = MockRepository()
    service.achievements = MockRepository()
    service.languages = MockRepository([_make_language()])
    service.publications = MockRepository()
    service.awards = MockRepository()
    service.social_links = MockRepository()
    service.documents = MockRepository()
    service.resumes = MockRepository()

    data = await service.get_dashboard_data()
    assert data["profile"].full_name == "Test User"
    assert data["total_education"] == 1
    assert data["total_experience"] == 1
    assert data["total_skills"] == 1
    assert data["total_languages"] == 1
    assert data["profile_completion"] >= 0
