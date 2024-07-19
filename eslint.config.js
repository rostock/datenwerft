import html from 'eslint-plugin-html'

export default [
  {
    files: ['**/*.js'],
    rules: {
      'no-unused-vars': ['off']
    }
  }, {
    files: ['**/*.html'],
    plugins: {
      html
    }
  }
]
