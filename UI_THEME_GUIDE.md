# WorkHub AI - UI/CSS Standardization & Theme Guide

## Overview
This guide documents the unified CSS theme system for WorkHub AI, ensuring consistent styling across all pages and modules.

---

## Theme System Architecture

### CSS Files Structure
```
static/css/
├── theme.css          # Main unified theme with CSS variables
├── style.css          # Login and general page styles
├── chatbot.css        # Chatbot widget styles
└── footer.css         # Footer styles
```

### Theme Loading Order (in HTML)
```html
<!-- Load in this order for proper cascading -->
<link rel="stylesheet" href="/static/css/theme.css">
<link rel="stylesheet" href="/static/css/style.css">
<link rel="stylesheet" href="/static/css/chatbot.css">
<link rel="stylesheet" href="/static/css/footer.css">
```

---

## CSS Variables System

### Color Variables
```css
:root {
    /* Primary Colors */
    --primary-color: #3b82f6;        /* Blue */
    --primary-dark: #2563eb;
    --primary-light: #60a5fa;
    
    /* Success Colors */
    --success-color: #22c55e;        /* Green */
    --success-dark: #16a34a;
    --success-light: #86efac;
    
    /* Warning Colors */
    --warning-color: #fbbf24;        /* Amber */
    --warning-dark: #f59e0b;
    --warning-light: #fcd34d;
    
    /* Danger Colors */
    --danger-color: #ef4444;         /* Red */
    --danger-dark: #dc2626;
    --danger-light: #fca5a5;
    
    /* Neutral Colors */
    --neutral-50: #f9fafb;
    --neutral-100: #f3f4f6;
    --neutral-200: #e5e7eb;
    --neutral-300: #d1d5db;
    --neutral-400: #9ca3af;
    --neutral-500: #6b7280;
    --neutral-600: #4b5563;
    --neutral-700: #374151;
    --neutral-800: #1f2937;
    --neutral-900: #111827;
}
```

### Spacing Variables
```css
:root {
    --spacing-xs: 4px;      /* Extra small */
    --spacing-sm: 8px;      /* Small */
    --spacing-md: 16px;     /* Medium (default) */
    --spacing-lg: 24px;     /* Large */
    --spacing-xl: 32px;     /* Extra large */
    --spacing-2xl: 48px;    /* 2x large */
}
```

### Typography Variables
```css
:root {
    /* Fonts */
    --font-primary: 'Poppins', sans-serif;
    --font-secondary: 'Inter', sans-serif;
    
    /* Font Sizes */
    --font-size-xs: 12px;
    --font-size-sm: 14px;
    --font-size-md: 16px;
    --font-size-lg: 18px;
    --font-size-xl: 20px;
    --font-size-2xl: 24px;
    --font-size-3xl: 32px;
}
```

### Border Radius Variables
```css
:root {
    --radius-sm: 4px;       /* Small corners */
    --radius-md: 8px;       /* Medium corners */
    --radius-lg: 12px;      /* Large corners */
    --radius-xl: 15px;      /* Extra large corners */
    --radius-full: 9999px;  /* Fully rounded */
}
```

### Shadow Variables
```css
:root {
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}
```

### Transition Variables
```css
:root {
    --transition-fast: 0.15s ease;
    --transition-base: 0.3s ease;
    --transition-slow: 0.5s ease;
}
```

---

## Component Styles

### Buttons

**Default Button**:
```html
<button>Click Me</button>
<button class="btn">Click Me</button>
```

**Button Variants**:
```html
<!-- Primary (default) -->
<button class="btn btn-primary">Primary</button>

<!-- Success -->
<button class="btn btn-success">Success</button>

<!-- Warning -->
<button class="btn btn-warning">Warning</button>

<!-- Danger -->
<button class="btn btn-danger">Delete</button>

<!-- Secondary -->
<button class="btn btn-secondary">Secondary</button>

<!-- Outline -->
<button class="btn btn-outline">Outline</button>
```

