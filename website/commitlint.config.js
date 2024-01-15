import conventional from '@commitlint/config-conventional';

export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    ...conventional.rules,
    'type-enum': [
      2,
      'always',
      ['feat', 'feature', 'fix', 'refactor', 'docs', 'build', 'test', 'ci', 'chore', 'wip'],
    ],
  },
};
