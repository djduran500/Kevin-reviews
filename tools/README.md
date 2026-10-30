# Update tools

- `render_feedback.py cards.json DJ/img` — renders "Client feedback" cards (941px WebP) in the site's style.
- `add_feedback.py DJ cards.json` — adds those cards to `DJ/index.html`, re-sorts newest first, rebuilds year sections, filter bar and summary line.

cards.json: `[{"file":"2025-10-27_Feedback_Kerri-and-Peter.webp","date":"2025-10-27","name":"Kerri and Peter","text":"..."}]`
New DJ page: copy a feedback-only page (e.g. `tom/index.html`), change title/h1, empty `<main>`, then run the tools. Add the DJ to the front page `index.html` with updated counts.
