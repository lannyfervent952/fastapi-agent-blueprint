---
name: onboard
argument-hint: "(no arguments)"
description: |
  This skill should be used when the user asks to
  "project introduction", "getting started",
  "how does this project work", "I'm new to this project",
  or is a new team member needing orientation to the project.
---

# Interactive Onboarding for New Team Members

> **Design Principle**: This skill does not have its own architecture documentation.
> All information is read at runtime from existing sources (README.md, ADR, project-dna.md, CLAUDE.md, Serena memory, src/user/ code).
> When the structure changes, the source is updated, and onboarding automatically reflects the latest content.

## Pre-check: Collect Project State

Execute the following to understand the current project state (do not output to the user):

1. Read Serena `project_overview` memory -- tech stack and app structure
2. Read Serena `refactoring_status` memory -- confirm work in progress
3. Read Serena `architecture_conventions` memory -- current DO/DON'T rules
4. Glob `src/*/` to identify current domain list (excluding `_core`, `_apps`)
5. `git log --oneline -5` to check recent activity

## Phase 0: Welcome -- Assess Experience Level

Ask the user about their experience level:

> Welcome! Before we start the onboarding, one quick question.
>
> **How much experience do you have with Python/FastAPI?**
> - **(1) Beginner** -- Python basics, first time with FastAPI
> - **(2) Intermediate** -- FastAPI experience, first time with DDD/layered architecture
> - **(3) Advanced** -- DDD + DI Container experience, just need to understand this project's structure

After receiving the user's response, refer to the level-specific adjustment criteria in `${CLAUDE_SKILL_DIR}/references/role-tracks.md`
to adjust the depth of each Phase. Track overview:

```
=== Onboarding Track ===
Experience: {selected level}
Phase: 1(Methodology) -> 2(Project Overview) -> 3(Architecture Rules) -> 4(Data Flow) -> 5(Skills) -> 6(Next Steps)
Depth Adjustment: {adjustment summary based on level}
```

Proceed to the next Phase after user confirmation.

## Phase 1: Methodology and Architecture Evolution History

**Information Source**: `README.md`, `docs/history/` ADR files

> The purpose of this Phase is to help understand "why it was built this way."
> Before explaining rules and structure, the background must be conveyed first so the rules resonate.

### 1.1 DDD (Domain-Driven Design) Core Concepts

Explain the following:
- **Bounded Context**: Each domain has independent models and logic. In this project, `src/{domain}/` represents one Bounded Context
- **Layered Architecture**: Separating concerns so each layer can be independently replaced/tested
- **Dependency Direction**: Interface -> Application -> Domain <- Infrastructure (Domain is central, unaware of Infrastructure)

**Experience level adjustment**:
- **Beginner**: Explain each concept in detail with analogies. "Layers are like floors in a building -- the upper floor (Router) knows about the lower floor (Service), but the lower floor doesn't know about the upper floor"
- **Intermediate**: Briefly touch on concepts and move on
- **Advanced**: Skip DDD concept explanation, go directly to 1.2

### 1.2 Evolution of This Project

Reference the ADRs in `docs/history/` directory and convey in narrative form what **problem** each major decision originated from:

**Story 1: Structural Evolution**
- Read `docs/history/006-ddd-layered-architecture.md` and convey the key points
- "Originally apps/ and domains/ were separate, but code navigation was inconvenient, so we switched to per-domain flattening"
- Key takeaway: Opening just one domain folder shows all code for that feature

**Story 2: Entity -> DTO Unification**
- Read `docs/history/004-dto-entity-responsibility.md` and convey the key points
- "Entity was introduced following the DDD pattern, but since there was no business logic, its role overlapped with DTO"
- "to_entity/from_entity conversion was repeated in every handler -> removed and unified to DTO"
- Key takeaway: This is the background for the "No Entity pattern, DTO unification" rule

**Story 3: 4-Tier -> 3-Tier Hybrid**
- Read `docs/history/011-3tier-hybrid-architecture.md` and convey the key points
- "UseCase -> Service -> Repository each simply delegated to the layer below (passthrough)"
- "BaseService was restored, and UseCase is added only when needed -- transitioning to a hybrid"
- Key takeaway: This is the background for the "UseCase is optional" rule. More layers does not mean better architecture

**Story 4: Why IoC Container**
- Read `docs/history/013-why-ioc-container.md` and convey the key points
- "Inheritance implies an is-a relationship, but Service uses (has-a) Repository, not is-a"
- "FastAPI Depends() only works in Router -> cannot be reused in Worker"
- "Container connects Protocol (interface) and implementation at runtime"
- Key takeaway: This is the mechanism that enables the "No Infrastructure import in Domain" rule

