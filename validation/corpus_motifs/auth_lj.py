"""Autorisation OAuth propre au minage de corpus sur LibreJustice (PKCE, enregistrement dynamique, redirection locale).

    python auth_lj.py            affiche le lien d'autorisation, attend le retour sur 127.0.0.1, enregistre le jeton
    python auth_lj.py --etat     dit si un jeton est enregistré et sa validité restante

Le jeton est rangé hors du dépôt (~/.harness-corpus/librejustice.json), jamais affiché ; il se rafraîchit seul.
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import json
import secrets
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

SERVEUR = "https://librejustice.fr"
RESSOURCE = "https://librejustice.fr/mcp"
PORT = 8765
REDIRECTION = f"http://127.0.0.1:{PORT}/callback"
FICHIER = Path.home() / ".harness-corpus" / "librejustice.json"


def _post(url: str, donnees: dict, json_corps: bool = False) -> dict:
    corps = json.dumps(donnees).encode() if json_corps else urllib.parse.urlencode(donnees).encode()
    typ = "application/json" if json_corps else "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=corps, headers={"Content-Type": typ, "Accept": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def _enregistrer(etat: dict) -> None:
    FICHIER.parent.mkdir(parents=True, exist_ok=True)
    FICHIER.write_text(json.dumps(etat), encoding="utf-8")


def jeton() -> str:
    """Jeton d'accès valide, rafraîchi au besoin."""
    if not FICHIER.exists():
        raise RuntimeError("aucune autorisation : lancer `python auth_lj.py`")
    etat = json.loads(FICHIER.read_text(encoding="utf-8"))
    if time.time() > etat.get("expire", 0) - 120 and etat.get("refresh_token"):
        t = _post(f"{SERVEUR}/oauth/token", {"grant_type": "refresh_token", "refresh_token": etat["refresh_token"],
                                              "client_id": etat["client_id"], "resource": RESSOURCE})
        etat.update(access_token=t["access_token"], refresh_token=t.get("refresh_token", etat["refresh_token"]),
                    expire=time.time() + int(t.get("expires_in", 3600)))
        _enregistrer(etat)
    return etat["access_token"]


def autoriser() -> None:
    client = _post(f"{SERVEUR}/oauth/register", {"client_name": "harness contentieux, minage de corpus", "redirect_uris": [REDIRECTION],
                                                  "grant_types": ["authorization_code", "refresh_token"], "response_types": ["code"],
                                                  "token_endpoint_auth_method": "none", "scope": "mcp"}, json_corps=True)
    verif = secrets.token_urlsafe(64)
    defi = base64.urlsafe_b64encode(hashlib.sha256(verif.encode()).digest()).rstrip(b"=").decode()
    etat_csrf = secrets.token_urlsafe(16)
    lien = f"{SERVEUR}/oauth/authorize?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": client["client_id"], "redirect_uri": REDIRECTION, "scope": "mcp",
        "code_challenge": defi, "code_challenge_method": "S256", "state": etat_csrf, "resource": RESSOURCE})
    recu: dict = {}

    class Retour(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            recu.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("Autorisation reçue. Vous pouvez fermer cet onglet.".encode())

        def log_message(self, *a):  # silence
            pass

    print("LIEN_AUTORISATION " + lien, flush=True)
    serveur = http.server.HTTPServer(("127.0.0.1", PORT), Retour)
    while "code" not in recu and "error" not in recu:
        serveur.handle_request()
    if recu.get("state") != etat_csrf or "code" not in recu:
        sys.exit(f"autorisation refusée ou invalide : {recu.get('error', 'état incohérent')}")
    t = _post(f"{SERVEUR}/oauth/token", {"grant_type": "authorization_code", "code": recu["code"], "redirect_uri": REDIRECTION,
                                          "client_id": client["client_id"], "code_verifier": verif, "resource": RESSOURCE})
    _enregistrer({"client_id": client["client_id"], "access_token": t["access_token"], "refresh_token": t.get("refresh_token"),
                  "expire": time.time() + int(t.get("expires_in", 3600))})
    print("autorisation enregistrée", flush=True)


if __name__ == "__main__":
    if "--etat" in sys.argv:
        if FICHIER.exists():
            e = json.loads(FICHIER.read_text(encoding="utf-8"))
            print("jeton enregistré, valide encore", round((e.get("expire", 0) - time.time()) / 60), "min ; rafraîchissement :",
                  bool(e.get("refresh_token")))
        else:
            print("aucun jeton")
    else:
        autoriser()
