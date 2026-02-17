import eslint from '@eslint/js';
import tseslint from 'typescript-eslint';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import compat from 'eslint-plugin-compat';
import security from 'eslint-plugin-security';

export default tseslint.config(
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      'data/**',
      '.npm-cache/**'
    ]
  },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{js,mjs,cjs,ts,jsx,tsx}'],
    plugins: {
      'jsx-a11y': jsxA11y,
      'compat': compat,
      'security': security
    },
    rules: {
      ...jsxA11y.configs.recommended.rules,
      ...security.configs.recommended.rules,
      'security/detect-object-injection': 'warn',
      'jsx-a11y/alt-text': 'error',
      'no-eval': 'error'
    }
  }
);
