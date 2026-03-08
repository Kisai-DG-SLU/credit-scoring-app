# Gestion des Versions - Projet 7

**Candidat :** Damien GUESDON  
**Projet :** Déploiement et monitoring d'un modèle de scoring  
**État du dépôt :** v0.21 (Release actuelle)  
**Date :** 21 Janvier 2026

---

## 1. Stratégie de Versioning
Le projet a adopté un versioning sémantique incrémental (**v0.x.x**) pour refléter les phases de tests intensifs et de déploiements continus (CI/CD). Chaque version correspond à une amélioration de la robustesse, de la couverture de tests ou de la sécurité.

---

## 2. Historique Synthétique des Jalons

| Version | Date | Nature des évolutions |
| :--- | :--- | :--- |
| **v0.21** | 21/01/2026 | **Version finale (Ultimate)** : Nettoyage sécurisé de l'historique et validation de conformité. |
| **v0.16** | 16/01/2026 | Optimisation des ports API (8501) pour le déploiement Hugging Face. |
| **v0.14** | 16/01/2026 | **QA & Tests** : Validation de la couverture de tests à 75%+. |
| **v0.12** | 14/01/2026 | Correction des erreurs de runtime et gestion du PYTHONPATH en production. |
| **v0.10** | 14/01/2026 | **Industrialisation** : Passage au Docker `python-slim` (résolution OOM Error 137). |
| **v0.0.4** | 12/01/2026 | **Release Stable** : Finalisation de la V1 avec licence et support LFS. |
| **v0.0.1** | 12/01/2026 | Initialisation du monitoring et première clôture de session. |

---

## 3. Historique Complet

