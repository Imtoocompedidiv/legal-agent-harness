"""Texte intégral d'une décision LibreJustice par le client autorisé : python decision.py URL"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lj import Client
sys.stdout.reconfigure(encoding="utf-8")
d = Client().appel("get_decision", {"url": sys.argv[1]})
print("#", d.get("title")); print(d.get("text", ""))
