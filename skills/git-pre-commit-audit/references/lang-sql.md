# Qualité — SQL et Migrations

## Patterns bloquants ❌

```sql
DROP TABLE users;                          -- sans IF EXISTS, irréversible
DELETE FROM sessions;                      -- sans WHERE, suppression totale
ALTER TABLE x DROP COLUMN y;              -- perte de données définitive
UPDATE users SET role='admin';            -- sans WHERE, affecte tout le monde
```

## Avertissements ⚠️

```sql
ALTER TABLE ADD COLUMN x VARCHAR NOT NULL  -- sans DEFAULT sur table peuplée
DROP INDEX idx_email;                      -- index sur colonne fréquemment requêtée
CREATE INDEX ... ON large_table;          -- sans CONCURRENTLY (lock en prod)
```

## Points à vérifier pour chaque migration

- La migration est-elle **réversible** ? Y a-t-il un `down()` équivalent ?
- Les `DROP` sont-ils tous précédés d'une sauvegarde ou d'un rollback plan ?
- Les colonnes `NOT NULL` ajoutées ont-elles une valeur `DEFAULT` ?
- Les nouveaux index sur grandes tables utilisent-ils `CONCURRENTLY` (PostgreSQL) ?
- Les foreign keys ont-elles des index sur les colonnes référencées ?
- Le changement de type de colonne préserve-t-il les données existantes ?

## Patterns corrects

```sql
-- ✅ Suppression sécurisée
DROP TABLE IF EXISTS old_table;
DELETE FROM sessions WHERE created_at < NOW() - INTERVAL '30 days';

-- ✅ Ajout de colonne safe
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}';

-- ✅ Index sans lock (PostgreSQL)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);
```

## Impact à évaluer

- Nombre de lignes affectées estimé (mentionner si table volumineuse)
- Compatibilité avec le code applicatif existant avant déploiement
- Nécessité d'une migration de données en plusieurs étapes (expand/contract)
