# Backend Development Audit & Improvement Plan

**Framework:** Flask + Peewee ORM  
**Date:** April 4, 2026  
**Status:** REQUIRES REFACTORING

---

## BFRI (Backend Feasibility & Risk Index) Assessment

### Current Score: **-2** (DANGEROUS)

| Dimension | Score | Reason |
|-----------|-------|--------|
| **Architectural Fit** | 2 | Missing controller + repository layers; routes call services directly |
| **Business Logic Complexity** | 3 | URL shortening is moderate; user/event models are simple |
| **Data Risk** | 2 | FK relationships exist but no transaction handling; direct model access |
| **Operational Risk** | 1 | No Sentry; no performance tracing; only basic structured logging |
| **Testability** | 2 | Tests exist but lack base fixtures; hard to mock services without DI |

**Calculation:** (2 + 2) − (3 + 2 + 1) = **-2**

**Verdict:** Current architecture violates core layering doctrine. Unsafe for production without refactoring.

---

## Architecture Violation Summary

### ❌ **CRITICAL ISSUES**

| Issue | Current | Required | Impact |
|-------|---------|----------|--------|
| **Controller Layer** | ✗ Missing | ✓ Required | Routes have business logic; no coordination layer |
| **Repository Pattern** | ✗ Missing | ✓ Required | Services access Peewee models directly; hard to test |
| **Dependency Injection** | Manual | Constructor-based | Tight coupling; hard to mock in tests |
| **Input Validation** | Manual type checks | Zod/Pydantic schema | Fragile; not DRY; inconsistent |
| **Error Tracking (Sentry)** | ✗ Missing | ✓ Required | Blind spot for production errors |
| **Observability** | Basic logging | Sentry tracing + logs | No performance insights |

### ⚠️ **MODERATE ISSUES**

| Issue | Current | Impact |
|-------|---------|--------|
| Configuration pattern | `os.getenv()` in config module | Works but less robust than centralized const |
| Service instantiation | Per-request in route | Creates new service per request; wasteful |
| Error handling scope | Only in route handlers | Services throw; no middleware wrapper |
| Test framework | pytest + fakeredis | Good, but no base controller/service test fixtures |

### ✅ **STRENGTHS**

| Strength | Value |
|----------|-------|
| **Error Classes** | Well-structured custom exception hierarchy |
| **Middleware** | Excellent request logging with tracing |
| **Models** | Correct FK relationships; good naming |
| **Config Management** | Env-based with class hierarchy |
| **Services** | Business logic is isolated (URLShortenerService) |

---

## Improvement Roadmap

### PHASE 1: Add Controller Layer (CRITICAL)

**What:** Introduce controllers as coordination points between routes and services.

**Example Structure:**

```python
# backend/app/controllers/base_controller.py
class BaseController:
    def handle_success(self, res, data, status=200):
        return jsonify(data), status
    
    def handle_error(self, error, res, operation):
        Sentry.captureException(error)
        if isinstance(error, AppError):
            return jsonify(error=error.error_code, message=str(error)), error.status_code
        return jsonify(error='internal_error'), 500

# backend/app/controllers/url_controller.py
class URLController(BaseController):
    def __init__(self, url_service: URLShortenerService):
        self.url_service = url_service
    
    def create_short_link(self, req, res):
        try:
            schema = CreateShortLinkSchema.parse(req.get_json())
            short_url = self.url_service.create_short_url(
                original_url=schema.url,
                custom_alias=schema.custom_alias,
                creator_ip=req.remote_addr
            )
            return self.handle_success(res, short_url, 201)
        except Exception as e:
            return self.handle_error(e, res, 'create_short_link')
```

**Why:** Routes stay thin; controllers coordinate; services don't touch Flask.

---

### PHASE 2: Add Repository Layer (CRITICAL)

**What:** Repositories encapsulate Peewee queries; services use repositories, not models directly.

**Example:**

