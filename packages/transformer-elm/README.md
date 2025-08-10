# @confidenceman02/parcel-transformer-djelm

A Parcel V2 transformer for the [djelm](https://github.com/Confidenceman02/django-elm) framework. It enables you to compile Elm files directly within your Parcel project.

## Features

- Compiles Elm source files.
- Supports `debug` and `production` modes.
- Minifies compiled Elm code in production for smaller bundles, following Elm's optimization guide.
- Integrates Elm's compiler errors beautifully with Parcel's diagnostic output.
- Injects a `die()` function into the compiled JavaScript for advanced lifecycle management with `djelm`.

## Installation

Install the package using your favorite package manager:

```bash
npm install --save-dev @confidenceman02/parcel-transformer-djelm
# or
pnpm add -D @confidenceman02/parcel-transformer-djelm
# or
yarn add -D @confidenceman02/parcel-transformer-djelm
```

## Usage

To use this transformer, you need to configure it in your `.parcelrc` file.

```json
{
  "extends": "@parcel/config-default",
  "transformers": {
    "*.elm": ["@confidenceman02/parcel-transformer-djelm"]
  }
}
```

Now, Parcel will automatically use this transformer for any `.elm` files it encounters.

## Configuration

### Debug Mode

By default, the transformer compiles Elm code with `debug` options enabled. In production mode (`parcel build`), `debug` is turned off.

You can force `debug` mode to be off by setting the `PARCEL_ELM_NO_DEBUG` environment variable.

```bash
PARCEL_ELM_NO_DEBUG=true parcel build
```

### Optimization

When Parcel's `shouldOptimize` flag is set (which is the default for production builds), the transformer will minify the compiled JavaScript using `terser` with settings recommended for Elm.

## Repository

This package is part of the [django-elm](https://github.com/Confidenceman02/django-elm) monorepo. For issues, contributions, and more information, please visit the main repository.

## License

This project is licensed under the ISC License. See the `LICENSE.txt` file in the root of the repository for details.
