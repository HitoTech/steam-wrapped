# Conventional Commits

This project follows the Conventional Commits specification for commit messages. All commit messages must follow this format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Commit Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools and libraries such as documentation generation

## Examples
- `feat: add steam API integration`
- `fix(api): resolve authentication issue`
- `docs: update README with setup instructions`
- `refactor(ui): improve display component structure`
- `test: add unit tests for steam service`

## Breaking Changes
For breaking changes, use `!` after the type and scope:
- `feat!: change API response format`

## Scope
Use scope to indicate which part of the codebase is affected:
- `api`: Steam API related changes
- `ui`: User interface changes
- `config`: Configuration changes
- `docs`: Documentation changes