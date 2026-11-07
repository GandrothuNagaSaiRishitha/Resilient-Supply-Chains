import time
from hindsight_client import Hindsight

client = Hindsight(base_url="http://127.0.0.1:8888", timeout=240.0)
print("version:", client.get_version().api_version)

bank = "smoke_test_bank_001"
try:
    client.create_bank(
        bank_id=bank,
        name="SUPPLYMIND smoke test",
        mission="You are a supply-chain memory assistant. Remember verified supplier delivery facts.",
    )
except Exception as exc:
    print("create_bank:", type(exc).__name__, str(exc)[:300])

t0 = time.time()
res = client.retain(
    bank_id=bank,
    content=(
        "Order 101 from Alpha Components was promised in 5 days but arrived after 15 days. "
        "The shipment was delayed at the Rotterdam port because of a customs hold. "
        "This is a verified delivery fact recorded on 2026-10-02."
    ),
    context="supplier delivery history",
    metadata={"supplier": "Alpha Components", "order": "101", "source_type": "verified_business_fact"},
)
print(f"retain: ok in {time.time()-t0:.1f}s ->", res)

t0 = time.time()
recall = client.recall(bank_id=bank, query="How reliable is Alpha Components for urgent orders?")
print(f"recall: {len(recall.results)} results in {time.time()-t0:.1f}s")
for r in recall.results:
    print(" -", r.type, "|", r.text[:200])

t0 = time.time()
answer = client.reflect(
    bank_id=bank,
    query="Should we order from Alpha Components for an urgent 5-day delivery?",
    context="Procurement decision for 1,000 electronic components",
)
print(f"reflect: in {time.time()-t0:.1f}s")
print(answer.text[:1500])
