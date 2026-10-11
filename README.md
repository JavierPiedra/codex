# Codex personal de Javier

La fuente canónica de las skills personales es `plugins/javier/skills/`.
El plugin `javier` contiene las skills seleccionadas y se invoca como
`$javier:write-goal`, `$javier:idea-council`, etc. Las referencias a proveedores
externos, como `$awra:prd` e Image Gen, conservan su proveedor.

Las skills excluidas permanecen en el historial y en `skills/`, pero no
forman parte del plugin. El catálogo actual está en `scripts/skill-catalog.json`.
La selección histórica de la migración y las huellas de las copias anteriores
permanecen en `scripts/migration.json`.

## Qué instala cada parte

El marketplace `.agents/plugins/marketplace.json` distribuye únicamente el
plugin. El setup explícito instala `AGENTS.md`, las políticas y perfiles de
agentes y la referencia de revisión externa en el Codex home de
cada equipo. Estas instrucciones globales no se activan por instalar el plugin.

`scripts/setup.py --with-runtime` crea un entorno Python bajo
`<codex_home>/javier-runtime` con `keyring`, `tzdata` y validación JSON Schema/fechas,
y registra su ejecutable
en `javier-paths.toml`. Python 3.11 o posterior es necesario para el setup;
se ha preparado para el Python 3.12 suministrado por la app. Cada equipo conserva
su configuración, permisos, autenticación y conexiones. No se distribuyen
credenciales ni se modifican los runtimes de la app.

## Instalación

Usar `main` para el marketplace y para la copia de fuente del setup. Actualizar
ambos al mismo commit antes de ejecutar el setup; no mezclar versiones.

Si `codex` no está en PATH, usar el ejecutable suministrado por la app. En Windows,
el agente del equipo debe localizar ese ejecutable; no asumir que está instalado
el CLI de forma independiente. Los siguientes comandos muestran sus argumentos:

```text
codex plugin marketplace add JavierPiedra/codex --ref main
codex plugin add javier@javier
```

En la copia de fuente, hacer checkout del mismo commit. Revisar primero el setup:

```text
<app-python> scripts/setup.py --dry-run
<app-python> scripts/setup.py --with-runtime
```

En PowerShell, ejecutar rutas con espacios mediante el operador `&`:

```powershell
& $codexCli plugin marketplace add JavierPiedra/codex --ref main
& $codexCli plugin add javier@javier
& $appPython '.\scripts\setup.py' --dry-run
& $appPython '.\scripts\setup.py' --with-runtime
```

`$codexCli` y `$appPython` son variables locales con los ejecutables observados
en ese equipo. No cambiar `HOME`, `CODEX_HOME` ni el sandbox para instalar.
El home se toma de `CODEX_HOME` si ya existe; en otro caso se usa el home del
usuario más `.codex`. `--codex-home` permite probar en un directorio aislado.

El setup conserva una copia de cada archivo global que reemplaza en
`<codex_home>/javier-setup-backups/`. Si existe `AGENTS.override.md`, se detiene
antes de escribir para resolver qué instrucciones deben aplicarse.
Si Codex home también es un checkout Git, el setup se detiene cuando tendría
que cambiar archivos versionados. Actualizar primero ese checkout al commit de
la fuente y reconciliar sus cambios locales; el setup solo debe escribir allí
el archivo de rutas del equipo y otros archivos no versionados.

## Fuentes y herramientas de cada equipo

Los flujos Awra requieren sus fuentes locales. Registrar únicamente ubicaciones
que existan con `--awra-guidance-root` y `--awra-voice-root`. En Windows no se
han identificado todavía esas ubicaciones; las skills y el perfil deben indicar
la fuente faltante cuando sea necesaria. El plugin Awra y los conectores se
instalan y autentican por separado.

WakaTime usa el Keychain nativo en Mac y Windows Credential Locker en Windows.
La clave se registra una vez por equipo con `--store-key` del helper, mediante
un prompt oculto. El servicio sigue siendo `codex.invoice-goodancestor.wakatime`
y la cuenta corresponde al usuario local. Nunca pasar la clave como argumento.

`$javier:exa-deep-search` aparece como **Javier: Exa Deep Search**. Usa el mismo
runtime con `keyring`, con una entrada independiente: servicio
`codex.javier.exa-deep-search`, cuenta `api-key`. Ejecutar su helper
`plugins/javier/skills/exa-deep-search/scripts/exa_deep_search.py` con el Python
registrado y `setup` en un terminal local para introducir la clave de forma oculta;
`update` la reemplaza y `remove` elimina solo la credencial local. Estas órdenes
no llaman a Exa. No pasar la clave en argumentos, archivos ni variables de entorno.

