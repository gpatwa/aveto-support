# Fix round: QA Q1 and Q2

## Q1 client preflight restored
Field error only, no card, no fetch, focus to #q (ruling by Orchestrator: main's copy collides with a pin in test_page_cards.py).
New copy for END_REVIEW:
- empty: "Enter a question before you press Ask."
- over 500 characters: "Shorten your question to 500 characters or fewer."
Server cards for empty/too long stay for no-JS.

## Q2 waiting copy
- Stage 1: "Your question has been sent." (dropped "usually takes a few seconds", also unrecorded)
- Stage 2: "This is taking longer than usual. Please keep this page open."
- Stage 3 unchanged (states only the elapsed time the counter shows).

## Fail-first
`test_script_checks_question_length_before_sending` against the unfixed file:
`AssertionError: assert ('q.value.trim()' in ', function (e) {... if (busy) { return; } busy = true; ...showWaiting(); ')` -> 1 failed.