| id | Date | Nature des évolutions |
| :--- | :--- | :--- |
| 43996789 | 2026-01-21 | fix: ultimate version (I hope)  (HEAD -> temp/rescue-mission, origin/temp/rescue-mission)|
| 632e398e | 2026-01-17 | Add rescue workflow |
| 2edcfc86 | 2026-01-17 | Add rescue workflow |
| 6f4e5384 | 2026-01-17 | Add rescue workflow |
| 3523215d | 2026-01-17 | token rescue  (origin/feat/final-delivery-v1.2.0, feat/final-delivery-v1.2.0)|
| b51efa7d | 2026-01-17 | fix(ci): Exclude delivery folder from HF deployment |
| 92ded5b9 | 2026-01-17 | feat(final): Finalisation projet v1.2.0 (Docs, Scripts, Preuves)  (origin/main, origin/HEAD, main)|
| 7f400ee0 | 2026-01-16 | deploy: 35fdcd4e006a5ae7a5406d2b9ed37a9b20ef9dfc  (origin/gh-pages)|
| f6ec24ad | 2026-01-16 | Merge pull request #37 from Kisai-DG-SLU/fix/hf-port-config  (tag: v0.0.16)|
| 35e48d69 | 2026-01-16 | fix: specify app_port 8501 for Hugging Face |
| 748138ce | 2026-01-16 | deploy: 07c6b776d96f64e40ddb87b9eabbb7322d429937 |
| a25444a4 | 2026-01-16 | Merge pull request #36 from Kisai-DG-SLU/fix/hf-lfs-onnx  (tag: v0.0.15)|
| 226b2369 | 2026-01-16 | fix: add onnx to lfs tracking in hf deployment |
| a583c65c | 2026-01-16 | deploy: ba358d3efe1a946ac0fd4d47ee96fcdc678c3b8e |
| fdd231ff | 2026-01-16 | Merge pull request #35 from Kisai-DG-SLU/feat/T046-api-validation-tests  (tag: v0.0.14)|
| 94c3d020 | 2026-01-16 | fix: final test coverage reaching 75% for dashboard and db utils (T046) |
| acbe24bb | 2026-01-16 | fix: additional tests to reach 70% coverage (T046) |
| b271c84d | 2026-01-16 | fix: add test coverage for db migration logic (T046) |
| 703dcfbe | 2026-01-16 | fix: add onnx dependencies to environment.yml for CI (T046) |
| f3dc3b82 | 2026-01-16 | feat: enhance api robustness and reach 72% coverage (T046) |
| 1996a54f | 2026-01-14 | deploy: d31c85fdfa40a1fa672b7f4ad9b7f27cdee504d9 |
| 747c55d7 | 2026-01-14 | Merge pull request #34 from Kisai-DG-SLU/fix/hf-debug-structure  (tag: v0.0.13)|
| 1388e070 | 2026-01-14 | fix: exhaustive diagnostic for HF file structure  (origin/fix/rename-src-data, origin/fix/hf-debug-structure, fix/rename-src-data, fix/hf-debug-structure)|
| fc96b4b5 | 2026-01-14 | deploy: 1b0098398e6f790f5bba8697fe2d7daf75a507a5 |
| cdd0427d | 2026-01-14 | deploy: ade36f991a6e8957184d907c70bfafb164308f7a |
| 338bfdef | 2026-01-14 | Merge pull request #33 from Kisai-DG-SLU/fix/hf-runtime-error  (tag: v0.0.12)|
| 620a4617 | 2026-01-14 | fix: robust PYTHONPATH and module discovery for HF Spaces (#32)  (tag: v0.0.11)|
| 8ea9e07b | 2026-01-14 | fix: robust PYTHONPATH and module discovery for HF Spaces |
| 7aa826eb | 2026-01-14 | deploy: 949dfa5e9b866da756ee965f7a16e922f397f2c0 |
| 71a5cda4 | 2026-01-14 | Merge pull request #31 from Kisai-DG-SLU/fix/docker-oom-repair  (tag: v0.0.10)|
| fb45ad8a | 2026-01-14 | fix: switch to python-slim base to resolve HF build OOM (Error 137) |
| 0d5060d8 | 2026-01-12 | deploy: d7d5aa3903f2231a6e5c65f25e0055a8cb4942b0 |
| 4e493f40 | 2026-01-12 | Merge pull request #29 from Kisai-DG-SLU/fix/robust-auto-merge-v2  (tag: v0.0.9)|
| 71dccbeb | 2026-01-12 | fix: correct deploy-docs artifact download action |
| 66e8fe2d | 2026-01-12 | Merge pull request #28 from Kisai-DG-SLU/fix/robust-auto-merge-v2  (tag: v0.0.8)|
| ea709a2f | 2026-01-12 | fix: correct gh cli syntax and stabilize pr sequence |
| 38c85c96 | 2026-01-12 | fix: sequence PR creation and merge |
| ae611e2f | 2026-01-12 | fix: finalize project 8 compliance, correct labels and robust auto-merge |
| 8f18e82b | 2026-01-12 | Merge pull request #26 from Kisai-DG-SLU/fix/badges-and-urls  (tag: v0.0.7)|
| bdb456b0 | 2026-01-12 | docs: fix coverage URL casing and switch release badge to tag |
| 54e8dedd | 2026-01-12 | deploy: 66c06cb6fb1daed0d78feca566ac1bc5f5aff3ae |
| 287ba7fe | 2026-01-12 | Merge pull request #25 from Kisai-DG-SLU/fix/standardize-ci-p7-final  (tag: v0.0.6)|
| a16c8665 | 2026-01-12 | fix: finalize P7 standardized CI/CD flow |
| 858f47b1 | 2026-01-12 | deploy: 5453adc4ffb171ee52c721b49b7384f6dd1df94c |
| e242e97a | 2026-01-12 | Merge pull request #24 from Kisai-DG-SLU/fix/automatic-tagging-repair |
| dcd01f16 | 2026-01-12 | fix: repair automatic release with GH_PAT and deduplicate workflows |
| f250d889 | 2026-01-12 | deploy: cdd3d7bdc964b6f0a673e648510aa759f9de75f8 |
| 6876c701 | 2026-01-12 | Merge pull request #23 from Kisai-DG-SLU/fix/final-compliance-fix  (tag: v0.0.5)|
| ed6b6fdd | 2026-01-12 | fix: compliance and tagging configuration |
| 821f418f | 2026-01-12 | docs: fix license badge link |
| e226dd79 | 2026-01-12 | deploy: 05badce45e15b7421787e7c755cae72eb994bf27 |
| 97678d5e | 2026-01-12 | Merge pull request #22 from Kisai-DG-SLU/fix/v1.0.0-final-fixes  (tag: v0.0.4)|
| 5773940d | 2026-01-12 | fix: finalize release v1.0.0 with license and hf fixes |
| 8fee61f4 | 2026-01-12 | WIP on main: 0592df3b fix: add license, fix coverage badge and hf lfs support v1.0.0  (refs/stash)|
| 6c113a0f | 2026-01-12 | fix: add license, fix coverage badge and hf lfs support v1.0.0 |
| 5958d8a6 | 2026-01-12 | feat: final delivery package for soutenance v1.0.0 |
| ecf3d429 | 2026-01-12 | deploy: b4e19b30d0c11bb73ebefbd0ce7041f01e8fe56d |
| f499ee33 | 2026-01-12 | Merge pull request #21 from Kisai-DG-SLU/fix/leak-cleanup  (tag: v0.0.3)|
| 3b0a1c76 | 2026-01-12 | chore: remove sensitive specs and logs from public repository |
| e45d12fb | 2026-01-12 | deploy: df96488be769cf77c3ceed813f732ffc6004a6c3 |
| f58d2be4 | 2026-01-12 | Merge pull request #19 from Kisai-DG-SLU/feat/final-docs  (tag: v0.0.2)|
| f0d76f7a | 2026-01-12 | docs: final documentation and evidence for soutenance |
| 98f8ccd9 | 2026-01-12 | deploy: d5a8dcb5502a832ba565967b815af62dc708c677 |
| a2285af6 | 2026-01-12 | Merge pull request #18 from Kisai-DG-SLU/feat/session-cloture-amelia  (tag: v0.0.1)|
| cc916afb | 2026-01-12 | chore: sync with main |
| 3976a407 | 2026-01-12 | fix: stabilize ModelLoader, fix monitoring tests and reach 79% coverage (formatted) |
| 4d27ac26 | 2026-01-12 | style: fix black formatting in loader.py (hotfix) |
| bd108f9c | 2026-01-12 | fix: update Streamlit API to use width='stretch' instead of deprecated use_container_width |
| e182635a | 2026-01-12 | fix: repair Makefile syntax and target separation |
| a9e97676 | 2026-01-12 | fix: enable local database mounting in Docker and use absolute paths for loader |
| 1290c51b | 2026-01-12 | feat: complete phases 7-10 with P6 realignment and perf metrics |
| dfdd0b20 | 2026-01-12 | chore(mnt): save emergency demo changes [skip ci] |
| 140c06a8 | 2026-01-11 | Merge pull request #16 from Kisai-DG-SLU/fix/final-cd-automation |
| 5396cfa4 | 2026-01-11 | fix: ensure CD is triggered after auto-merge |
| 0d5b1427 | 2026-01-11 | Merge pull request #15 from Kisai-DG-SLU/feat/gh-pat-auto-merge |
| 4b7926fe | 2026-01-11 | feat: use GH_PAT for auto-merge to trigger CD pipeline |
| f2eb0c19 | 2026-01-11 | Merge pull request #14 from Kisai-DG-SLU/fix/hf-lite-db |
| 1d2f184c | 2026-01-11 | fix: use head_ref for source branch in CI auto-merge |
| 164ad136 | 2026-01-11 | Merge pull request #13 from Kisai-DG-SLU/fix/hf-lite-db |
| 9927f19a | 2026-01-11 | fix: yaml syntax in auto-merge job |
| f91e072a | 2026-01-11 | fix: robust auto-merge logic and casing |
| 088cbc7b | 2026-01-11 | feat: implement global auto-merge workflow in CI |
| 81468286 | 2026-01-11 | fix: include lite database in Hugging Face deployment workflow |
| 9ff1123e | 2026-01-11 | fix: generate lite database for Hugging Face deployment |
| 6e0167a3 | 2026-01-11 | docs: finalize README and add demo guide for presentation |
| 28f648c5 | 2026-01-11 | Merge pull request #11 from Kisai-DG-SLU/fix/hf-metadata |
| 4b01a1c3 | 2026-01-11 | fix: add Hugging Face Spaces metadata to README |
| 8b34c4e8 | 2026-01-11 | Merge pull request #10 from Kisai-DG-SLU/feat/final-optimizations |
| ced8f6b4 | 2026-01-11 | feat: optimize dashboard performance with streamlit caching |
| 0227007e | 2026-01-11 | Merge pull request #9 from Kisai-DG-SLU/fix/restore-all |
| 6b1228b1 | 2026-01-11 | chore: restore full monitoring system and fix overwritten files |
| adad76ad | 2026-01-11 | Merge pull request #8 from Kisai-DG-SLU/fix/hf-deploy-lfs |
| b3653404 | 2026-01-11 | fix: enable Git LFS for model artifact during HF deployment |
| 58c71ec1 | 2026-01-11 | Merge pull request #7 from Kisai-DG-SLU/fix/deploy-lfs-error |
| b558821d | 2026-01-11 | fix: ignore dirty history and large files for HF deployment |
| 83be2738 | 2026-01-11 | Merge pull request #5 from Kisai-DG-SLU/feat/deploy-hf |
| fc2bbdf2 | 2026-01-11 | Merge branch 'main' into feat/deploy-hf |
| 21665b62 | 2026-01-11 | Merge pull request #6 from Kisai-DG-SLU/fix/ci-naming |
| 71d1f11e | 2026-01-11 | fix: rename CI job to match branch protection rules |
| 84c7a0ae | 2026-01-11 | feat: setup automated deployment to Hugging Face Spaces |
| b3d8e37e | 2026-01-09 | docs: overhaul README with badges, install steps and architectural overview (#2) |
| 3956a190 | 2026-01-09 | fix(ci): remove redundant python-version causing version conflict |
| 0346f97a | 2026-01-09 | test(model): add comprehensive tests for features.py and config coverage |
| 44da857e | 2026-01-09 | chore: migrate to conda, setup CI/CD, and cleanup venv |
| 7e6492d6 | 2026-01-09 | feat(tests): finalisation de la suite de tests unitaires et validation sqlite |
| 7861794f | 2026-01-09 | docs: renforcement du protocole de démarrage et log session |
| ffc27a69 | 2026-01-09 | feat(init): basic API structure with FastAPI and model loader |
| dd8da229 | 2026-01-08 | style: sanitize makefile for production |
| 7bd5cda3 | 2026-01-08 | style(makefile): fix syntax and indentation |
| b9fa6088 | 2026-01-08 | fix(makefile): include SESSION_LOG.md in brain backup |
| 3f27259f | 2026-01-08 | Merge pull request #1 from Kisai-DG-SLU/docs/init-specs |
| 29a7860e | 2026-01-08 | fix(makefile): correct save-brain command branch and robustness |
| 932203d4 | 2026-01-08 | Initial commit: Structure Guesdon Hybrid (BMAD+SpecKit) |

---
