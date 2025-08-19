# Floiy Reco API (MVP)

## Quickstart
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# Health: http://127.0.0.1:8000/health
# POST http://127.0.0.1:8000/v1/extract_keywords
# POST http://127.0.0.1:8000/v1/recommendations
```

## Example Request
```json
POST /v1/recommendations
{
  "story": "요즘 지친 친구에게 밝은 꽃",
  "budget": 50000,
  "preferred_colors": ["yellow","white"],
  "excluded_flowers": ["국화"],
  "top_k": 3
}
```
