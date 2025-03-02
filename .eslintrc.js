module.exports = {
  root: true,
  env: {
    node: true,
    browser: true
  },
  extends: [
    'plugin:vue/recommended',
    'eslint:recommended'
  ],
  rules: {
    'vue/attributes-order': 'off',
    'vue/max-attributes-per-line': 'off',
    'prettier/prettier': 'off',
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
    'vue/no-v-html': 'off'
  },
  parserOptions: {
    parser: 'babel-eslint'
  }
} 