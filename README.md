# PG del Campo — Paquete para publicar

Sitio listo para publicar (por ejemplo en **GitHub Pages**) con las tres aplicaciones del negocio.

## Contenido

| Archivo | Descripción | Conexión |
|---|---|---|
| `index.html` | Portal de entrada con enlaces a las tres apps | Sin internet |
| `panel.html` | Panel Administrativo (Inicio + Promociones editables) | Interfaz **sin internet** (usa `vendor/`); la base de datos Firebase sí requiere conexión |
| `tienda.html` | Tienda en Línea para clientes (con pantalla de bienvenida y todas las promociones) | Requiere internet |
| `tarjeta-fidelidad.html` | Club de clientes frecuentes (estrellas, premios) | Requiere internet |
| `vendor/` | Librerías locales del panel: Tailwind, Chart.js, QRCode, Font Awesome y fuentes Google | — |
| `.nojekyll` | Evita que GitHub Pages ignore carpetas | — |

## Versión offline del panel

El `panel.html` ya no depende de CDNs para su interfaz: todas las librerías están
dentro de la carpeta `vendor/` y se cargan de forma local. Puede abrirse con doble
clic incluso sin conexión y la interfaz se verá correctamente.

> Nota: la **base de datos** (Firebase Realtime Database) siempre necesita internet
> para leer y guardar datos reales — eso no puede funcionar sin conexión porque es
> un servicio en la nube. Sin internet, la interfaz carga pero no habrá datos.

## Novedades de esta versión

- **Entrega de pedidos con destino contable.** En el panel, al pulsar **Entregar** un
  pedido (en *Inicio* o *Pedidos*) se elige la forma de entrega:
  - **Contado** → el monto entra directamente a **Ingresos** (Ventas y Transacciones).
  - **Crédito** → el **abono inicial** entra a **Ingresos** y el **saldo restante**
    pasa a **Cuentas por Cobrar** del cliente.
  Una vez entregado, el pedido **desaparece de Inicio y de Pedidos** y no vuelve a
  aparecer (queda guardado localmente, así que se mantiene aunque se recargue la página).
- **El ingreso ya no se registra al llegar el pedido**, sino únicamente cuando se
  **entrega** (al contado o con abono). Así los pedidos pendientes no inflan los ingresos.
- **"Factura" en lugar de "Recibo".** La Tienda en Línea y la Tarjeta de Fidelidad ahora
  emiten una **Factura** al cliente.
- **El "Recibo" queda reservado para los abonos** de facturas a crédito: se genera un
  recibo de abono desde la ventana *Entregar pedido n.º xxxxx* y también al registrar un
  abono desde **Cuentas por Cobrar**.

## Reinicio desde cero

Este paquete viene **sin datos de ejemplo**: no hay clientes, ventas, recibos, pedidos
ni gastos de demostración. El panel arranca limpio y se va llenando con la operación real
(pedidos de la nube y ventas del Punto de Venta).

> **Importante:** ya **no se cargan productos de ejemplo automáticamente**. Antes, el panel
> reinyectaba un catálogo demo a la nube cuando estaba vacío (por eso “siempre cargaba
> datos”). Eso quedó **desactivado**. Ahora el catálogo se llena solo con los productos
> reales que usted cree con **“Nuevo producto”** y publique con **“Publicar a Tienda y
> Tarjeta”**.

### Botón “Reiniciar desde cero” (recomendado)

En el panel, entra a **Catálogo** y usa el botón rojo **“Reiniciar desde cero”**. Con dos
confirmaciones borra de una sola vez **todos** los datos de prueba — tanto en este panel
como en la **Tienda en Línea** y la **Tarjeta de Fidelidad** (Firebase): productos,
clientes, pedidos, ventas, transacciones, cuentas por cobrar y los contadores de
numeración. También limpia los datos guardados en el navegador y recarga la página.

> ⚠️ Es una acción **destructiva y no reversible**, y afecta a las tres aplicaciones a la
> vez. Úselo solo cuando de verdad quiera empezar de cero.

### Alternativa manual: borrar en la consola de Firebase

Para empezar completamente desde cero, borra estos nodos en tu **Firebase Realtime
Database** (consola de Firebase → *Realtime Database* → selecciona el nodo → menú **⋮ →
Eliminar**, o pon su valor en `null`):

- `transacciones`
- `compras_registro`
- `cuentas_por_cobrar`
- `clientes` (solo si quieres borrar también los clientes de prueba)
- `meta/contador_recibo` y/o `secuencia_recibos` (contadores de numeración; ponlos en el
  valor inicial que desees, p. ej. `1000`)

> Los **productos** (`productos`) normalmente **NO** se borran: son tu catálogo real.

### Limpiar los datos guardados en el navegador (panel)

El panel guarda las entregas confirmadas en el navegador. Para reiniciarlas, abre el
panel, pulsa **F12 → Console** y ejecuta `localStorage.clear()`, o borra los datos del
sitio desde la configuración del navegador. Luego recarga la página.

## Cómo publicar en GitHub Pages

1. Sube todo el contenido de esta carpeta a la raíz de tu repositorio.
2. En GitHub: **Settings → Pages**.
3. En *Source* elige la rama (por ejemplo `main`) y la carpeta **/ (root)**.
4. Guarda. En unos minutos el sitio quedará en `https://TU-USUARIO.github.io/TU-REPO/`.
5. La página de inicio será `index.html` (el portal).

## Reglas de promociones (referencia)

- **Descuento por monto:** 1% ≥ C$600 · 2% ≥ C$1,200 · 3% ≥ C$1,800
- **Premio de fidelidad:** 2% adicional en la 10.ª compra
- **Puntos:** 1 estrella por cada C$20 de compra
- **Envíos:** domicilio C$20 (Jinotepe, Dolores, Diriamba, San Marcos; otras zonas a convenir) · comercios gratis · empresas C$20 (retención 2% I.R. en compras mayores a C$1,000)

## ⚠️ Seguridad antes de producción

- **Cambia las credenciales demo** del panel (`admin` / `1234`).
- En un repositorio **público**, la configuración de Firebase queda visible en el HTML.
  Activa las **reglas de seguridad de Firebase** y **restringe la API key por dominio**
  desde Google Cloud Console.