```python
# backend/app/repositories/url_repository.py
class URLRepository:
    def create(self, code, original_url, user_id=None, expires_at=None):
        return ShortURL.create(code=code, original_url=original_url, user_id=user_id, expires_at=expires_at)
    
    def find_by_code(self, code):
        try:
            return ShortURL.get(ShortURL.code == code)
        except DoesNotExist:
            return None
    
    def get_recent_visits(self, short_url_id, limit=25):
        return list(
            LinkVisit.select()
            .where(LinkVisit.short_url_id == short_url_id)
            .order_by(LinkVisit.accessed_at.desc())
            .limit(limit)
        )

# backend/app/services/url_shortener.py
class URLShortenerService:
    def __init__(self, url_repo: URLRepository):
        self.url_repo = url_repo
    
    def create_short_url(self, original_url, custom_alias=None):
        code = self._get_code(custom_alias)
        return self.url_repo.create(code=code, original_url=original_url)
```

**Why:** Tests can mock `URLRepository`; queries are centralized; services are testable.

---

### PHASE 3: Add Zod/Pydantic Schema Validation (HIGH PRIORITY)

**What:** Replace manual `request.get_json()` type checks with declarative schemas.

**Example (using Pydantic):**

```python
# backend/app/validators/url_schema.py
from pydantic import BaseModel, HttpUrl, Field

class CreateShortLinkSchema(BaseModel):
    url: HttpUrl
    custom_alias: str | None = None
    expires_at: str | None = None
    
    class Config:
        str_strip_whitespace = True

# In controller:
schema = CreateShortLinkSchema(**request.get_json())
```

**Why:** Declarative; automatic validation; type hints; reusable; DRY.

---

### PHASE 4: Add Sentry Integration (HIGH PRIORITY)

**What:** Integrate Sentry for error tracking and performance monitoring.

**Steps:**

1. Install `sentry-sdk[flask]`
2. Initialize in `backend/app/__init__.py` FIRST import:
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.flask import FlaskIntegration
   
   sentry_sdk.init(
       dsn=config.SENTRY_DSN,
       integrations=[FlaskIntegration()],
       trace_sample_rate=0.1
   )
   ```
3. Wrap errors in controllers/services:
   ```python
   except Exception as e:
       sentry_sdk.captureException(e)
       raise
   ```

**Why:** Blind spot elimination; production visibility; performance tracing.

---

### PHASE 5: Add Proper Dependency Injection (MEDIUM PRIORITY)

**What:** Use a simple DI pattern (or library like `injector`) so services/controllers receive deps via constructor.

**Example:**

```python
# backend/app/di.py
class Container:
    def __init__(self):
        self.url_repo = URLRepository()
        self.url_service = URLShortenerService(self.url_repo)
        self.url_controller = URLController(self.url_service)

# In routes:
container = Container()

@api_bp.post('/links')
def create_link(req):
    return container.url_controller.create_short_link(req, res)
```

**Why:** Mockable in tests; loose coupling; reusable across endpoints.

---

### PHASE 6: Align with Automated Test Requirements (BLOCKING)

**Current:** Only implements `/api/v1/links*` (old contract)  
**Required:** Must implement `/users*`, `/urls*`, `/events*` per AUTOMATED_TESTS.md

**Action Required:**
1. Add User model + repository + controller
2. Add Event model + repository + controller  
3. Rename Link → URL (for contract alignment)
4. Implement all 13 endpoints from AUTOMATED_TESTS.md

---

## Implementation Checklist

### PHASE 1 (Controller Layer)
- [ ] Create `backend/app/controllers/base_controller.py`
- [ ] Create `backend/app/controllers/url_controller.py`
- [ ] Create `backend/app/controllers/user_controller.py`
- [ ] Update `backend/app/routes/api.py` to use controllers
- [ ] Add error handler wrapper for async routes

### PHASE 2 (Repository Pattern)
- [ ] Create `backend/app/repositories/base_repository.py`
- [ ] Create `backend/app/repositories/url_repository.py`
- [ ] Create `backend/app/repositories/user_repository.py`
- [ ] Refactor services to use repos instead of models
- [ ] Add unit tests for repositories

### PHASE 3 (Schema Validation)
- [ ] Add `pydantic` to dependencies
- [ ] Create `backend/app/validators/url_schema.py`
- [ ] Create `backend/app/validators/user_schema.py`
- [ ] Update controllers to use schemas
- [ ] Test validation with invalid inputs

### PHASE 4 (Sentry)
- [ ] Add `sentry-sdk[flask]` to dependencies
- [ ] Create `backend/app/config.py` entry for `SENTRY_DSN`
- [ ] Initialize Sentry in `backend/app/__init__.py`
- [ ] Wrap all service/controller errors with Sentry capture
- [ ] Test error reporting in dev

### PHASE 5 (DI)
- [ ] Create `backend/app/di.py` container
- [ ] Inject repos into services
- [ ] Inject services into controllers
- [ ] Update routes to use container
- [ ] Add test fixtures for container

### PHASE 6 (Automated Test Alignment)
- [ ] Review AUTOMATED_TESTS.md
- [ ] Implement 18 missing endpoints
- [ ] Test against evaluator spec
- [ ] Verify all response schemas match

---

## Revised BFRI After Improvements

**Projected Score: +8** (SAFE)

| Dimension | Before | After |
|-----------|--------|-------|
| **Architectural Fit** | 2 | 5 |
| **Testability** | 2 | 5 |
| **Business Logic Complexity** | 3 | 3 |
| **Data Risk** | 2 | 1 |
| **Operational Risk** | 1 | 4 |

**(5 + 5) − (3 + 1 + 1) = +5 (SAFE)**

---

## Quick Start: Implement Phase 1 (1 hour)

```bash
# 1. Create base controller
touch backend/app/controllers/__init__.py backend/app/controllers/base_controller.py

