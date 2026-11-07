import json, time, subprocess, requests, uuid
BASE="http://127.0.0.1:8000"

def reg(name,email):
    r=requests.post(f"{BASE}/auth/register",json={"organization_name":name,"full_name":"Tester","email":email,"password":"pass1234"})
    r.raise_for_status(); return r.json()

A=reg("ExpCo","exp@expco.local")
tokenA=A["access_token"]; orgA=A["organization"]["id"]
H={"Authorization":f"Bearer {tokenA}"}
print("orgA",orgA)
# create suppliers/orders via direct DB using backend venv would be separate; here just chat baseline
r=requests.post(f"{BASE}/agent/chat",headers=H,json={"message":"Which supplier should we choose for an urgent order, Alpha or Beta?","new_conversation":True})
print(json.dumps(r.json(),indent=2)[:3000])
