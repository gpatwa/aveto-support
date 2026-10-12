# Judge raw replies, batch 1 (the only place judge reasons are kept)

## r001  input sha256 6ed92cda33adb7655011e310f502a44e95f47dbe276e0f32726b2dc8f5728e23
(spawned in the background: result arrived by task notification; agent ab442e1b1746d3bb4)
```
Q1 NOT_ANSWERABLE: passages cover approval requests and approval records, but none mention Microsoft Teams or any chat channel.
```

## r002  input sha256 d92ecd033af69f76070a9f10898ad6c62404f26a23a520db9535f0cffffd1421
(agent ab21e97ded0497a9c)
```
Q1 ANSWERABLE The Tech Writer prompt and agent brief say a Tech Writer writes a doc delta from the diff and QA for each shipped slice.
```

## Driver deviations to disclose to the scorer
- Before r001 the driver ran `cat` on batch-1.txt and `ls -a .aveto-judge` via Bash (not Read, not judge-input/apply). Read-only; no key, eval file or corpus touched.
- The driver is the Orchestrator session, which also ran the earlier probe work; it is not a fresh context.

## r003  input sha256 01e660d80cf84cf4cdf000aa1ead48dab6cda9937de349efc78d8b1522d464f1  — INVALID SPAWN (driver error)
(agent acd4f4e4ee72f539d) The driver's spawn prompt was NOT verbatim: it was cut off inside passage 5a (ends "building an uninstaller would discard...") and omitted the rest of 5a, all of 5b and the `=== end Q1 ===` marker. Reply below is for that truncated payload and was NOT passed to judge-apply. Batch 1 is void from r003 on by the driver's own error (spec 5.3 / addendum 7.4).
```
Q1 ANSWERABLE Passage 1a: resume from the partial artefact; usage limit is infrastructure, not a restart.
```
