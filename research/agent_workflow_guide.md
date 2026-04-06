# Agent Workflow Guide: Multi-Agent Best Practices for Claude Code

> Researched April 2026. Based on official Anthropic docs, community guides, and practical testing.

---

## Table of Contents

1. [How Agent Teams Work](#1-how-agent-teams-work)
2. [Subagents vs Agent Teams](#2-subagents-vs-agent-teams)
3. [In-Process vs Tmux Display Modes](#3-in-process-vs-tmux-display-modes)
4. [Communication: SendMessage and Its Limits](#4-communication-sendmessage-and-its-limits)
5. [Coordination Patterns](#5-coordination-patterns)
6. [Known Limitations](#6-known-limitations)
7. [Preventing Agent Failure Modes](#7-preventing-agent-failure-modes)
8. [Best Practices](#8-best-practices)
9. [Recommendations for Battlecode Development](#9-recommendations-for-battlecode-development)

---

## 1. How Agent Teams Work

Agent Teams (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) let you run 2-16 Claude Code sessions coordinated by a single team lead. Available since v2.1.32 (February 2026).

### Core Components

| Component     | Role                                                                 |
|:------------- |:---------------------------------------------------------------------|
| **Team Lead** | Main Claude Code session. Creates team, spawns teammates, coordinates |
| **Teammates** | Independent Claude Code instances, each with own context window       |
| **Task List** | Shared list at `~/.claude/tasks/{team-name}/` with dependency tracking |
| **Mailbox**   | Peer-to-peer messaging via `SendMessage` tool                        |

### Seven Primitives

`TeamCreate`, `TaskCreate`, `TaskUpdate`, `TaskList`, `Task` (with team_name), `SendMessage`, `TeamDelete` -- all file-based on disk under `~/.claude/teams/` and `~/.claude/tasks/`.

### Task Lifecycle

Tasks move through three states: **pending -> in_progress -> completed**. Tasks can declare dependencies on other tasks. A pending task with unresolved dependencies cannot be claimed until those dependencies complete. File locking prevents race conditions when multiple teammates try to claim the same task.

### Context at Spawn

Teammates load the same project context as a regular session: `CLAUDE.md`, MCP servers, and skills. They do NOT inherit the lead's conversation history. Task-specific details must be included in the spawn prompt.

---

## 2. Subagents vs Agent Teams

These are fundamentally different architectures. Choose based on whether workers need to talk to each other.

| Feature            | Subagents                                    | Agent Teams                                   |
|:-------------------|:---------------------------------------------|:----------------------------------------------|
| **Context**        | Own window; results return to caller         | Own window; fully independent                 |
| **Communication**  | Report back to parent ONLY                   | Peer-to-peer messaging between any teammates  |
| **Coordination**   | Parent manages all work                      | Shared task list with self-coordination       |
| **Cost**           | Lower (results summarized back)              | Higher (each teammate = separate instance)    |
| **Lifetime**       | Short-lived, terminate after task            | Persistent, stay alive across multiple tasks  |
| **Best for**       | Focused tasks where only result matters      | Complex work needing discussion/collaboration |

### Key Constraint: Subagents CANNOT Message Each Other

Subagents operate in a strict hub-and-spoke pattern: each worker reports results back to the parent and then terminates. Sibling subagents cannot talk to each other directly. This is NOT a bug -- it is the design.

Only Agent Teams support peer-to-peer messaging via `SendMessage`.

---

## 3. In-Process vs Tmux Display Modes

### In-Process Mode (Default)

- All teammates run inside your main terminal
- Navigate with `Shift+Up/Down` to cycle between teammates
- Press `Enter` to view a teammate's session, `Escape` to interrupt
- `Ctrl+T` to toggle the task list
- Works in ANY terminal, no extra setup
- **Limitation:** `/resume` and `/rewind` do NOT restore in-process teammates

### Split Pane Mode (tmux/iTerm2)

- Each teammate gets its own pane
- See all agents working simultaneously
- Recommended for 3+ teammates
- **Requirements:** tmux or iTerm2 with `it2` CLI
- **NOT supported in:** VS Code integrated terminal, Windows Terminal, Ghostty

### Configuration

```json
// ~/.claude.json
{
  "teammateMode": "in-process"  // or "tmux" or "auto" (default)
}
```

Force in-process for a single session: `claude --teammate-mode in-process`

### Windows Limitation

Split-pane mode (tmux) is not natively available on Windows. Use in-process mode, or run inside WSL if you need split panes.

---

## 4. Communication: SendMessage and Its Limits

### How It Works

`SendMessage` allows any teammate to message any other teammate by name, or broadcast to all with `to: "*"`. Messages arrive automatically -- no polling required.

### Critical Limitations

1. **Subagents cannot use SendMessage to message other subagents.** Communication is strictly parent-child in the subagent model.

2. **SDK/In-Process Mode Delivery Issue:** When using Agent Teams with `ClaudeSDKClient`, teammate messages sent via `SendMessage` may not be received by the lead because the SDK session terminates before the next turn. In SDK mode, the session ends when `receive_response()` yields a `ResultMessage` -- there is no "next turn" to receive messages.

3. **No shared memory:** Agents don't share their full context window. Only explicit messages and the shared task list provide coordination.

4. **Broadcast costs scale linearly** with team size -- use sparingly.

### Practical Impact

If you are running agents via the Claude Agent SDK (Python) or in certain in-process configurations, `SendMessage` delivery between teammates may be unreliable. This is a known issue (see GitHub issue anthropics/claude-agent-sdk-python#577).

**Workaround:** Use the shared task list as the primary coordination mechanism. Write findings to files on disk. Use messages only for urgent coordination that cannot be conveyed through task descriptions.

---

## 5. Coordination Patterns

### Pattern 1: Hub-and-Spoke (Lead Orchestrates)

```
Lead assigns tasks -> Teammates work independently -> Report results -> Lead synthesizes
```

Best for: Research, code review, independent implementations.

The lead creates tasks, assigns them, and waits for results. Teammates work in isolation and report back. This is the simplest and most reliable pattern.

**When to use:** Most of the time. Start here.

### Pattern 2: Peer-to-Peer (Teammates Collaborate)

```
Lead spawns team -> Teammates claim tasks and message each other -> Lead synthesizes
```

Best for: Debugging with competing hypotheses, design discussions, adversarial review.

Teammates can challenge each other's findings, share discoveries, and build on each other's work. Requires Agent Teams (not subagents).

**When to use:** When you need agents to argue, debate, or cross-validate.

### Pattern 3: Wave-Based Execution

```
Wave 1: Independent tasks in parallel
  -> Wait for completion
Wave 2: Dependent tasks that use Wave 1 results
  -> Wait for completion
Lead: Synthesize all results
```

Best for: Complex features with dependency chains.

Explicitly encode dependencies in task descriptions. The task system auto-unblocks dependent tasks when prerequisites complete.

**When to use:** When work has clear phases (research -> design -> implement -> test).

### Pattern 4: Plan-Then-Execute

```
Phase 1: Lead + cheap model (Sonnet) plans the work
Phase 2: Lead spawns team with detailed task specs for parallel execution
```

Best for: Expensive work where direction matters.

"Start with plan mode (cheap), then hand the plan to a team for parallel execution (expensive but fast)." This checkpoint prevents costly course corrections mid-swarm.

**When to use:** Always, for any non-trivial team task. Planning is cheap; execution is expensive.

### Pattern 5: Adversarial Debate

```
Agent A: Proposes solution
Agent B: Tries to break it (devil's advocate)
Agent C: Synthesizes, makes final call
```

Best for: Preventing confirmation bias, finding edge cases, strategy decisions.

The three-agent configuration (two opposing perspectives + neutral synthesizer) is the most practical for production. Force independent responses in Round 1 before any cross-agent visibility.

**When to use:** Strategy decisions, architecture choices, debugging where root cause is unclear.

### Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails |
|:-------------|:-------------|
| Jumping to teams without planning | Cost spirals; one wrong-direction team = 500k+ wasted tokens |
| Multiple agents editing same file | Overwrites, merge conflicts, corrupted state |
| Too many agents for simple tasks | Coordination overhead > benefit |
| Letting team run unattended | Agents go off rails, waste tokens, compound errors |
| Sequential work with teams | Teams add overhead; a single session is faster for serial work |

---

## 6. Known Limitations

### Architectural Limits

- **One team per session:** Lead can only manage one team at a time
- **No nested teams:** Teammates cannot spawn their own teams
- **Lead is fixed:** Cannot promote a teammate to lead
- **No session resumption:** `/resume` and `/rewind` do not restore in-process teammates. After resuming, the lead may try to message teammates that no longer exist
- **Permissions propagate:** All teammates start with the lead's permission mode; cannot set per-teammate modes at spawn time

### Coordination Limits

- **Task status lag:** Teammates sometimes fail to mark tasks as completed, which blocks dependent tasks. Workaround: manually check and update, or tell the lead to nudge the teammate
- **Shutdown is slow:** Teammates finish their current request/tool call before shutting down
- **Context isolation:** No shared memory. Teammates must communicate explicitly
- **No project-level team config:** A file like `.claude/teams/teams.json` in your project is NOT recognized; Claude treats it as an ordinary file

### Cost Limits

- Token costs scale linearly with teammates
- Three teammates costs ~440k tokens vs ~200k for solo work (2.2x overhead)
- Each teammate is a full Claude context window
- Broadcast messages multiply cost by team size

---

## 7. Preventing Agent Failure Modes

### Problem: "Agent Always Thinks It's Right"

**Symptom:** Agent commits to first hypothesis, ignores contradicting evidence, declares success prematurely.

**Solutions:**

1. **Adversarial debate structure:** Spawn agents with explicitly opposing mandates. One proposes, one must find flaws. "You are skeptical by default. Identify what's missing, wrong, or risky in any proposal."

2. **Independent parallel investigation:** Run Round 1 in strict isolation -- no cross-agent visibility. If agents see each other's responses too early, they anchor on the first answer.

3. **Dedicated devil's advocate:** One agent whose sole job is to find flaws. Give it the system prompt: "You disagree by default. Only agree when forced to by evidence."

4. **Plan approval gates:** Require teammates to plan before implementing. The lead reviews and either approves or rejects with feedback.

5. **Quality gate hooks:** Use `TaskCompleted` hooks to run automated checks before marking tasks done.

### Problem: Confirmation Bias in Reviews

**Symptom:** Agent finds one issue type and anchors entire review around it.

**Solutions:**

1. **Split review by domain:** One agent per concern (security, performance, test coverage). Each starts clean without knowing what others found.

2. **Synthesize after all complete:** Lead collects all independent findings and produces holistic picture. Do NOT let reviewers see each other's work until after Round 1.

### Problem: Tunnel Vision in Debugging

**Symptom:** Agent latches onto first plausible explanation and stops investigating.

**Solutions:**

1. **Competing hypotheses:** Spawn 3-5 agents, each assigned a different theory. Have them actively try to disprove each other.

2. **Adversarial framing:** "Each one's job is not only to investigate its own theory but to challenge the others'." The theory that survives falsification attempts is much more likely to be correct.

### Problem: Agent Does Everything Itself Instead of Delegating

**Symptom:** Lead implements tasks instead of assigning to teammates.

**Solutions:**

1. **Delegate mode:** Restricts the lead to coordination only -- it cannot write code, run tests, or do implementation work.

2. **Explicit instruction:** "Wait for your teammates to complete their tasks before proceeding."

3. **Tiered model selection:** "The lead runs on Opus, teammates on Sonnet." This naturally forces the lead to delegate (cheaper execution on teammates).

### Problem: Agents Quickly Agree ("Good point, I agree")

**Symptom:** Debate collapses to one round of agreement.

**Root cause:** Insufficient differentiation in system prompts and/or early visibility to other responses.

**Solutions:**

1. Rewrite prompts with genuinely different mandates and values
2. Add explicit disagreement instructions: "challenge reasoning by default"
3. Run Round 1 in strict parallel isolation
4. Use adversarial framing that makes agreement require evidence, not assumption
5. Three well-differentiated agents outperform five similar ones

---

## 8. Best Practices

### Team Size

- **Start with 3-5 teammates** for most workflows
- **5-6 tasks per teammate** keeps everyone productive
- If you have 15 independent tasks, 3 teammates is a good starting point
- Three focused teammates often outperform five scattered ones
- Scale up only when work genuinely benefits from parallel execution

### Task Design

- **Too small:** Coordination overhead exceeds benefit
- **Too large:** Teammates work too long without check-ins, risking wasted effort
- **Just right:** Self-contained units that produce a clear deliverable (a function, a test file, a review)

### File Conflict Prevention

- **Break work by file ownership:** Each teammate owns a different set of files
- **Interface-first:** Define contracts before parallel implementation
- **Single-writer rule:** One agent writes shared files, others read
- **Git worktrees:** For heavier isolation, use `isolation: worktree` in subagent definitions -- each agent gets its own checkout

### Context Management

- Include task-specific details in the spawn prompt (teammates don't get lead's history)
- Use `CLAUDE.md` for project-wide context (all teammates load it automatically)
- Write intermediate results to files on disk for teammates to read
- Keep messages concise -- they consume context window space

### Cost Control

- Use plan-then-execute: plan with Sonnet, execute with team
- Assign different models per teammate: "The debugger runs on Opus, the UI agent on Sonnet"
- Avoid broadcast messages (cost scales linearly with team size)
- For routine tasks, a single session is more cost-effective
- Monitor token usage and shut down idle teammates promptly

### Monitoring

- Check in on teammates' progress regularly
- Redirect approaches that aren't working early
- Don't set it and forget it -- unmonitored agents waste tokens
- Use split-pane mode (if available) for easier oversight with 3+ teammates

### Cleanup

- Always use the lead to clean up (`Clean up the team`)
- Shut down all teammates before cleanup
- Teammates should NOT run cleanup (their team context may not resolve correctly)
- Check for orphaned tmux sessions: `tmux ls` / `tmux kill-session -t <name>`

---

## 9. Recommendations for Battlecode Development

### Optimal Team Structure for Competitive Bot Development

Given our project (Python Battlecode bot, economy-focused strategy, qualifier April 20), here are specific recommendations:

### Recommended Roles (3-4 agents)

| Role | Responsibilities | Model |
|:-----|:-----------------|:------|
| **Team Lead** | Coordination, task assignment, synthesis, strategic decisions | Opus |
| **Implementer** | Writes bot code, implements features, fixes bugs | Opus or Sonnet |
| **Analyst** | Watches replays, studies opponents, analyzes match data, proposes strategy adjustments | Sonnet |
| **Tester/Reviewer** | Runs `cambc test-run`, validates no TLE, reviews code for edge cases and CPU safety | Sonnet |

### When to Use Agent Teams vs Single Agent

**Use a single agent for:**
- Implementing a specific feature (e.g., "add splitter-based ammo delivery")
- Fixing a specific bug
- Writing a single module
- Sequential refactoring within one file

**Use agent teams for:**
- Full-phase implementation (e.g., "implement Phase 4: Offense + Adaptation")
- Parallel testing across map categories (small/medium/large/choke/open)
- Strategy review: one agent proposes strategy, another plays devil's advocate
- Post-match analysis: one agent reviews replays while another implements fixes

### Workflow for Our Use Case

```
1. PLAN (single agent, cheap)
   - Read ROADMAP.md, identify next phase
   - Break into independent tasks
   - Identify file ownership boundaries

2. EXECUTE (agent team, parallel)
   - Implementer: writes the code (owns bots/buzzing/*.py)
   - Tester: runs cambc test-run on each map category
   - Analyst: reviews strategy assumptions against latest ladder results

3. VALIDATE (agent team, adversarial)
   - Implementer: "this approach is optimal because..."
   - Reviewer: "here's why it might fail: ..."
   - Lead: synthesizes, makes call

4. SUBMIT (single agent)
   - cambc submit, monitor first 10 ladder matches
```

### File Ownership Boundaries

To prevent conflicts in our codebase:

```
roles/core_brain.py        -> ONE agent at a time
roles/economy_builder.py   -> ONE agent at a time  
roles/military_builder.py  -> ONE agent at a time
roles/scout.py             -> ONE agent at a time
roles/attacker.py          -> ONE agent at a time
roles/turret_brain.py      -> ONE agent at a time
systems/markers.py         -> ONE agent at a time
systems/pathfinding.py     -> ONE agent at a time
systems/symmetry.py        -> ONE agent at a time
constants.py               -> Shared, but only lead edits
main.py                    -> Shared, but only lead edits
```

Never assign two agents to the same file. If a feature spans files, assign the entire feature to one implementer.

### Preventing Tunnel Vision in Strategy

The biggest risk in competitive bot development is tunnel vision: optimizing for one strategy without testing alternatives.

**Counter-measures:**

1. **Weekly adversarial review:** Spawn a devil's advocate agent that must argue against our current strategy and propose alternatives

2. **Parallel hypothesis testing:** When debugging a loss, spawn 3 agents with different theories (economy problem? defense problem? timing problem?)

3. **Replay analysis with fresh eyes:** Give an analyst agent the replay data WITHOUT telling it our current strategy. Let it identify issues independently

4. **Parameter sweep agent:** One agent systematically tests different constants (builder count, turret timing, attack round) while the main implementer works on features

### Cost-Effective Usage

For our budget constraints:

- Use single agents for 80% of work (implementation, bug fixes, refactoring)
- Reserve agent teams for phase transitions, strategy reviews, and parallel testing
- Use Sonnet for testing/analysis teammates (cheaper, still capable)
- Plan before spawning teams (planning is cheap, execution is expensive)
- Shut down agents when idle -- don't let them sit consuming tokens

---

## Summary: Decision Checklist

Before spawning an agent team, answer these questions:

1. **Can the work be parallelized?** If tasks are sequential, use a single agent.
2. **Do workers need to communicate?** If not, subagents are cheaper than teams.
3. **Is the work complex enough?** Coordination overhead must be justified by speed gain.
4. **Have you planned first?** Never jump to teams without a plan. One wrong-direction team wastes 500k+ tokens.
5. **Are file boundaries clear?** Two agents on one file = guaranteed problems.
6. **Is someone watching?** Unmonitored teams drift and waste resources.

If all answers are favorable, create a team with 3-5 teammates, 5-6 tasks each, clear file ownership, and plan approval for risky changes.

---

## Sources

- [Official Agent Teams Documentation](https://code.claude.com/docs/en/agent-teams)
- [Addy Osmani: Claude Code Swarms](https://addyosmani.com/blog/claude-code-agent-teams/)
- [30 Tips for Claude Code Agent Teams](https://getpushtoprod.substack.com/p/30-tips-for-claude-code-agent-teams)
- [From Tasks to Swarms: Agent Teams in Claude Code](https://alexop.dev/posts/from-tasks-to-swarms-agent-teams-in-claude-code/)
- [You Probably Don't Need Claude Agent Teams](https://www.builder.io/blog/claude-agent-teams-explained-what-it-is-and-how-to-actually-use-it)
- [Agent Chat Rooms: Multi-Agent Debate](https://www.mindstudio.ai/blog/agent-chat-rooms-multi-agent-debate-claude-code)
- [GitHub Issue: SendMessage in SDK mode](https://github.com/anthropics/claude-agent-sdk-python/issues/577)
- [Claude Code Subagents Docs](https://code.claude.com/docs/en/sub-agents)
- [Git Worktrees for Parallel Agents](https://engineering.intility.com/article/agent-teams-or-how-i-learned-to-stop-worrying-about-merge-conflicts-and-love-git-worktrees)
- [LaoZhang AI: Claude Code Agent Teams Guide](https://blog.laozhang.ai/en/posts/claude-code-agent-teams)
