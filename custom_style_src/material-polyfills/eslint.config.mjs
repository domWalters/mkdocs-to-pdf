import js from '@eslint/js'
import prettier from 'eslint-config-prettier'
import globals from 'globals'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist/**', 'node_modules/**'] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2015,
      sourceType: 'module',
      globals: {
        ...globals.browser,
        ...globals.serviceworker,
        ...globals.node
      }
    }
  },
  {
    // Webpack loads plugins and loaders through `require`.
    files: ['webpack.config.ts'],
    rules: { '@typescript-eslint/no-require-imports': 'off' }
  },
  prettier
)
