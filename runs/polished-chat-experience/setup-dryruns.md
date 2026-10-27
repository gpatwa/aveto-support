# Setup phase — dry runs (2026-10-26, after Charter approval at 20:08:31Z)

The plan file is hashed in the Charter (C1.2), so results are recorded here, not in the plan.

| id | Result |
|---|---|
| C6.P | `.claude/settings.local.json` (main checkout, gitignored) holds exactly the 50 rules of C6.P (12 `Agent(<role>)`). The file existed before with 3 app-added read rules; original saved to the session scratchpad and restored after the pull request opens. Dry runs with no prompt: `uv run`, `uv sync --locked` (earlier), `git rev-list`/`merge-base`/`status`, `shasum`, `date -u`, `charter-check`, `events-verify`, `usage`, `az account show`, `az keyvault secret list`, `az containerapp show`/`revision list`, `az acr repository show-tags` (3 tags), `az bicep build` (ok), `npm install --prefix` axe, `gh pr view` (no PR yet), the browser tools. Gated, not run: `az acr build`, `az deployment group create`, `git push`, `gh pr create`. |
| C6.1 | `0 0` against `main`; packVersion 29. |
| C6.3 | 668 passed, mypy and ruff clean. |
| C6.6 | `ca-aveto-ask--0000008`, image `d067b9a95ac6`, kill switch off, prices 2000/10000; ACR holds tags `0fa04abda8ad`, `879cae23690b`, `d067b9a95ac6`. |
| C6.7 | `events-verify`: chain intact, 45 lines; one alert (seq 45: the verifier's own in-flight call, no outcome yet). |
| C6.8 | axe-core 4.10.2 installed in the scratchpad (`.../scratchpad/axe`). |
| C6.9 | A scratch dev server (outside the repo, `.../scratchpad/devserver.py`: the service on the test fakes, `127.0.0.1:8765`, plus a scratch `/__axe.js` route) answers `GET /` in the browser pane; axe ran once with tags wcag2a/2aa/21aa/22aa. **Baseline of the current page: 1 violation, `aria-prohibited-attr`, impact serious (1 node), 25 passes.** The bar C1.4.3 therefore needs the new page to fix this. |