Para una búsqueda autorizada, usar `search "<pregunta>" --mode deep` o
`--mode deep-reasoning`. Devuelve fuentes y el coste estimado reportado por la API
cuando existe. `--synthesize` añade texto generado con grounding y `--retries 0`
limita la búsqueda a un intento. No ejecuta Exa Agent ni cambia a búsqueda ordinaria.
Las búsquedas consumen créditos y requieren autorización; la configuración no las
ejecuta. Ver [la skill](plugins/javier/skills/exa-deep-search/SKILL.md) para los límites.
Para todas las opciones de Search compatibles con los dos modos profundos, usar
`search --request-file <request.json>` con los nombres camelCase de la API.
`--dry-run` valida el archivo sin leer credenciales ni llamar a Exa. La
[referencia de opciones](plugins/javier/skills/exa-deep-search/references/api-options.md)
incluye fechas, contenido, frescura, esquemas, filtros, ubicación, SSE y beta de
highlights. Actualizar el runtime con `scripts/setup.py --with-runtime` al adoptar
esta versión. Snapshot e HIPAA son incompatibles con estos modos y se rechazan.

Por decisión de Javier, `whatsapp-group-review` conserva la base local de macOS.
Se incluye en ambos catálogos, pero en Windows se detiene con
`UNSUPPORTED_PLATFORM`. La fuente Windows se definirá por separado.

Las skills que dependen de herramientas de la app, conectores, un modelo o un
perfil deben comprobar su disponibilidad en la sesión concreta. Instalar los
archivos no demuestra acceso al servicio ni disponibilidad del modelo.

## Comprobación y actualización

Abrir un chat nuevo después de instalar. Comparar las skills registradas y
habilitadas con `scripts/skill-catalog.json`; comprobar el
namespace `javier:*`, los recursos asociados y los perfiles. Las skills con
`allow_implicit_invocation: false` no aparecen en el contexto inicial del
chat; comprobar su invocación en el selector de skills por separado.
Comprobar también que los textos globales corresponden a esta fuente antes de
retirar las copias anteriores. Si el catálogo omite una skill, investigar la
causa antes de retirar su copia anterior; la existencia del directorio no
demuestra que la app la ofrezca.

Los checks del repositorio usan datos sintéticos y no consultan credenciales,
mensajes, historiales reales ni proveedores:

```text
python -m pip install -r scripts/requirements-dev.txt -r plugins/javier/requirements.txt
python scripts/check.py
python -m unittest discover -s scripts -p 'test_*.py' -v
python scripts/runtime_check.py
```

Ejecutar estos checks en un entorno de desarrollo aislado. GitHub Actions los
ejecuta con Python 3.12 en macOS y Windows; sus resultados no sustituyen la
comprobación del catálogo en las apps reales.

Para actualizar, refrescar el marketplace Git, reinstalar el plugin y actualizar
la copia de fuente al mismo commit antes de reejecutar el setup:

```text
codex plugin marketplace upgrade javier
codex plugin add javier@javier
```

## Retirar las copias anteriores

Solo después de verificar ambos equipos, ejecutar en cada uno:

```text
<app-python> scripts/setup.py --retire-local-skills --installed-plugin <observed-plugin-path> --dry-run
<app-python> scripts/setup.py --retire-local-skills --installed-plugin <observed-plugin-path>
```

El script verifica que el paquete instalado coincida con esta fuente y mueve
únicamente las copias personales seleccionadas, sin cambios locales, a un backup
privado. No toca las skills excluidas. Si alguna copia difiere —también por CRLF—,
se detiene antes de mover cualquier skill; revisar y reconciliar esa diferencia.
No normalizar archivos automáticamente para ocultar cambios.

En Mac, Codex home también es la copia Git activa. El pull de esta migración
elimina las antiguas rutas de skills versionadas. Verificar primero el plugin
en ambos equipos y archivar esas copias con `--retire-local-skills`. Después,
revisar `git -C <codex_home> status --short` y reconciliar cualquier otro cambio
versionado sin descartar ediciones propias. Actualizar con
`git -C <codex_home> pull --ff-only origin main` y ejecutar el setup desde esa
misma revisión. Git admite las eliminaciones locales de skills si coinciden
con las del commit entrante; cualquier diferencia requiere revisión manual.

## Referencias del formato

- [Plugins y marketplaces de Codex](https://developers.openai.com/plugins/build/plugins)
- [Instrucciones AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Almacenes nativos de keyring](https://keyring.readthedocs.io/en/latest/)
