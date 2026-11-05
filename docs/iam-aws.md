# Accès AWS (IAM) — Uber

Le dashboard Uber lit un fichier Parquet dans S3. Il utilise **sa propre clé AWS**, rattachée à un user IAM
dont les droits sont limités à un seul bucket. Aucun `AmazonS3FullAccess`, aucune clé partagée avec un
autre projet.

Pourquoi : une clé AWS d'un autre projet de ce compte a fuité dans un dépôt GitHub public et a dû être
révoquée. Jusqu'en novembre 2026, ce projet réutilisait d'ailleurs la clé du projet Kayak, qui n'avait pas
les droits sur ce bucket : chaque projet a désormais son user.

## Qui utilise quoi

| User IAM | Bucket | Fichier local | Déploiement en ligne |
|---|---|---|---|
| `cdsd-uber` | `cdsd-uber-data` | `.env` (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `S3_BUCKET`) et `.streamlit/secrets.toml` (section `[aws]`) | Streamlit Community Cloud : Settings → Secrets |

Région : `eu-west-3`.

| Script | Opération S3 | Droit requis |
|---|---|---|
| `dashboard/prepare_data.py` | dépose `dashboard_sept2w.parquet` (`upload_file`), une seule fois | `s3:PutObject` |
| `dashboard/app.py` | lit `s3://cdsd-uber-data/dashboard_sept2w.parquet` via `s3fs` / pandas | `s3:GetObject` |

## Policy du user (inline `cdsd-uber-rw`)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "UberDataReadWrite",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::cdsd-uber-data/*"
    }
  ]
}
```

Pas de `s3:DeleteObject`, pas d'accès aux autres buckets. Le listing du bucket est refusé : l'app lit le
fichier par son nom exact.

## Créer ou renouveler la clé

À faire avec un profil administrateur. La clé est écrite dans un fichier lisible par vous seul : elle ne
s'affiche ni dans le terminal ni dans l'historique du shell, et ne doit jamais être collée dans un chat.

```bash
umask 077
aws iam create-access-key --user-name cdsd-uber \
  --query 'AccessKey.[AccessKeyId,SecretAccessKey]' --output text > cdsd-uber.key
```

Reporter l'identifiant et le secret à **deux endroits**, puis détruire le fichier (`shred -u cdsd-uber.key`) :

1. le `.env` et `.streamlit/secrets.toml` locaux ;
2. les **Secrets de l'app en ligne** (Streamlit Community Cloud → Settings → Secrets, section `[aws]`),
   puis redémarrer l'app (Reboot app). Les secrets locaux n'ont aucun effet sur l'app hébergée.

Pour renouveler : créer la nouvelle clé, mettre à jour les deux endroits, vérifier, puis supprimer
l'ancienne (`aws iam delete-access-key`). Ne pas garder le CSV de clés téléchargé depuis la console IAM
dans le projet.

## Vérifier la clé (sans modifier de données)

```bash
set -a; source .env; set +a
aws sts get-caller-identity --query Arn --output text                      # doit afficher le user cdsd-uber
aws s3 cp s3://cdsd-uber-data/dashboard_sept2w.parquet - | wc -c          # doit réussir (octets lus)
aws s3 ls s3://cdsd-uber-data/                                             # doit être refusé (AccessDenied)
aws s3 ls s3://cdsd-kayak-datalake/                                        # doit être refusé : autre projet
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN            # avant de repasser en admin
```

Pour l'app **hébergée**, ouvrir l'URL : le dashboard doit afficher les données (sinon le message « Accès S3
refusé » de `dashboard/app.py` s'affiche). Un administrateur confirme l'usage de la clé avec :

```bash
aws iam get-access-key-last-used --access-key-id <ID_DE_LA_CLE> \
  --query 'AccessKeyLastUsed.[LastUsedDate,ServiceName,Region]' --output text
```

## Une erreur 403 / AccessDenied

Lire le message : il nomme l'**action** et la **ressource** refusées. Si l'accès est légitime, ajouter cette
action sur cette ressource à la policy, au plus juste.

- `ListObjectsV2` refusé au lancement de l'app (`s3fs` liste parfois avant de lire) : ajouter `s3:ListBucket`
  sur `arn:aws:s3:::cdsd-uber-data`, avec la condition `s3:prefix` sur le fichier ou le préfixe lu.
- `InvalidAccessKeyId` / `InvalidClientTokenId` (et non `AccessDenied`) : la clé n'existe plus. L'app
  hébergée garde probablement l'ancienne clé dans ses Secrets : les mettre à jour et redémarrer l'app.

## Règles

- Une clé par projet, jamais de clé partagée.
- Pas d'`AdministratorAccess` ni de `*FullAccess`, pas de `s3:*`, pas de ressource `*`.
- `.env` et `.streamlit/secrets.toml` restent hors git (`.gitignore`) et en `600`.
- Activer le *secret scanning* et la *push protection* GitHub sur le dépôt.
