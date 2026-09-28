# Volumen: cómo montarla gratis en tu móvil

Todo lo de esta guía es gratis. Tardarás unos 30–40 minutos la primera vez.

Qué hay en la carpeta:

| Archivo | Para qué sirve |
|---|---|
| `index.html` | La app entera |
| `productos.json` | Productos reales de Mercadona (ids, nombres, precios) |
| `actualizar_productos.py` | Script que actualiza precios y nutrición cada semana |
| `.github/workflows/actualizar-precios.yml` | Lanza el script solo cada domingo |
| `supabase.sql` | Crea tu base de datos y la protege |
| `manifest.webmanifest`, `sw.js`, iconos | Para que se instale como app y abra sin cobertura |

---

## 1. Base de datos en Supabase

1. Crea una cuenta en **supabase.com** y pulsa **New project**. Ponle de nombre `volumen`, inventa una contraseña para la base de datos (guárdala) y elige una región de Europa (Frankfurt o París).
2. Cuando termine de crearse, ve a **SQL Editor → New query**, pega todo el contenido de `supabase.sql` y pulsa **Run**. Debe decir *Success*.
3. Ve a **Authentication → Sign In / Providers → Email** y desactiva **Confirm email**. Así no tendrás que confirmar tu correo (es una app solo para ti).
4. Ve a **Project Settings → API Keys** (o **Data API**) y copia dos cosas:
   - la **Project URL** (tipo `https://abcdefgh.supabase.co`)
   - la clave **publishable** o **anon** (la pública). **Nunca** uses la `service_role` o `secret`.
5. Abre `index.html` con cualquier editor de texto (el Bloc de notas vale), busca estas dos líneas al principio del script y pega tus datos entre las comillas:

```js
const SUPABASE_URL="PEGA_AQUI_TU_PROJECT_URL";
const SUPABASE_KEY="PEGA_AQUI_TU_CLAVE_PUBLICA";
```

La clave pública puede estar en el código sin problema: las reglas de seguridad de `supabase.sql` hacen que cada usuario solo pueda ver sus propios datos y fotos.

## 2. Publicar la web en GitHub Pages

Usamos GitHub porque, además de alojar la web gratis, ejecuta cada semana el script que actualiza los precios.

1. Crea una cuenta en **github.com** y pulsa **New repository**. Nombre: `volumen`. Márcalo como **Public** (GitHub Pages gratis solo funciona con repositorios públicos; tu código será visible, pero tus datos personales y fotos están en Supabase, no ahí).
2. En el repositorio, pulsa **Add file → Upload files** y arrastra todos los archivos de la carpeta.
3. La carpeta `.github` a veces no se sube arrastrando porque está oculta. Si no aparece, pulsa **Add file → Create new file**, escribe como nombre `.github/workflows/actualizar-precios.yml` y pega dentro el contenido de ese archivo.
4. Ve a **Settings → Pages**. En *Source* elige **Deploy from a branch**, rama `main`, carpeta `/ (root)`, y guarda. En un par de minutos tendrás tu app en `https://TU-USUARIO.github.io/volumen/`.
5. Ve a **Settings → Actions → General**, baja a *Workflow permissions*, marca **Read and write permissions** y guarda.
6. Ve a la pestaña **Actions**, elige *Actualizar precios y nutrición* y pulsa **Run workflow** para probarlo. Si sale en verde, `productos.json` ya tiene precios del día. A partir de ahora se ejecuta solo cada domingo.
7. Vuelve a Supabase, **Authentication → URL Configuration**, y pon tu dirección de GitHub Pages como **Site URL**.

## 3. Crear tu cuenta y cerrar la puerta

1. Abre tu dirección en el móvil, pulsa **Crear cuenta** con tu email y una contraseña. Rellena tu perfil y haz el check-in inicial.
2. En Supabase, ve a **Authentication → Sign In / Providers** y desactiva **Allow new users to sign up**. Así nadie más puede registrarse en tu app.

## 4. Instalarla en el móvil

**Opción rápida (recomendada):** en Chrome, abre tu dirección, menú ⋮ → **Instalar app** o **Añadir a pantalla de inicio**. Tendrás icono propio y se abre a pantalla completa, sin barra del navegador.

**Opción APK:**
1. Entra en **pwabuilder.com**, pega tu dirección y pulsa **Start**.
2. Pulsa **Package for stores → Android → Generate** y descarga el zip.
3. Dentro hay un archivo `.apk`. Pásalo al móvil, ábrelo y acepta *instalar apps de origen desconocido*.
4. Guarda también el archivo de firma (`signing.keystore` y su contraseña) que viene en el zip: lo necesitarás si algún día quieres generar una versión nueva del APK que se instale encima.

La app funciona con tus datos móviles en cualquier sitio. Sin cobertura se abre igualmente y guarda lo que hagas en el móvil; lo sube a Supabase cuando vuelve la conexión. Las fotos sin conexión se guardan en pequeño solo en el móvil.

---

## De dónde salen los productos y los precios

- **Productos y precios de Mercadona:** API pública (no oficial) de la tienda online, documentada en el proyecto [datania/mercadona-catalog](https://github.com/datania/mercadona-catalog). El `productos.json` inicial viene de su catálogo, y el script pide cada domingo solo los ~35 productos de tu plan, uno por segundo.
- **Valores nutricionales:** [Open Food Facts](https://world.openfoodfacts.org), base de datos abierta. El script busca cada producto por su código de barras y solo acepta los datos si las calorías cuadran con los macros. Si no encuentra el producto, la app usa los valores genéricos que ya trae.
- **Consum:** no tiene un catálogo abierto equivalente, así que ahí los precios siguen siendo una estimación.

**Cambiar un producto:** abre el producto en tienda.mercadona.es; el número de la dirección (`/product/18018/...`) es su id. Cámbialo en `productos.json` y lanza la Action a mano.

## Cosas a tener en cuenta

- **Pausa de Supabase:** los proyectos gratis se pausan si pasan 7 días sin uso. Si te pasa, entra en supabase.com y pulsa *Restore*; los datos no se pierden.
- **La API de Mercadona no es oficial.** Su `robots.txt` pide que los robots no la usen, y puede cambiar o bloquear las peticiones en cualquier momento. Para uso personal, una vez por semana y con pocas peticiones, el impacto es mínimo, pero es decisión tuya. Si un día falla, la app sigue funcionando con los últimos precios guardados.
- **Actualizar la app:** cambia los archivos en GitHub. En el móvil, cierra y abre la app dos veces para que coja la versión nueva.
- **Esta app no sustituye a un médico o dietista-nutricionista.**