**Button Sizes**:
```html
<button class="btn btn-sm">Small</button>
<button class="btn">Medium (default)</button>
<button class="btn btn-lg">Large</button>
```

**Button Modifiers**:
```html
<!-- Full width -->
<button class="btn btn-block">Full Width</button>

<!-- Disabled -->
<button class="btn" disabled>Disabled</button>

<!-- With icon -->
<button class="btn"><i class="icon"></i> Button</button>
```

### Cards

**Basic Card**:
```html
<div class="card">
    <h3>Card Title</h3>
    <p>Card content goes here</p>
</div>
```

**Card Variants**:
```html
<!-- Default card (white background) -->
<div class="card">Content</div>

<!-- Dark card -->
<div class="card dark">Content</div>

<!-- Compact card (less padding) -->
<div class="card compact">Content</div>

<!-- Elevated card (more shadow) -->
<div class="card elevated">Content</div>
```

### Forms

**Form Structure**:
```html
<form>
    <div class="form-group">
        <label for="email">Email Address</label>
        <input type="email" id="email" name="email" placeholder="Enter email">
    </div>
    
    <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password">
    </div>
    
    <div class="form-group">
        <label for="message">Message</label>
        <textarea id="message" name="message"></textarea>
    </div>
    
    <button type="submit" class="btn btn-primary">Submit</button>
</form>
```

### Tables

**Table Markup**:
```html
<table>
    <thead>
        <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Status</th>
            <th>Action</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>John Doe</td>
            <td>john@example.com</td>
            <td><span class="badge badge-success">Active</span></td>
            <td><button class="btn btn-sm">Edit</button></td>
        </tr>
    </tbody>
</table>
```

### Alerts

**Alert Types**:
```html
<!-- Success -->
<div class="alert alert-success">✅ Operation successful!</div>

<!-- Warning -->
<div class="alert alert-warning">⚠️ Please review this carefully</div>

<!-- Danger -->
<div class="alert alert-danger">❌ An error occurred</div>

<!-- Info -->
<div class="alert alert-info">ℹ️ This is an information message</div>
```

### Badges

**Badge Variants**:
```html
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-danger">Danger</span>
```

---

## Utility Classes

### Text Alignment
```html
<p class="text-left">Left aligned</p>
<p class="text-center">Center aligned</p>
<p class="text-right">Right aligned</p>
```

### Text Colors
```html
<p class="text-primary">Primary text</p>
<p class="text-success">Success text</p>
<p class="text-warning">Warning text</p>
<p class="text-danger">Danger text</p>
<p class="text-muted">Muted text</p>
```

### Spacing
```html
<!-- Margin Top -->
<div class="mt-xs">Extra small margin top</div>
<div class="mt-sm">Small margin top</div>
<div class="mt-md">Medium margin top</div>
<div class="mt-lg">Large margin top</div>
<div class="mt-xl">Extra large margin top</div>

<!-- Margin Bottom -->
<div class="mb-xs">Extra small margin bottom</div>
<div class="mb-sm">Small margin bottom</div>
<div class="mb-md">Medium margin bottom</div>
<div class="mb-lg">Large margin bottom</div>

<!-- Padding -->
<div class="p-xs">Extra small padding</div>
<div class="p-sm">Small padding</div>
<div class="p-md">Medium padding</div>
<div class="p-lg">Large padding</div>
<div class="p-xl">Extra large padding</div>
```

### Display & Layout
```html
<!-- Flex utilities -->
<div class="flex">Flex container</div>
<div class="flex-center">Centered flex</div>
<div class="flex-between">Space between flex</div>
<div class="flex-column">Flex column</div>

<!-- Grid utilities -->
<div class="grid">1 column grid</div>
<div class="grid grid-2">2 column grid</div>
<div class="grid grid-3">3 column grid</div>
<div class="grid grid-4">4 column grid</div>

<!-- Visibility -->
<div class="hidden">Hidden element</div>
<div class="visible">Visible element</div>
```

