# Codex personal de Javier

La fuente canónica de las skills personales es `plugins/javier/skills/`.
El plugin `javier` contiene las 31 skills seleccionadas y se invoca como
`$javier:write-goal`, `$javier:idea-council`, etc. Las referencias a proveedores
externos, como `$awra:prd` e Image Gen, conservan su proveedor.

Las diez skills excluidas permanecen en el historial y en `skills/`, pero no
forman parte del plugin. La selección exacta y las huellas de las copias
anteriores están en `scripts/migration.json`.

## Qué instala cada parte

El marketplace `.agents/plugins/marketplace.json` distribuye únicamente el
plugin. El setup explícito instala `AGENTS.md`, las dos políticas de agentes,
los siete perfiles y la referencia de revisión externa en el Codex home de
cada equipo. Estas instrucciones globales no se activan por instalar el plugin.

`scripts/setup.py --with-runtime` crea un entorno Python bajo
`<codex_home>/javier-runtime` con `keyring` y `tzdata`, y registra su ejecutable
en `javier-paths.toml`. Python 3.11 o posterior es necesario para el setup;
se ha preparado para el Python 3.12 suministrado por la app. Cada equipo conserva
su configuración, permisos, autenticación y conexiones. No se distribuyen
credenciales ni se modifican los runtimes de la app.

## Instalación de la versión candidata

Esta rama prepara la versión 1.0.0. Hasta que se integre en `main`, usar
`feature/codex/personal-skills-plugin` como referencia tanto para el marketplace
como para la copia de fuente del setup. No mezclar una instalación de una rama
con un setup de otra.

Si `codex` no está en PATH, usar el ejecutable suministrado por la app. En Windows,
el agente del equipo debe localizar ese ejecutable; no asumir que está instalado
el CLI de forma independiente. Los siguientes comandos muestran sus argumentos:

```text
codex plugin marketplace add JavierPiedra/codex --ref feature/codex/personal-skills-plugin
codex plugin add javier@javier
```

En la copia de fuente, hacer checkout de la misma rama. Revisar primero el setup:

```text
<app-python> scripts/setup.py --dry-run
<app-python> scripts/setup.py --with-runtime
```

En PowerShell, ejecutar rutas con espacios mediante el operador `&`:

```powershell
& $codexCli plugin marketplace add JavierPiedra/codex --ref feature/codex/personal-skills-plugin
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

Por decisión de Javier, `whatsapp-group-review` conserva la base local de macOS.
Se incluye en ambos catálogos, pero en Windows se detiene con
`UNSUPPORTED_PLATFORM`. La fuente Windows se definirá por separado.

Las skills que dependen de herramientas de la app, conectores, un modelo o un
perfil deben comprobar su disponibilidad en la sesión concreta. Instalar los
archivos no demuestra acceso al servicio ni disponibilidad del modelo.

## Comprobación y actualización

Abrir un chat nuevo después de instalar. Verificar las 31 entradas `javier:*`,
sus recursos asociados y los siete perfiles. Comprobar que los textos globales
corresponden a esta fuente. Si el catálogo omite una skill, investigar la causa
antes de retirar su copia anterior; la existencia del directorio no demuestra
que la app la ofrezca.

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
la copia de fuente al mismo commit antes de reejecutar el setup. Después de
integrar la versión candidata, usar `main` como referencia del marketplace:

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

La copia de fuente en Mac es también el Codex home activo. Hacer pull de esta
migración en esa copia elimina del árbol las 31 rutas anteriores; por ello,
integrarla allí solo después de validar ambos catálogos y el retiro. La copia
aislada de trabajo y el plugin instalado permiten verificar antes de ese paso.

## Referencias del formato

- [Plugins y marketplaces de Codex](https://developers.openai.com/plugins/build/plugins)
- [Instrucciones AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Almacenes nativos de keyring](https://keyring.readthedocs.io/en/latest/)
