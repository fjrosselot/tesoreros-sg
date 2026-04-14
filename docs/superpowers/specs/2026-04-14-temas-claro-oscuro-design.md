# Diseño: Sistema de Temas Claro/Oscuro

**Fecha:** 2026-04-14  
**Versión app:** v2.10+  
**Estado:** Aprobado

---

## Descripción

Agregar soporte de tema claro y oscuro con toggle manual. El usuario elige su preferencia y se persiste en `localStorage`. El tema oscuro reemplaza el actual (negro puro) por un slate azulado más suave.

---

## Temas

### Modo oscuro (default)
```css
--bg: #161e2e;
--surface: #1e2a3e;
--surface2: #253347;
--border: #2d3f5c;
--border2: #354a6e;
--text: #e2e8f5;
--muted: #7a90b0;
--subtle: #2d3f5c;
--navy: #4f7ef8;
--navy-dim: rgba(79,126,248,.15);
--navy-light: #7aa0fa;
--green: #34d399;
--green-dim: rgba(52,211,153,.15);
--yellow: #fbbf24;
--yellow-dim: rgba(251,191,36,.15);
--red: #f87171;
--r: 10px; --r-lg: 14px;
```

### Modo claro
```css
--bg: #f1f5f9;
--surface: #ffffff;
--surface2: #f8fafc;
--border: #e2e8f0;
--border2: #cbd5e1;
--text: #1a2340;
--muted: #64748b;
--subtle: #e2e8f0;
--navy: #2d5be3;
--navy-dim: rgba(45,91,227,.08);
--navy-light: #2d5be3;
--green: #16a34a;
--green-dim: rgba(22,163,74,.1);
--yellow: #d97706;
--yellow-dim: rgba(217,119,6,.1);
--red: #dc2626;
--r: 10px; --r-lg: 14px;
```

---

## Toggle UI

### Desktop (sidebar)
Al pie del sidebar, entre la lista de navegación y el botón de salir:
```
☀️  [○────]  🌑
```
- Click en el switch cambia el tema y actualiza `localStorage`

### Móvil (header)
Ícono ☀️/🌑 en el extremo derecho del header móvil, antes del botón de salir.

---

## Persistencia

- Key: `localStorage.getItem("theme")` → `"light"` | `"dark"`
- Default: `"dark"` (si no hay preferencia guardada)
- Al cargar la app (`DOMContentLoaded`): leer key y aplicar clase al `<body>` antes de cualquier render

---

## Implementación técnica

### CSS
Reemplazar `:root { ... }` con:
```css
body.theme-dark { /* variables dark */ }
body.theme-light { /* variables light */ }
```

### JS — función `applyTheme(theme)`
```js
function applyTheme(theme) {
  document.body.classList.remove("theme-dark", "theme-light");
  document.body.classList.add("theme-" + theme);
  localStorage.setItem("theme", theme);
  window._currentTheme = theme;
}
```

### Init en DOMContentLoaded
```js
var savedTheme = localStorage.getItem("theme") || "dark";
applyTheme(savedTheme);
```

### Toggle HTML — sidebar desktop
Agregado dentro de `.sidebar-footer`, antes del botón de salir:
```html
<div class="theme-toggle" onclick="applyTheme(window._currentTheme==='dark'?'light':'dark')">
  <span>☀️</span>
  <div class="toggle-track"><div class="toggle-thumb"></div></div>
  <span>🌑</span>
</div>
```

### Toggle HTML — header móvil
Botón ícono en `.mob-header` a la derecha:
```html
<button id="mob-theme-btn" onclick="applyTheme(window._currentTheme==='dark'?'light':'dark')" ...>☀️</button>
```
El ícono se actualiza con `applyTheme`.

---

## Fuera de Alcance

- Detección automática del tema del sistema (`prefers-color-scheme`)
- Temas adicionales (más de dos)
- Configuración por usuario en Firebase
