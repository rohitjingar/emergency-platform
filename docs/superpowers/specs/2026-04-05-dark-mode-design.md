# Dark Mode Feature Design

**Date:** 2026-04-05  
**Feature:** Dark Mode for Emergency Platform

## Overview

Add dark mode support to the Emergency Platform frontend, automatically matching system preference and persisting user choice.

## Implementation Approach

### 1. Theme Context (`src/context/ThemeContext.jsx`)
- Detect system preference via `prefers-color-scheme` media query
- Store preference in localStorage (`theme` key)
- Provide `toggleTheme()` function
- Expose `theme` state and `isDark` boolean

### 2. Tailwind Configuration
```js
darkMode: 'class'
```

### 3. Color Strategy
- Use Tailwind semantic colors (`bg-gray-50`, `text-gray-900`, etc.)
- Add `dark:` prefix variants for all custom colors
- Slate gray dark scheme:
  - Light: standard Tailwind grays
  - Dark: `gray-900` background, `gray-100` text

### 4. Components to Update
| Component | Changes |
|-----------|---------|
| `Navbar.jsx` | bg-white → dark:bg-gray-900, text colors |
| `Layout.jsx` | Background color |
| `Login.jsx` | Card and form backgrounds |
| `Register.jsx` | Card and form backgrounds |
| `Card.jsx` | Default card styling |
| `Input.jsx` | Input field backgrounds |
| `Button.jsx` | Button variants |
| `Alert.jsx` | Alert type colors |
| All Dashboard pages | Consistent dark mode |

### 5. Files to Create/Modify

**Create:**
- `src/context/ThemeContext.jsx`

**Modify:**
- `tailwind.config.js` - enable darkMode
- `src/main.jsx` - wrap with ThemeProvider
- ~15 component files - add dark: variants

## Behavior

1. On first visit: use system preference
2. User can toggle via theme toggle button in Navbar
3. Choice persists in localStorage
4. Toggle button shows sun/moon icons

## Acceptance Criteria

- [ ] Dark mode matches system preference on first visit
- [ ] Theme choice persists across browser sessions
- [ ] All pages/components support dark mode
- [ ] Toggle button visible in navbar
- [ ] No flash of wrong theme on page load
