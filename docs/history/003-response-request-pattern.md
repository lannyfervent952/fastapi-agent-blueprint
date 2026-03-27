# 003. Response/Request Pattern Design

- Status: Accepted
- Date: 2025-03-19 ~ 2025-09-09
- Related issues: #1, #5, #22
- Related PRs: #2, #24
- Related commits: `cdcbf59`, `42fc118`, `204e325`, `2d4c6fe`, `fd191b3`, `3b69806`, `a05ced4`

## Background

The API response format is a contract with the frontend.
In the early stages of the project, both single-item and multi-item query APIs existed,
and clients needed to be able to control overhead directly for multi-item queries.
Since the frontend could provide a pagination UI, the server needed to include pagination information in the response.

Additionally, error response formats were not standardized,
making it difficult for clients to distinguish between intentional errors and unexpected errors.

## Problem

### 1. Scattered Pagination Responses (#1)

Initially, `PaginationResponse` was created as a separate class,
but this meant that regular responses and pagination responses were separated, resulting in different response structures per API.

```python
# Initial structure (commit cdcbf59) — separate class
class PaginationResponse(BaseModel):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    next_page: int
    previous_page: int
```

### 2. Response Format Responsibility Location (#1)

Response format logic was in `base_usecase`,
but the use case is a layer responsible for business logic, not for determining response formats.

### 3. Mixed Return Type and response_model (#5)

FastAPI's `response_model` parameter and function return type annotations were mixed,
causing discrepancies between the response schema displayed in Swagger documentation and the actual returned data.
Additionally, the `data` field was of type `Any`, providing no type safety.

### 4. Non-Standardized Error Responses (#22)

Error response formats were not standardized,
so error response schemas were not displayed in Swagger documentation,
and frontend developers could not write error handling logic consistently.

## Decision

### 1. Integrate PaginationInfo into BaseResponse as Optional

Since not all APIs need pagination, it was integrated as `Optional[PaginationInfo]`.

```python
# After integration (commit 42fc118)
class PaginationInfo(BaseModel):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    next_page: int
    previous_page: int

class BaseResponse(ABC, BaseModel):
    success: bool = True
    message: str = "Request processed successfully"
    data: Optional[Any] = None
    pagination: Optional[PaginationInfo] = None
```

### 2. Move Response Format Responsibility to Controller (Router)

Since response formatting is an interface concern, the controller (later renamed to router) was made responsible (commit `204e325`).
The use case returns only business data, and wrapping it in a response format became the router's responsibility.

### 3. Separate SuccessResponse and ErrorResponse

Success responses don't need `error_code` or `error_details`,
and error responses don't need `data` or `pagination`.
These were separated so each response type contains only the fields it needs.

```python
# Current structure
class SuccessResponse(ApiConfig, Generic[ReturnType]):
    success: bool = True
    message: str = "Request processed successfully"
    data: ReturnType | None = None
    pagination: PaginationInfo | None = None

class ErrorResponse(ApiConfig):
    success: bool = False
    message: str = "Request failed"
    error_code: str | None = None
    error_details: dict | None = None
```

### 4. Register Global Error Response Models

Common error responses (400/401/403/404/500) were registered in the FastAPI app settings
so that error response schemas are automatically displayed in Swagger documentation (commit `a05ced4`).

```python
# src/app.py
app = FastAPI(
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Authentication required or token mismatch"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Resource not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
```

Error response generation is handled by ExceptionMiddleware,
which uniformly converts both intentional errors (business exceptions) and uncaught errors (system exceptions)
into the `ErrorResponse` format.

## Rationale

| Decision | Reason |
|----------|--------|
| PaginationInfo Optional integration | Unifies response structure for single/multi-item queries. Clients can branch based on the presence of the pagination field |
| Response format -> Controller | Response formatting is an interface concern. Ensures use case reusability (shared between API/Worker) |
| Success/Error response separation | Each response contains only necessary fields for clear semantics. Errors have no data, successes have no error_code |
| Global error response registration | Swagger auto-documentation lets frontend developers immediately check error formats |
| data field Generic typing | Changed from `Any` to `ReturnType` for improved type safety and Swagger schema accuracy |

## Follow-up

- Changing the `data` field from `Any` to `ReturnType` Generic type made DTO types display accurately in Swagger
- This later intersected with the DTO/Entity responsibility redefinition (-> [004](004-dto-entity-responsibility.md)), where response DTOs were separated from domain Entities
