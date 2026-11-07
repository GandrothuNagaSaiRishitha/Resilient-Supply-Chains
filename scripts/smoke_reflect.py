"""Verify recall and reflect against the live Hindsight server (no retain).

Run after the smoke retain has stored at least one memory:
    backend/.venv/Scripts/python scripts/smoke_reflect.py
"""
import time

from hindsight_client import Hindsight

client = Hindsight(base_url="http://127.0.0.1:8888", timeout=240.0)
bank = "smoke_test_bank_001"

t0 = time.time()
recall = client.recall(bank_id=bank, query="How reliable is Alpha Components for urgent orders?", budget="mid")
print(f"recall: {len(recall.results)} results in {time.time()-t0:.1f}s")
for r in recall.results[:5]:
    print(" -", r.type, "|", r.text[:180])

t0 = time.time()
answer = client.reflect(
    bank_id=bank,
    query="Should we order from Alpha Components for an urgent 5-day delivery?",
    context="Procurement decision for 1,000 electronic components",
    budget="mid",
)
print(f"reflect: in {time.time()-t0:.1f}s")
print(answer.text[:2000])

