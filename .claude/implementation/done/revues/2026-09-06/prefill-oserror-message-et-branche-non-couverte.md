+++
id = "prefill-oserror-message-et-branche-non-couverte"
title = "La branche OSError de prefill._run n'est jamais couverte, et son message ment sur la cause"
date = 2026-08-31
reviewed = 2026-09-06
category = "pertinent"
+++

## Vérifié par

```
$ grep -n -A5 "except OSError" skills/list-dir/scripts/listdir/prefill.py
105:    except OSError as exc:
106-        # C'est `bash` qui manque, pas la commande : celle-ci, introuvable, ressort
107-        # en code 127 par la branche suivante. Confondre les deux enverrait corriger
108-        # un contrat parfaitement valide.
109-        return fail(f"{subject} — commande « {command} » : bash introuvable — {exc}")

$ grep -n "OSError\|binaire_absent" skills/list-dir/scripts/tests/test_prefill.py
88:def test_champ_command_binaire_absent(liste_vide: Path) -> None:
```

## Verdict

La branche est inchangée : **toute** `OSError` est rapportée « bash introuvable », quelle qu'en
soit la cause — permission refusée sur le `cwd`, `bash` non exécutable, `ENOMEM`. Ni la
distinction par `errno`, ni le renoncement à nommer une cause inconnue, n'ont été écrits.

Côté couverture, le test qui porte le nom trompeur n'a pas été renommé et aucun test n'exerce la
branche `OSError` : elle reste entièrement non couverte, exactement comme au constat.

## Action

Maintien au registre. `category = "pertinent"`, `reviewed = 2026-09-06`.

## Arbitrage

<OPTIONNEL>
