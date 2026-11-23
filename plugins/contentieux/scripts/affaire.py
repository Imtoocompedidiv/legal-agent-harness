"""Commandes du dossier d'affaire. Toutes les dates d'écriture sont lues sur le poste.

  init <dossier> --intitule T --client C [--adversaire A]... [--juridiction J]... --objectif O
  etat                                   briefing complet (identique au démarrage de session)
  journal "texte" [--type fait|acte|strategie|decision_client|note]
  piece ajouter <fichier> --cote N --date AAAA-MM-JJ --description D [--source S]
  piece verifier                         recalcule les empreintes du bordereau
  echeance ajouter --objet O --date D --regle R --depart P --source S [--certitude certaine|scenario]
  canal controle <id> [--resultat R]     consigne le contrôle d'un canal de notification
  objection ajouter --acte A --enonce E --gravite dirimante|serieuse|mineure [--auteur X]
  objection clore <id> --statut traitee|acceptee_client|rejetee_motivee --resolution R [--ou O]
  verifier                               valide tous les fichiers d'état et les pièces
  empreinte <fichier>                    SHA-256 exact du fichier (à donner au juge simulé)
  extrait-tri <brouillon.md>             première page et dispositif, ce que lit le juge du tri
  controle <brouillon.md>               lance le contrôle avant dépôt (gate.py)
  finaliser <brouillon.md>               copie en ecritures/FINAL après contrôle PASS sur l'empreinte exacte
  depot <final.md> --accord "mots du client" --canal C   consigne un dépôt ou un envoi fait sur accord exprès
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import lib_affaire as L  # noqa: E402

GABARIT = ICI.parent / "templates" / "affaire"


def racine_ou_sortie() -> Path:
    r = L.trouver_racine(Path.cwd())
    if r is None:
        raise SystemExit("Pas de dossier d'affaire ici (etat/affaire.json introuvable dans ce dossier ou ses parents).")
    return r


def cmd_init(a):
    cible = Path(a.dossier).resolve()
    if cible.is_relative_to(ICI.parent):
        raise SystemExit("Un dossier d'affaire ne se range pas dans le répertoire du plugin : Claude Code y refuse les écritures.")
    if (cible / L.MARQUEUR).exists():
        raise SystemExit(f"{cible} est déjà un dossier d'affaire.")
    cible.mkdir(parents=True, exist_ok=True)
    for src in GABARIT.rglob("*"):
        dst = cible / src.relative_to(GABARIT)
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        elif not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    # Le chemin des scripts est celui du plugin qui crée le dossier, installé ou non : écrit en dur, il renvoyait l'agent vers
    # l'arbre de développement (banc du 22 novembre : une session de la v38 exécutait les scripts de la source).
    constitution = cible / "AGENTS.md"
    if constitution.is_file():
        constitution.write_text(constitution.read_text(encoding="utf-8").replace("{{SCRIPTS}}", str(ICI) + os.sep), encoding="utf-8")
    affaire = L.lire_json(cible / L.MARQUEUR, {}) or {}
    ident = a.id or L.maintenant().strftime("%Y%m%d-%H%M")
    affaire.update({"id": ident, "intitule": a.intitule, "client": a.client, "adversaires": a.adversaire or [],
                    "juridictions": a.juridiction or [], "objectif": a.objectif, "cree_le": L.horodatage()})
    L.ecrire_json(cible / L.MARQUEUR, affaire)
    L.ajouter_journal(cible, f"Ouverture du dossier « {a.intitule} ». Objectif déclaré : {a.objectif}", "fait")
    print(f"Dossier créé : {cible}\nOuvrir Claude Code dans ce dossier ; le briefing d'état s'affiche au démarrage.")


def cmd_etat(a):
    import hook
    print(hook.briefing(racine_ou_sortie(), ""))


def cmd_journal(a):
    print(L.ajouter_journal(racine_ou_sortie(), a.texte, a.type).strip())


def cmd_piece(a):
    r = racine_ou_sortie()
    chemin_b = r / "pieces/bordereau.json"
    b = L.lire_json(chemin_b, {"pieces": []}) or {"pieces": []}
    if a.action == "ajouter":
        src = Path(a.fichier).resolve()
        if not src.is_file():
            raise SystemExit(f"Fichier introuvable : {src}")
        if any(str(p["cote"]) == str(a.cote) for p in b["pieces"]):
            raise SystemExit(f"La cote {a.cote} existe déjà ; une pièce ne se remplace pas, elle reçoit une nouvelle cote.")
        dst = r / "pieces/originaux" / f"{int(a.cote):03d}_{src.name}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        empreinte = L.sha256_fichier(dst)
        if empreinte != L.sha256_fichier(src):
            dst.unlink()
            raise SystemExit("Copie non conforme à l'original ; rien n'a été ajouté.")
        b["pieces"].append({"cote": str(a.cote), "fichier": dst.relative_to(r).as_posix(), "sha256": empreinte,
                            "date_piece": a.date, "description": a.description, "source": a.source or "",
                            "ajoutee_le": L.horodatage()})
        b["pieces"].sort(key=lambda p: int(p["cote"]) if str(p["cote"]).isdigit() else 10**6)
        L.ecrire_json(chemin_b, b)
        L.ajouter_journal(r, f"Pièce {a.cote} ajoutée : {a.description} ({empreinte[:12]}).", "fait")
        print(f"Pièce {a.cote} : {dst.relative_to(r).as_posix()} [{empreinte[:12]}]")
    else:
        defauts = 0
        for p in b["pieces"]:
            f = r / p["fichier"]
            if not f.is_file():
                print(f"MANQUANTE cote {p['cote']} : {p['fichier']}")
                defauts += 1
            elif L.sha256_fichier(f) != p["sha256"]:
                print(f"ALTÉRÉE cote {p['cote']} : {p['fichier']}")
                defauts += 1
        print(f"{len(b['pieces'])} pièce(s) contrôlée(s), {defauts} défaut(s).")
        raise SystemExit(1 if defauts else 0)


def cmd_echeance(a):
    r = racine_ou_sortie()
    chemin = r / "etat/echeances.json"
    d = L.lire_json(chemin, {"echeances": []}) or {"echeances": []}
    if L.parse_date(a.date) is None:
        raise SystemExit("Date attendue au format AAAA-MM-JJ ou AAAA-MM-JJTHH:MM.")
    ident = f"E{len(d['echeances']) + 1:03d}"
    d["echeances"].append({"id": ident, "objet": a.objet, "date": a.date, "regle": a.regle, "point_de_depart": a.depart,
                           "source": a.source, "certitude": a.certitude, "statut": "a_venir", "inscrite_le": L.horodatage()})
    L.ecrire_json(chemin, d)
    L.ajouter_journal(r, f"Échéance {ident} : {a.objet}, {a.date} ({a.regle}, départ {a.depart}).", "fait")
    print(ident)


def cmd_canal(a):
    r = racine_ou_sortie()
    chemin = r / "etat/canaux.json"
    d = L.lire_json(chemin, {"canaux": []}) or {"canaux": []}
    for c in d["canaux"]:
        if c["id"] == a.id:
            c["dernier_controle"] = L.maintenant().isoformat(timespec="minutes")
            c["dernier_resultat"] = a.resultat or ""
            L.ecrire_json(chemin, d)
            L.ajouter_journal(r, f"Canal « {c['nom']} » contrôlé : {a.resultat or 'rien de nouveau'}.", "fait")
            print(f"{c['nom']} contrôlé à {c['dernier_controle']}.")
            return
    raise SystemExit(f"Canal {a.id} inconnu ; canaux : {[c['id'] for c in d['canaux']]}")


def cmd_objection(a):
    r = racine_ou_sortie()
    chemin = r / "etat/objections.json"
    d = L.lire_json(chemin, {"objections": []}) or {"objections": []}
    if a.action == "ajouter":
        ident = f"O{len(d['objections']) + 1:03d}"
        d["objections"].append({"id": ident, "acte": a.acte, "enonce": a.enonce, "auteur": a.auteur or "",
                                "gravite": a.gravite, "statut": "ouverte", "date": L.horodatage()})
        print(ident)
    else:
        for o in d["objections"]:
            if o["id"] == a.id:
                if a.statut == "acceptee_client" and not a.resolution:
                    raise SystemExit("Une objection acceptée par le client exige ses mots et la date de son accord dans --resolution.")
                o.update({"statut": a.statut, "resolution": a.resolution, "ou": a.ou or "", "close_le": L.horodatage()})
                break
        else:
            raise SystemExit(f"Objection {a.id} inconnue.")
    L.ecrire_json(chemin, d)
    L.ajouter_journal(r, f"Objection {a.action} : {a.enonce if a.action == 'ajouter' else a.id + ' ' + a.statut}.", "strategie")


def cmd_verifier(a):
    r = racine_ou_sortie()
    total = 0
    for rel in L.SCHEMAS:
        for e in L.valider_fichier(r, rel):
            print(e)
            total += 1
    import pieces as PIECES
    ctx = PIECES.Contexte(r)
    for cote in ctx.bordereau:
        if ctx.fiche(cote) is not None:
            for e in ctx.validation(cote)[0]:
                print(e)
                total += 1
    for e in PIECES.valider_matrice(r, ctx)[0]:
        print(e)
        total += 1
    print(f"{total} défaut(s) de structure.")
    raise SystemExit(1 if total else 0)


def cmd_empreinte(a):
    print(L.sha256_fichier(Path(a.fichier).resolve()))


def cmd_extrait_tri(a):
    import lint_ecriture as LINT
    src = Path(a.fichier).resolve()
    r = L.trouver_racine(src)
    texte = src.read_text(encoding="utf-8")
    debut, _ = LINT.section_conclusions(texte)
    dispositif = texte[debut:] if debut >= 0 else "(aucun dispositif repéré)"
    for borne in ("\n## Pièces", "\nPièces jointes", "\nBordereau", "\nINVENTAIRE"):
        i = dispositif.find(borne)
        if i > 0:
            dispositif = dispositif[:i]
    dst = r / "ecritures/controle" / f"{src.stem}.extrait_tri.md"
    dst.write_text(f"# Extrait de tri de {src.name}\n\n## Première page\n\n{LINT.premiere_page(texte)}\n\n[...]\n\n## Dispositif\n\n{dispositif.strip()}\n",
                   encoding="utf-8")
    print(f"{dst}\nempreinte du texte complet : {L.sha256_fichier(src)}")


def cmd_controle(a):
    import gate
    v = gate.controler(Path(a.fichier).resolve())
    print(gate.resume(v))
    raise SystemExit(0 if v["verdict"] == "PASS" else 1)


def cmd_finaliser(a):
    import gate
    src = Path(a.fichier).resolve()
    v = gate.controler(src)
    print(gate.resume(v))
    if v["verdict"] != "PASS":
        raise SystemExit("Finalisation refusée : contrôle FAIL.")
    r = L.trouver_racine(src)
    dst = r / "ecritures/FINAL" / f"{src.stem}__{v['sha256'][:10]}{src.suffix}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    L.ajouter_journal(r, f"Version finale {dst.relative_to(r).as_posix()} (contrôle PASS, {v['sha256'][:12]}). Aucun dépôt fait par cette commande.", "acte")
    print(f"Version finale : {dst}")


def cmd_depot(a):
    r = racine_ou_sortie()
    f = Path(a.fichier).resolve()
    if "FINAL" not in f.parts:
        raise SystemExit("Seule une version de ecritures/FINAL peut être consignée comme déposée ou envoyée.")
    if not a.accord.strip():
        raise SystemExit("L'accord exprès du client, dans ses mots, est obligatoire.")
    L.ajouter_journal(r, f"DÉPÔT/ENVOI de {f.relative_to(r).as_posix()} [{L.sha256_fichier(f)[:12]}] par {a.canal}. Accord du client : « {a.accord} ».", "acte")
    print("Consigné au journal. Conserver la preuve de dépôt dans pieces/ ou preuves/.")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    i = s.add_parser("init"); i.add_argument("dossier"); i.add_argument("--id"); i.add_argument("--intitule", required=True)
    i.add_argument("--client", required=True); i.add_argument("--adversaire", action="append"); i.add_argument("--juridiction", action="append")
    i.add_argument("--objectif", required=True); i.set_defaults(f=cmd_init)
    s.add_parser("etat").set_defaults(f=cmd_etat)
    j = s.add_parser("journal"); j.add_argument("texte"); j.add_argument("--type", default="note",
        choices=["fait", "acte", "strategie", "decision_client", "note"]); j.set_defaults(f=cmd_journal)
    pc = s.add_parser("piece"); pc.add_argument("action", choices=["ajouter", "verifier"]); pc.add_argument("fichier", nargs="?")
    pc.add_argument("--cote"); pc.add_argument("--date"); pc.add_argument("--description"); pc.add_argument("--source"); pc.set_defaults(f=cmd_piece)
    e = s.add_parser("echeance"); e.add_argument("action", choices=["ajouter"]); e.add_argument("--objet", required=True)
    e.add_argument("--date", required=True); e.add_argument("--regle", required=True); e.add_argument("--depart", required=True)
    e.add_argument("--source", required=True); e.add_argument("--certitude", default="certaine", choices=["certaine", "scenario"]); e.set_defaults(f=cmd_echeance)
    c = s.add_parser("canal"); c.add_argument("action", choices=["controle"]); c.add_argument("id"); c.add_argument("--resultat"); c.set_defaults(f=cmd_canal)
    o = s.add_parser("objection"); o.add_argument("action", choices=["ajouter", "clore"]); o.add_argument("id", nargs="?")
    o.add_argument("--acte"); o.add_argument("--enonce"); o.add_argument("--gravite", choices=["dirimante", "serieuse", "mineure"])
    o.add_argument("--auteur"); o.add_argument("--statut", choices=["traitee", "acceptee_client", "rejetee_motivee"])
    o.add_argument("--resolution"); o.add_argument("--ou"); o.set_defaults(f=cmd_objection)
    s.add_parser("verifier").set_defaults(f=cmd_verifier)
    em = s.add_parser("empreinte"); em.add_argument("fichier"); em.set_defaults(f=cmd_empreinte)
    et = s.add_parser("extrait-tri"); et.add_argument("fichier"); et.set_defaults(f=cmd_extrait_tri)
    k = s.add_parser("controle"); k.add_argument("fichier"); k.set_defaults(f=cmd_controle)
    fz = s.add_parser("finaliser"); fz.add_argument("fichier"); fz.set_defaults(f=cmd_finaliser)
    d = s.add_parser("depot"); d.add_argument("fichier"); d.add_argument("--accord", required=True); d.add_argument("--canal", required=True); d.set_defaults(f=cmd_depot)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
