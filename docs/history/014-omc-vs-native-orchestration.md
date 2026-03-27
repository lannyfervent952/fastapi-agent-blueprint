# 014. OMC vs Native Orchestration Decision

- Status: Pending
- Date: 2026-03-24
- Related Documents: None

## Background

The project has 11 domain skills + Serena + settings.json hooks established,
but an **orchestration layer** (multi-agent coordination, autonomous execution, model routing) is absent.

There are two options to fill this gap:
1. **OMC (Oh My ClaudeCode)** adoption -- a third-party orchestration wrapper
2. **Native** -- Claude Code's built-in Plugin system + `/team` utilization

## Problem

The project is currently operational without an orchestration layer, but limitations are anticipated in these scenarios:
- Simultaneous refactoring across 3+ domains
- Automatic decomposition and parallel execution of complex tasks
- Need for a standard interface when porting to production projects

## Alternatives Considered

### Option A: Thin OMC Adoption

Delegate only orchestration to OMC while keeping existing domain skills.

**Advantages:**
- `/autopilot`, `/team`, `/ultrapilot` immediately available (zero-config)
- 28 predefined agents (executor, debugger, designer, etc.)
- Automatic model tier routing (Haiku/Sonnet/Opus)
- Multi-provider (`omc ask codex/gemini`)
- Community standard interface -> reduced learning curve when moving between projects

**Disadvantages:**
- External npm dependency (`npm install -g oh-my-claudecode`)
- Risk of OMC's autonomous agents violating architecture absolute-prohibition rules
- Context window overhead from 28 agent definitions
- Dependency on OMC maintainer (compatibility risk with Claude Code updates)
- Risk of skill accumulation + keyword conflicts from Learner (auto skill suggestion)

### Option B: Native Plugin System + /team

Build commands/agents/hooks using Claude Code's official Plugin system.

**Advantages:**
- Anthropic official -- long-term stability guaranteed
- No external dependencies (directory drop-in)
- Existing 11 skills are fully compatible
- Minimal context overhead (define only what's needed)
- `/team` command is already built-in (multi-agent coordination)

**Disadvantages:**
- autopilot, model tiering, etc. must be implemented manually
- Not a community standard -> structure may vary between projects
- Higher initial setup cost than OMC

### Option C: Full OMC Adoption

Migrate existing skills to OMC format and fully adopt the Conductor model.

**Disadvantages outweigh Option A, so this was eliminated early:**
- Migration cost for existing 11 skills
- Complete dependency on OMC
- Full adoption is risky when team OMC proficiency is at zero

## First Discussion (cross-session-briefing session)

**Conclusion: Option B selected**

Premises at the time:
- 11 skills + Serena + hooks already cover OMC features more precisely
- Team OMC proficiency is 0, conservative team culture
- No tasks currently require multi-agent coordination

Learning curve analysis:

| What needs to be learned | Weight | Does OMC solve it? |
|---|---|---|
| DDD 4-layer rules, absolute prohibitions | 30% | No |
| Conversion patterns (model_validate, model_dump) | 15% | No |
| Domain-specific knowledge | 25% | No |
| Skill contents (what each skill does) | 20% | No |
| How to invoke skills | 5% | Yes |
| Orchestration usage | 5% | Yes |

OMC only reduces ~10% of the learning curve, and the core 90% is addressed by the `/onboarding` skill.

Agreed escalation path:
```
Single agent -> Agent Teams -> (if needed) OMC
```

## Second Discussion (2026-03-24, this session)

### Background for Re-evaluation

Premises from the first discussion changed:
- hooks are **still not configured**, Agent Teams are also **not configured**
- The orchestration layer is effectively **empty**
- A cost comparison between building it directly vs. layering OMC on top is needed

### context7 Investigation Results (new findings)

**Claude Code Native Plugin System Confirmed:**

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Metadata
├── commands/                 # Slash commands (*.md)
├── agents/                   # Specialized agents (*.md)
├── skills/                   # Skills (SKILL.md)
├── hooks/                    # Event handlers (hooks.json)
├── .mcp.json                 # MCP tool configuration
└── README.md
```

- Claude Code **already has** a built-in `/team` command (native team agents with built-in coordination)
- The Plugin system has the **same structure** as OMC (commands/agents/skills/hooks)
- OMC documentation directly states: "native '/team' utilizes Claude Code native team agents"

**OMC's actual differentiators (narrowed down):**

| Feature | Claude Code Built-in | OMC Additional |
|---|---|---|
| Multi-agent | `/team` (built-in) | `/omc-teams` (tmux external workers) |
| Skill system | SKILL.md (built-in) | Same format |
| Agent definitions | `agents/*.md` (Plugin) | 28 predefined |
| Autonomous execution | Write custom command | `/autopilot`, `/ultrapilot` immediately available |
| Model routing | Manual specification | Automatic tiering |
| Multi-provider | N/A | `omc ask codex/gemini` |

**Benchmark scores:**
- Claude Code Plugin: 80.85
- OMC: 75.44
- Claude Code Tresor (alternative plugin pack): 78.65

### Key Insights

1. **Domain specialization is handled by Skills** -- whether OMC or native, domain skills must be written directly regardless
2. **OMC's added value is orchestration convenience** -- autopilot, model tiering, 28 agents
3. **Claude Code Plugin is converging in the same direction as OMC** -- with Anthropic official support
4. **Built-in `/team` + Plugin have not been tried yet** -- evaluating built-in capabilities should come before OMC adoption
5. **Skill formats are compatible** -- starting native means low switching cost to OMC later

### Arguments for OMC Adoption (added in second discussion)

- It is true that OMC is more convenient than building built-in capabilities yourself
- If someone familiar with OMC joins the project, orchestration is immediately usable
- Converging toward a community standard -> freedom of movement between projects

### Arguments for Native Selection (organized in second discussion)

- "Adopting an external tool without even trying the built-in features is a decision made without evaluation"
- Anthropic's official Plugin system is converging in the same direction -> more stable long-term
- OMC can always be added later, but removing it after adoption is difficult
- Context window savings (28 agent definitions not loaded)

## Decision

**Pending -- Undecided**

The escalation path is maintained:
```
Single agent (current)
  -> /team (built-in) + Plugin system evaluation
  -> If insufficient: OMC adoption
  -> Trigger: Confirmed limitations of built-in features during simultaneous work across 3+ domains
```

## Future Considerations

1. Evaluate Claude Code's built-in `/team` + Plugin system in actual work
2. Document "specific cases where built-in features fell short" during the evaluation period
3. Revisit OMC adoption if cases accumulate; otherwise, confirm Option B
