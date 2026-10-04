---
name: skill-convention
description: >
  Conventions de maintien de ma configuration Claude Code, globale (~/.claude) comme locale à un
  projet : prose d'une skill, code Python, documents posés depuis un gabarit, mémoire tenue en
  registres, commandes mises à la disposition d'un agent. Se déclenche à l'écriture ou à la
  relecture d'un `SKILL.md`, d'un fichier de `references/` ou de tout autre fichier d'une skill,
  à la pose d'un document ou d'un registre, et dès qu'un projet doit fournir une nouvelle commande à un
  agent. Ne corrige aucune skill.
---

# skill-convention — les conventions de ma configuration

Ce skill est un Shadow-skill : son contenu vit dans
[`shadow-skills/skill-convention/`](../../shadow-skills/skill-convention/SKILL.md), hors du
contexte. Le charger avant d'écrire ou de relire un fichier de skill :

```bash
shadow-skill charge skill-convention
```
