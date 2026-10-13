# Ticket template

Use sections that contribute to the ticket; omit empty optional sections.

```markdown
# <Verb + specific outcome>

## Problem and desired behavior
<Concrete trigger, current behavior, and expected result.>

## Scope
- <Owned surface and included behavior>

## Out of scope
- <Related work explicitly excluded>

## Acceptance criteria
1. Given <state>, when <action>, then <observable result>.
2. <Relevant invalid input/error/default behavior>.
3. <Existing behavior that must still work>.

## Verification
- <Project command and meaningful assertion/scenario>

## Dependencies and contract
<Linked prerequisite, agreed input/output contract, or None.>

## Implementation pointers
<Relevant paths and constraints; omit unnecessary detail.>

## Open decisions / assumptions
<Only unresolved decisions and labeled assumptions.>
```

For bugs include reproduction and expected/actual behavior. For parallel tickets make ownership disjoint and include the same agreed API contract or a link to its canonical source. Do not include secrets or private payloads in published examples.
