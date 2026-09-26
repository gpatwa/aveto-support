# Aveto Support

A support agent for [Aveto](https://aveto.dev) — built **by Aveto, in public**.

It answers questions about Aveto from Aveto's own documentation and drafts
replies to GitHub issues and Discussions. **It never posts on its own:** every
reply is approved by a person first.

## Why this repo exists

This is Aveto's reference app. Its job is to show the pipeline building real
software — a real stack, a real deploy, a real model in a shipped feature —
where anyone can read how it was built. Every slice's intent, specs, QA
evidence, security findings and approvals are committed under `runs/`.

The plan, and the bar it has to clear, is T22 in the playbook's
[backlog](https://github.com/gpatwa/agentic-sdlc-playbook/blob/main/docs/BACKLOG.md).

## How it works (as designed)

1. **Classify** the question — plain rules first, a model only when they can't.
2. **Retrieve** the relevant docs — plain code.
3. **Draft** a grounded reply — model one.
4. **Check** the draft against its sources — a separate, cheaper model that did
   not write it. Unsupported claims are removed or the question is escalated.
5. **A person approves** before anything is posted.

## Status

**Not built yet.** This repo holds the installed Aveto pack and nothing else.
The first slice sets up the stack and ships the retrieval step in plain code,
before any model is wired in.