### 1.3 AIDD (AI-Driven Development)

Read the **AI Pair Programming (AIDD)** section of `README.md` and explain the following:
- This project is designed for pair programming with Claude Code
- 11 Skills (slash commands) automate domain creation, API addition, architecture verification, etc.
- MCP servers (Serena, context7) support symbolic code exploration and library documentation lookup
- Skills reference project-dna.md and CLAUDE.md to automatically follow project rules

> "If you have any questions, feel free to ask. Otherwise, say 'next'."

## Phase 2: Project Overview

**Information Source**: `project-dna.md sections 0-1`, Serena `project_overview` memory

1. Read the **section 0 Project Scale** of `.claude/skills/_shared/project-dna.md`
   and explain the project's purpose and scale.

2. Show the architecture core as a diagram (keep it concise since context is already known from Phase 1):
   ```
   Basic: Router -> Service(BaseService) -> Repository(BaseRepository)
   Complex: Router -> UseCase -> Service -> Repository (when combining multiple Services)
   ```

3. Read **section 1 Domain Directory Structure** of `project-dna.md` and show the file composition of a single domain.

4. Show the current domain list and recent git activity collected during Pre-check.

5. Present the tech stack read from Serena `project_overview` memory.

**Experience level adjustment** (refer to `role-tracks.md` section 2):
- **Beginner**: Additional explanation of DI Container, Protocol, Pydantic BaseModel
- **Advanced**: Present only domain list + tech stack summary

> "If you have any questions, feel free to ask. Otherwise, say 'next'."

## Phase 3: Architecture Rules

**Information Source**: `CLAUDE.md` Absolute Prohibitions section

1. Read the **Absolute Prohibitions** section of `CLAUDE.md` and present the 4 rules.
   Since the history was already conveyed in Phase 1, connect each rule to **which story it originated from**:
   - "No Infrastructure import in Domain" <- Story 4 (IoC Container enables this)
   - "No Model exposure outside Repository" <- Story 2 (DTO handles inter-layer data transfer)
   - "No Mapper class" <- Inline conversion is sufficient (Story 2)
   - "No Entity pattern, DTO unification" <- Story 2 (ADR 004)

2. Read the **Terminology Definitions** section of `CLAUDE.md` and explain the roles and locations of Request/Response, DTO, and Model.

**Experience level adjustment**:
- **Advanced**: Just the rule list + story connections, kept concise

> "If you have any questions, feel free to ask. Otherwise, say 'next'."

## Phase 4: Data Flow Walkthrough

**Information Source**: `CLAUDE.md` Conversion Patterns section, `src/user/` live code

1. Read the **Conversion Patterns** section of `CLAUDE.md` (Write direction, Read direction) and show the overall flow.

2. Read the actual code from the `src/user/` domain live and show concrete examples:

   **Write Path (Create):**
   - Read the Request DTO with Serena `find_symbol` and show the field structure
   - Read the Router's create method and show the Request -> Service passing pattern
   - Read the Repository's insert method and show the `Model(**entity.model_dump())` conversion

   **Read Path (Query):**
   - Read the Repository's select method and show the `DTO.model_validate(model)` conversion
   - Show the Router's response return pattern

**Experience level adjustment**:
- **Advanced**: Present only the conversion pattern summary table, skip code walkthrough

> "If you have any questions, feel free to ask. Otherwise, say 'next'."

## Phase 5: Development Workflow and Skills

**Information Source**: `CLAUDE.md` Skills section, Serena `suggested_commands` memory

1. Read the **Task-specific Skills** section of `CLAUDE.md` and present the full Skills list in workflow order:
   > "When developing a new feature, use Skills in this order:"
   > Design(`/plan-feature`) -> Create(`/new-domain`, `/add-api`) -> Verify(`/review-architecture`, `/test-domain`) -> Fix(`/fix-bug`)

2. Read Serena `suggested_commands` memory and present frequently used commands (server start, tests, lint, etc.).

**Experience level adjustment**:
- **Advanced**: Present Skills list only

> "If you have any questions, feel free to ask. Otherwise, say 'next'."

## Phase 6: Personalized Next Steps

**Information Source**: `role-tracks.md` section 4 Next Step Recommendations

Read the "first 3 tasks" for the user's experience level from `${CLAUDE_SKILL_DIR}/references/role-tracks.md` section 4.

Wrap-up:
```
=== Onboarding Complete ===
Feel free to ask any additional questions at any time.

Key reference materials:
- CLAUDE.md -- Full project rules
- .claude/skills/_shared/project-dna.md -- Code pattern Reference
- docs/history/ -- Architecture Decision Records (ADR)
- src/user/ -- Reference domain implementation
```
