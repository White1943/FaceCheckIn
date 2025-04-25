/**
 * @author https://github.com/zxwk1998/vue-admin-better （不想保留author可删除）
 * @description .eslintrc.js
 */

module.exports = {
  root: true,
  env: {
    node: true,
    browser: true
  },
  extends: ['plugin:vue/recommended', 'eslint:recommended', '@vue/prettier'],
  rules: {
    'no-undef': 'off',
    'no-console': 'off',
    'no-debugger': 'off',
    'prettier/prettier': 'off',
    'prefer-template': 'error',
    '@typescript-eslint/no-this-alias': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-var-requires': 'off',
    '@typescript-eslint/no-empty-function': 'off',
    '@typescript-eslint/ban-ts-comment': 'off',
    'vue/no-reserved-component-names': 'off',
    'vue/no-v-html': 'off',
    'no-unused-vars': 'off',
    'vue/no-useless-template-attributes': 'off',
    'use-isnan': 'off',
    'vue/attributes-order': 'warn',
    'vue/order-in-components': 'warn',
    'vue/max-attributes-per-line': 'off',
    'vue/singleline-html-element-content-newline': 'off',
    'vue/multiline-html-element-content-newline': 'off',
    'vue/first-attribute-linebreak': ['error', {
      singleline: 'ignore',
      multiline: 'ignore'
    }],
    'vue/html-closing-bracket-newline': ['error', {
      singleline: 'never',
      multiline: 'never'
    }],
    'vue/html-self-closing': 'off',
    'vue/attribute-hyphenation': 'off',
    'vue/multi-word-component-names': 'off'
  },
  parserOptions: {
    parser: 'babel-eslint',
  },
  overrides: [
    {
      files: ['**/__tests__/*.{j,t}s?(x)', '**/tests/unit/**/*.spec.{j,t}s?(x)'],
      env: {
        jest: true,
      },
    },
  ],
}
