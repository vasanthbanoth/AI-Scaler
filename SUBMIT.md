# Submission copy-paste (fill after deploy)

| Form field | Your value |
|------------|------------|
| Full name | Vasanth Banoth |
| Email | thevasanthbanoth@gmail.com |
| Hours spent | _(honest, e.g. 12–20)_ |
| Voice phone | `+1...` from Vapi dashboard |
| **Public chat URL** | `https://<render-app>.onrender.com/chat` |
| GitHub | `https://github.com/vasanthbanoth/scaler-ai-persona` |
| Loom | _(your link, ≤4 min)_ |
| Eval PDF | upload `evals/output/eval_report.pdf` |

Form: https://forms.gle/MrZMGCKikHaFkA3J9

## 15-minute deploy order

```bash
./scripts/setup.sh          # local: .env + ingest
gh auth login               # once
./scripts/publish_github.sh scaler-ai-persona
```

1. [Render](https://dashboard.render.com) → New → Blueprint → connect repo → add `OPENAI_API_KEY`, `CALCOM_*`
2. Wait for deploy + ingest (~3–5 min on free tier)
3. Open `https://<app>.onrender.com/health` → `corpus_ready: true`
4. `./scripts/configure_vapi.sh` → import JSON in Vapi → attach phone
5. `python evals/run_chat_eval.py` → edit voice stats → `python evals/generate_report.py`
6. Submit form + keep live **7 days**