# 2. Update routes to use controllers
# 3. Add error handler middleware
# 4. Test with existing endpoints
```

After Phase 1, you unlock Phases 2–6 safely.

---

## Risk Mitigation Strategy

**Current:** Manual validation, no error tracking, tight coupling  
**Danger:** Production bugs in dark; hard to debug; fragile

**With Improvements:**
- ✅ Centralized validation (Pydantic)
- ✅ Full error visibility (Sentry)
- ✅ Testable architecture (DI + repos)
- ✅ Compliant with evaluator spec (endpoints + schemas)

---

## Timeline Estimate

| Phase | Effort | Blocker? |
|-------|--------|----------|
| 1: Controllers | 2–3 hours | No (parallel work) |
| 2: Repositories | 2–3 hours | No (after phase 1) |
| 3: Schema Validation | 1–2 hours | No (parallel) |
| 4: Sentry | 1 hour | No (parallel) |
| 5: DI | 1–2 hours | No (after phases 1–2) |
| 6: Automated Tests | 4–6 hours | **YES** (blocking) |

**Total:** ~15–20 hours for production-grade refactor  
**Minimum MVP:** Phase 1 + Phase 6 (~8 hours) to pass evaluator tests

---

## Appendix: Code Examples

### Before (Anti-pattern)

```python
@api_bp.post("/links")
def create_short_link():
    payload = request.get_json(silent=True) or {}
    # ❌ Manual validation
    if not payload.get("url"):
        return jsonify(error="validation_error"), 400
    # ❌ No Sentry
    # ❌ Direct to service (no controller)
    short_url = _service().create_short_url(...)
    return jsonify(short_url), 201
```

### After (Production-pattern)

```python
@api_bp.post("/links")
def create_short_link(req, res):  # Controller handles
    return container.url_controller.create_short_link(req, res)

# In URLController
class URLController(BaseController):
    def create_short_link(self, req, res):
        try:
            # ✅ Schema-based validation
            schema = CreateShortLinkSchema(**req.get_json())
            # ✅ Service via DI
            short_url = self.url_service.create_short_url(
                original_url=schema.url,
                custom_alias=schema.custom_alias
            )
            # ✅ Consistent response
            return self.handle_success(res, short_url, 201)
        except ValidationError as e:
            # ✅ Sentry tracking
            return self.handle_error(e, res, "create_short_link")
```

---

## Definition of Done

Backend is production-ready when:

- [ ] BFRI ≥ +5
- [ ] All 18 endpoints implemented
- [ ] 100% schema validation (Pydantic)
- [ ] All errors logged to Sentry
- [ ] Unit tests for services/repos (80%+ coverage)
- [ ] Integration tests for routes
- [ ] No anti-patterns present
- [ ] Pass evaluator automated tests
