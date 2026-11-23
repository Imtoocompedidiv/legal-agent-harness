"""Client minimal du serveur MCP de LibreJustice (HTTP « streamable »), sans modèle : recherche et lecture de décisions publiques.

    from lj import Client
    c = Client(); hits = c.appel("search_decisions", {"query": "...", "limit": 20})
"""
from __future__ import annotations

import json
import time
import urllib.request

URL = "https://librejustice.fr/mcp/"


class Client:
    def __init__(self) -> None:
        self.session: str | None = None
        self.n = 0
        self._rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                 "clientInfo": {"name": "harness-corpus", "version": "1"}})
        self._notifier("notifications/initialized")

    def _post(self, corps: dict) -> tuple[dict | None, dict]:
        from auth_lj import jeton
        entetes = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream",
                   "Authorization": f"Bearer {jeton()}"}
        if self.session:
            entetes["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(URL, data=json.dumps(corps).encode(), headers=entetes, method="POST")
        with urllib.request.urlopen(req, timeout=90) as r:
            self.session = r.headers.get("Mcp-Session-Id") or self.session
            brut = r.read().decode("utf-8")
            if not brut.strip():
                return None, dict(r.headers)
            if "text/event-stream" in (r.headers.get("Content-Type") or ""):
                donnees = [l[5:].strip() for l in brut.splitlines() if l.startswith("data:")]
                return (json.loads(donnees[-1]) if donnees else None), dict(r.headers)
            return json.loads(brut), dict(r.headers)

    def _notifier(self, methode: str) -> None:
        self._post({"jsonrpc": "2.0", "method": methode})

    def _rpc(self, methode: str, params: dict) -> dict:
        self.n += 1
        rep, _ = self._post({"jsonrpc": "2.0", "id": self.n, "method": methode, "params": params})
        if rep is None or "error" in rep:
            raise RuntimeError(f"{methode} : {rep}")
        return rep["result"]

    def appel(self, outil: str, arguments: dict, essais: int = 3):
        for k in range(essais):
            try:
                res = self._rpc("tools/call", {"name": outil, "arguments": arguments})
                texte = "".join(b.get("text", "") for b in res.get("content", []) if b.get("type") == "text")
                if res.get("isError"):
                    raise RuntimeError(texte[:300])
                return json.loads(texte) if texte.strip().startswith(("{", "[")) else texte
            except Exception:  # noqa: BLE001
                if k == essais - 1:
                    raise
                time.sleep(3 * (k + 1))


if __name__ == "__main__":
    c = Client()
    print(json.dumps(c._rpc("tools/list", {}), ensure_ascii=False)[:400])