### Borders & Shadows
```html
<div class="rounded">Rounded corners</div>
<div class="rounded-sm">Small rounded</div>
<div class="rounded-full">Fully rounded</div>

<div class="shadow">Medium shadow</div>
<div class="shadow-lg">Large shadow</div>
```

### Other Utilities
```html
<!-- Opacity -->
<div class="opacity-50">50% opacity</div>
<div class="opacity-75">75% opacity</div>

<!-- Cursor -->
<div class="cursor-pointer">Pointer cursor</div>
<div class="cursor-default">Default cursor</div>

<!-- Text handling -->
<div class="truncate">Long text will be truncated...</div>

<!-- Transitions -->
<div class="transition-all">Smooth all transitions</div>
<div class="transition-colors">Color transitions</div>
```

---

## Responsive Design

### Breakpoints
```css
/* Mobile First Approach */
/* Default: Mobile (< 480px) */
/* Tablet: 480px - 768px */
/* Desktop: 769px - 1200px */
/* Large: > 1200px */

@media (max-width: 480px) {
    /* Mobile styles */
}

@media (min-width: 481px) and (max-width: 768px) {
    /* Tablet styles */
}

@media (min-width: 769px) {
    /* Desktop styles */
}

@media (min-width: 1201px) {
    /* Large screen styles */
}
```

### Responsive Grid
```html
<!-- Auto-adjusts columns -->
<div class="grid grid-2">
    <div>Item 1 - 2 cols on desktop, 1 on mobile</div>
    <div>Item 2</div>
</div>
```

### Responsive Font Sizes
```css
/* Font sizes automatically adjust on mobile */
/* Defined in theme.css @media queries */
h1 { /* 32px on desktop, 24px on mobile */ }
p { /* 16px on desktop, 14px on mobile */ }
```

---

## Dark Mode Implementation

### Theme Toggle Script
```html
<script>
// Toggle dark/light mode
document.body.classList.toggle('light-mode');

// Save preference to localStorage
function toggleTheme() {
    const isDarkMode = document.body.classList.toggle('light-mode');
    localStorage.setItem('theme', isDarkMode ? 'light' : 'dark');
}

// Load saved preference
window.addEventListener('DOMContentLoaded', () => {
    const theme = localStorage.getItem('theme');
    if (theme === 'light') {
        document.body.classList.add('light-mode');
    }
});
</script>
```

### Dark Mode Classes
```css
/* Default: Dark Mode */
body {
    background: linear-gradient(135deg, var(--dark-bg-primary), var(--dark-bg-secondary));
    color: var(--dark-text-primary);
}

/* Light Mode */
body.light-mode {
    background: linear-gradient(135deg, var(--light-bg-primary), var(--light-bg-secondary));
    color: var(--light-text-primary);
}
```

---

## Common Page Patterns

### Login Page Layout
```html
<body class="employee-login">
    <div class="login-container">
        <h2>Employee Login</h2>
        <form>
            <div class="form-group">
                <label>Employee ID</label>
                <input type="text" name="employee_id" required>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Login</button>
        </form>
    </div>
</body>
```

### Dashboard Layout
```html
<div class="container">
    <div class="card">
        <h1>Dashboard Title</h1>
        <div class="grid grid-3">
            <div class="card compact">
                <h3>Stat 1</h3>
                <p>Value</p>
            </div>
            <div class="card compact">
                <h3>Stat 2</h3>
                <p>Value</p>
            </div>
            <div class="card compact">
                <h3>Stat 3</h3>
                <p>Value</p>
            </div>
        </div>
    </div>
</div>
```

### Table with Actions
```html
<div class="card">
    <h2>Employee List</h2>
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>John Doe</td>
                <td>john@company.com</td>
                <td><span class="badge badge-success">Active</span></td>
                <td>
                    <button class="btn btn-sm btn-primary">Edit</button>
                    <button class="btn btn-sm btn-danger">Delete</button>
                </td>
            </tr>
        </tbody>
    </table>
</div>
```

