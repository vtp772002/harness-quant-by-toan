# 0001 — Judgment Boundaries: Stop Before an Open Choice

- Date: 2026-09-13. Status: accepted.
- Inspired by harness-by-victoria (repository authority and stop-before-mutation).

## Context
Agents tend to invent product policy when a request leaves an important choice
open, for example adding rate limiting without a quota or choosing a universe
without defining survivorship.

## Decision
Before every mutation, the agent must name the authority that permits it.
When a material choice remains open and would change observable behavior, stop
before editing, present the concrete options and consequences, and wait for the
human. Configurable defaults are not authority.

## Consequences
- A PR that invents policy without authority is rejected in review; technical
  debate does not substitute for the missing decision.
- The `encode-invariant` skill is the only approved path for turning a rule into
  a guard; see decision `0002`.
