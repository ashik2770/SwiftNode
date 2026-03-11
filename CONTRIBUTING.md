# Contributing to SwiftNode

First off, thank you for considering contributing to SwiftNode! It's people like you that make SwiftNode such a great tool.

## Where do I go from here?

If you've noticed a bug or have a feature request, make sure to check if there's already an [issue](https://github.com/ashik2770/SwiftNode/issues) open. If not, go ahead and open a new one!

## Fork & create a branch

If this is something you think you can fix, then fork SwiftNode and create a branch with a descriptive name.

A good branch name would be (where issue #325 is the ticket you're working on):

```sh
git checkout -b 325-add-new-translator-tool
```

## Implementing your fix or feature

- Make sure to add relevant comments to your code.
- If you're adding a new tool, ensure you register it in `swiftnode/tools/__init__.py` and add its schema.
- Follow PEP 8 style guidelines.

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Code of Conduct

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.
