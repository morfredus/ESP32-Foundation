# ESP32-Foundation

Framework applicatif générique pour projets ESP32 (PlatformIO / Arduino),
extrait et généralisé à partir de **Gateway Lab V1** et **MeteoHub-S3**.

ESP32 Foundation est un framework d'applications réutilisable, issu de
projets ESP32 concrets tels que Gateway Lab et MeteoHub. Il fournit des
services communs comme la gestion du Wi-Fi, les mises à jour OTA, la
journalisation, le stockage, une interface web, le routage API et des outils
de compilation, permettant ainsi aux nouveaux projets de se concentrer sur
les fonctionnalités spécifiques à leur application.

Ce framework n'a pas été conçu en premier. Il a été extrait ultérieurement
de plusieurs projets ESP32 après avoir identifié les composants qui étaient
fréquemment réutilisés.

Le framework fournit l'infrastructure commune à tout projet ESP32 connecté
(WiFi, serveur web, logs, OTA, stockage, configuration persistante,
informations système, mDNS, heure réseau) à travers un système de **modules**
optionnels : le framework ne connaît jamais le code métier, le métier ne
connaît jamais l'implémentation des services.

## Structure

```
ESP32-Foundation/
├── include/            project_config.h, board_config.h, secrets_example.h
├── src/
│   ├── core/           App, Module, ModuleManager
│   ├── services/       wifi, web, ota, storage, config, log, system_info, mdns, time
│   ├── api/            api_router (WebRouter)
│   ├── modules/         exemple de module métier
│   └── main.cpp
├── data/               interface web (HTML/CSS/JS) servie depuis LittleFS
├── tools/              build_info.py, minify_web.py, version_generator.py, package_web.py, release.py
├── docs/               ARCHITECTURE.md, INTEGRATION_GUIDE.md
└── examples/           example_project, minimal, sensor, api
```

## Démarrage rapide

```bash
cp include/secrets_example.h include/secrets.h   # WiFi de développement (optionnel)
pio run                                            # compile le firmware
pio run --target uploadfs                          # flashe data/ (interface web)
pio run --target upload                            # flashe le firmware
```

Important : exécuter `pio run -t uploadfs` au moins une fois après le tout
premier flash (et à chaque modification de `data/`) — sans cette étape,
l'interface web LittleFS est vide et toute page renvoie une page blanche ou
une erreur 404, même si le firmware fonctionne correctement. Voir l'explication
détaillée dans
[docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md#téléverser-linterface-web-littlefs--éviter-la-page-blanche-au-premier-démarrage).

Pour changer le nom du projet (logs, `/api/system`, interface web), voir la
section [Renommer le projet](docs/INTEGRATION_GUIDE.md#renommer-le-projet)
du guide d'intégration.

Voir [docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) pour démarrer un
nouveau projet, et [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) pour le détail
des choix de conception et leur origine (Gateway Lab / MeteoHub).

## Exemples fournis

| Exemple | Description |
|---|---|
| `examples/example_project/` | Module "Blink" minimal pilotant la LED embarquée — exemple historique de référence. |
| `examples/minimal/` | Le module le plus simple possible : cycle de vie `begin()/loop()` uniquement, sans capteur ni route HTTP. À lire en premier. |
| `examples/sensor/` | Lecture périodique d'une valeur simulée, intervalle de lecture configurable et persistant, route HTTP `GET /api/sensor/value`. |
| `examples/api/` | Trois routes HTTP de démonstration via `WebRouter` : GET simple, GET avec paramètre de requête, POST avec corps JSON et validation. |

Chaque exemple est un projet PlatformIO autonome (voir son propre
`platformio.ini`, qui référence le framework via `lib_extra_dirs = ../../`).
Le guide complet, pas à pas, pour créer son propre module à partir de ces
exemples se trouve dans
[docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md#créer-son-premier-module-pas-à-pas).

## Services fournis

| Service          | Rôle                                                         |
|-------------------|---------------------------------------------------------------|
| `wifiMgr`         | Multi-réseaux NVS, portail captif de secours, reconnexion auto |
| `webMgr`          | Serveur HTTP : `/`, `/logs`, `/files`, `/system`, `/ota`        |
| `otaMgr`          | Mise à jour firmware (ArduinoOTA + upload web)                |
| `storage`         | Fichiers LittleFS (lecture/écriture/liste/suppression)         |
| `config`          | Réglages persistants clé/valeur (NVS)                          |
| `logMgr`          | Logs série + tampon JSON (`LOG_INFO`, `LOG_ERROR`, ...)         |
| `systemInfo`      | État système en JSON (heap, version, WiFi, build...)           |
| `mdnsMgr`         | Résolution `http://<hostname>.local`                            |
| `timeMgr`         | Synchronisation NTP                                              |

Aucune dépendance métier n'est imposée : chaque service est utilisable
indépendamment des autres.
