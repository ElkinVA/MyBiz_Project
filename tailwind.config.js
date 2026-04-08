// ./tailwind.config.js
module.exports = {
  mode: 'jit',
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary, #3b82f6)',
        secondary: 'var(--color-secondary, #8b5cf6)',
        accent: 'var(--color-accent, #10b981)',
        'hero-bg': 'var(--color-hero-bg, #eff6ff)',
        'header-bg': 'var(--color-header-bg, #ffffff)',
        'footer-bg': 'var(--color-footer-bg, #111827)',
        'text-default': 'var(--color-text, #1f2937)',
        'bg-default': 'var(--color-background, #f9fafb)',
        'border-default': 'var(--color-border, #e5e7eb)', // если добавим потом, пока fallback
      },
      backgroundColor: {
        primary: 'var(--color-primary, #3b82f6)',
        secondary: 'var(--color-secondary, #8b5cf6)',
        accent: 'var(--color-accent, #10b981)',
        'header-bg': 'var(--color-header-bg, #ffffff)',
        'footer-bg': 'var(--color-footer-bg, #111827)',
        'hero-bg': 'var(--color-hero-bg, #eff6ff)',
        'default': 'var(--color-background, #f9fafb)',
      },
      textColor: {
        primary: 'var(--color-primary, #3b82f6)',
        secondary: 'var(--color-secondary, #8b5cf6)',
        accent: 'var(--color-accent, #10b981)',
        default: 'var(--color-text, #1f2937)',
      },
      borderColor: {
        primary: 'var(--color-primary, #3b82f6)',
        secondary: 'var(--color-secondary, #8b5cf6)',
        accent: 'var(--color-accent, #10b981)',
        default: 'var(--color-border, #e5e7eb)', // если добавим позже
      },
      minHeight: {
        'text-2': '2.5rem',
        'text-3': '3.75rem',
        'text-4': '5rem',
      },
      maxWidth: {
        '8xl': '88rem',
        '9xl': '96rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/line-clamp'),
  ],
  safelist: [
    // Динамические классы для цветов
    { pattern: /bg-(primary|secondary|accent|header-bg|footer-bg|hero-bg|default)/ },
    { pattern: /text-(primary|secondary|accent|default)/ },
    { pattern: /border-(primary|secondary|accent|default)/ },
    { pattern: /from-(primary|secondary|accent|hero-bg)/ },
    { pattern: /to-(primary|secondary|accent|hero-bg)/ },
    { pattern: /hover:bg-(primary|secondary|accent|header-bg|footer-bg|hero-bg|default)/ },
    { pattern: /hover:text-(primary|secondary|accent|default)/ },
    { pattern: /hover:border-(primary|secondary|accent|default)/ },

    // Темная тема
    'dark:bg-gray-800',
    'dark:bg-gray-900',
    'dark:text-white',
    'dark:text-gray-300',
    'dark:text-gray-400',
    'dark:border-gray-700',

    // Обработка текста
    'truncate',
    'line-clamp-1',
    'line-clamp-2',
    'line-clamp-3',
    'break-words',
    'hyphens-auto',
    'min-h-text-2',
    'min-h-text-3',
    'shrink-0',
    'flex-grow',
    'min-w-0',

    // Размеры для продуктов
    'aspect-square',
    'aspect-video',
  ],
}
