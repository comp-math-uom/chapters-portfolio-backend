# Chapters Portfolio Backend Data Models and Storage

## Storage Stack

- Database: MongoDB
- Async driver: Motor (`AsyncIOMotorClient`)
- ODM: Beanie
- Initialization entrypoint: `core/database.py`

Beanie is initialized with:

- `models.project.Project`
- `models.feedback.Feedback`

## Collections and Documents

### `projects` collection (`Project`)

Defined in `models/project.py`:

- `topic: str`
- `description: str`
- `batch: str`
- `contributors: List[str]`
- `search_tags: List[str]`
- `date: datetime`
- `image: str`
- `width: int`
- `height: int`
- `visibility: bool = True`
- `featured: bool = True`
- `created_at: datetime` (server-side default)

Helper methods:

- `get_visible_projects()`
- `get_featured_projects()`

### `feedback` collection (`Feedback`)

Defined in `models/feedback.py`:

- `project_id: str` (stored as string, not `ObjectId`)
- `username: str`
- `content: str`
- `rank: Optional[int]`
- `created_at: datetime` (server-side default)

## API Schema Boundary

Schema contracts are under `schemas/`:

- `ProjectCreateSchema`, `ProjectUpdateSchema`, `ProjectSchema`, `ProjectListSchema`
- `FeedbackCreate`, `FeedbackUpdate`, `FeedbackResponse`

Important distinction:

- Models define persistence shape and database behavior.
- Schemas define request/response validation and external API contract.

## Data Access Paths

- `database/project.py` handles most project CRUD/search operations.
- `routes/project.py` also directly uses model methods (`Project.get`, `Feedback.find`) in several feedback and visibility checks.
- `database/feedback.py` exists but is not currently wired by routes.

## Query Semantics

- Public listing uses visibility filtering (`visibility=True`).
- Featured listing requires both `featured=True` and `visibility=True`.
- Search uses case-insensitive regex over `topic` and `description`.
- Feedback list endpoint sorts by `created_at` descending.

## Data Invariants and Risks

- Route handlers rely on ObjectId validation for most project/feedback path IDs.
- `PUT /projects/{projectId}/featured` currently bypasses route-level ObjectId validation before DB conversion.
- Several list/search operations are unbounded and should be considered a scaling risk.
- Regex search currently accepts raw query strings and should be treated as query-safety sensitive.

## Operational Recommendations

- Introduce pagination limits for list and feedback endpoints.
- Define and document index strategy for frequent query paths.
- Document backup/restore and migration workflow before production-scale growth.