---

## Customization

### Changing Primary Color
```css
/* In theme.css, modify: */
:root {
    --primary-color: #your-color;
    --primary-dark: #darker-shade;
    --primary-light: #lighter-shade;
}

/* All components using --primary-color will update automatically */
```

### Adding New Colors
```css
:root {
    /* New color variable */
    --info-color: #06b6d4;
    --info-dark: #0891b2;
    --info-light: #22d3ee;
}

/* Use in CSS */
.btn-info {
    background: linear-gradient(135deg, var(--info-color), var(--info-dark));
}

/* Use in HTML */
<button class="btn btn-info">Info Button</button>
```

### Custom Component
```css
/* Add to appropriate CSS file */
.my-custom-component {
    background: var(--light-bg-primary);
    border: 1px solid var(--neutral-200);
    padding: var(--spacing-lg);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
}

.my-custom-component:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
```

---

## Browser Support

### Supported Browsers
- ✅ Chrome/Chromium (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ⚠️ IE 11 (limited support - no CSS variables)

### CSS Variable Fallback (for IE 11)
```css
.button {
    /* Fallback color for IE 11 */
    background: #3b82f6;
    
    /* CSS variables for modern browsers */
    background: var(--primary-color);
}
```

---

## Performance Optimization

### CSS Minification
```bash
# Use a CSS minifier in production
npm install cssnano postcss

# Or use online tool: https://cssnano.co/playground/
```

### Critical CSS
```html
<!-- Load critical CSS inline -->
<style>
    /* Critical styles for above-the-fold content */
    body, .card, button { ... }
</style>

<!-- Load remaining CSS asynchronously -->
<link rel="preload" href="/static/css/theme.css" as="style">
<link rel="stylesheet" href="/static/css/theme.css">
```

### Image Optimization
```html
<!-- Use modern image formats -->
<picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="description">
</picture>
```

---

## Testing & QA

### Cross-Browser Testing
- Test on Chrome, Firefox, Safari, Edge
- Test dark mode and light mode
- Test on mobile, tablet, desktop
- Test all form inputs and buttons
- Test responsive breakpoints

### Accessibility Testing
```html
<!-- Use semantic HTML -->
<button>Click me</button>  <!-- ✅ Good -->
<div onclick="...">Click</div>  <!-- ❌ Bad -->

<!-- Proper labels -->
<label for="email">Email</label>
<input id="email" type="email">

<!-- Color contrast -->
<!-- Ensure text is readable (AA 4.5:1 ratio) -->

<!-- Keyboard navigation -->
<!-- All interactive elements should be keyboard accessible -->
```

---

## Best Practices

### CSS Organization
1. ✅ Use CSS variables for consistency
2. ✅ Group related styles together
3. ✅ Use utility classes for common patterns
4. ✅ Avoid inline styles
5. ✅ Use semantic HTML
6. ✅ Follow BEM naming (optional)
7. ✅ Keep specificity low
8. ✅ Comment complex styles

### HTML Best Practices
1. ✅ Use semantic HTML5 elements
2. ✅ Ensure proper heading hierarchy
3. ✅ Include alt text on images
4. ✅ Use proper form labels
5. ✅ Include ARIA attributes where needed
6. ✅ Use meta viewport tag
7. ✅ Optimize images

### JavaScript Integration
```html
<!-- Load critical JS at end of body -->
<script src="/static/js/main.js" defer></script>

<!-- Use defer for non-critical JS -->
<script src="/static/js/analytics.js" defer></script>
```

---

## Resources

- [CSS Variables MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)
- [Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
- [Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
- [Web Accessibility](https://www.w3.org/WAI/WCAG21/quickref/)
- [Color Contrast Checker](https://webaim.org/resources/contrastchecker/)

---

**Last Updated**: June 2026
**Version**: 1.0.0
