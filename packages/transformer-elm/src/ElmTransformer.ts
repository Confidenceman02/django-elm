import { Transformer } from "@parcel/plugin";
import ThrowableDiagnostic, { md } from "@parcel/diagnostic";
import elm from "node-elm-compiler";
import which from "which";
import path from "node:path";
import { minify } from "terser";

const MODELS_DIR_NAME = "Models";
let ELM_PURE_FUNCS = [
  "F2",
  "F3",
  "F4",
  "F5",
  "F6",
  "F7",
  "F8",
  "F9",
  "A2",
  "A3",
  "A4",
  "A5",
  "A6",
  "A7",
  "A8",
  "A9",
];

export default new Transformer({
  async transform({ asset, options, logger }) {
    logger = logger;
    const debug =
      !options.env.PARCEL_ELM_NO_DEBUG && options.mode !== "production";
    const optimize = asset.env.shouldOptimize;
    const report = "json";
    const pathToElm = await which("elm");

    asset.invalidateOnEnvChange("PARCEL_ELM_NO_DEBUG");

    const directory = path.dirname(asset.filePath);
    const basename = path.basename(asset.filePath);
    const invalidatorsFiles = new Set([
      path.join(directory, MODELS_DIR_NAME, basename),
    ]);

    invalidatorsFiles.forEach((filePath) => {
      asset.invalidateOnFileChange(filePath);
    });

    let compiled;
    try {
      compiled = await elm.compileToString([asset.filePath], {
        debug,
        optimize,
        report,
        pathToElm,
      });
    } catch (e: any) {
      let compilerJson = e.message.split("\n")[1];
      let compilerDiagnostics = JSON.parse(compilerJson);

      if (compilerDiagnostics.type === "compile-errors") {
        throw new ThrowableDiagnostic({
          diagnostic: compilerDiagnostics.errors.flatMap(
            elmCompileErrorToParcelDiagnostics,
          ),
        });
      }

      // compilerDiagnostics.type === "error"
      // happens for example when compiled in prod mode with Debug.log in code
      throw new ThrowableDiagnostic({
        diagnostic: formatElmError(compilerDiagnostics, ""),
      });
    }

    const regex =
      /(function _Platform_initialize[^\{]*\{[\s\S]*?)(return ports \? \{\s*ports: ports\s*\} : \{\s*\}\s*;\s*\})/g;

    const injection = `
      const die = function () {
        managers = null;
        model = { $: null };
        stepper = () => {};
        ports = null;
      };
      return ports ? {
        ports: ports,
        die: die
      } : {
        die: die
      };
    `;

    compiled = compiled.replace(
      regex,
      `$1` + injection + "\n};", // Add the closing brace of the function
    );

    // TODO HMR!
    // if (options.hmrOptions) {
    //   compiled = elmHMR.inject(compiled);
    // }
    if (optimize) compiled = await minifyElmOutput(compiled, logger);

    asset.type = "js";
    asset.setCode(compiled);

    return [asset];
  },
});

function elmCompileErrorToParcelDiagnostics(error: {
  path: string;
  problems: any[];
}) {
  const relativePath = path.relative(process.cwd(), error.path);
  return error.problems.map((problem) => formatElmError(problem, relativePath));
}

function formatElmError(
  problem: { title: string | any[]; message: any[] },
  relativePath: string | any[],
) {
  const padLength = Math.max(
    80 - 5 - problem.title.length - relativePath.length,
    1,
  );
  const dashes = "-".repeat(padLength);
  const message = [
    "",
    `-- ${problem.title} ${dashes} ${relativePath}`,
    "",
    problem.message.map(formatMessagePiece).join(""),
  ].join("\n");

  return {
    message,
    origin: "@confidenceman02/parcel-transformer-djelm",
    stack: "", // set stack to empty since it is not useful
  };
}

async function minifyElmOutput(
  source: string,
  logger: {
    error(e: Error): void;
    [key: string]: any;
  },
) {
  // Recommended minification
  // Based on: http://elm-lang.org/0.19.0/optimize
  try {
    let result = await minify(source, {
      compress: {
        keep_fargs: false,
        passes: 2,
        pure_funcs: ELM_PURE_FUNCS,
        pure_getters: true,
        unsafe: true,
        unsafe_comps: true,
      },
      mangle: {
        reserved: ELM_PURE_FUNCS,
      },
    });
    if (result.code != null) return result.code;
  } catch (e) {
    logger.error(e as Error);
    throw e;
  }
}

function formatMessagePiece(piece: { string: any; underline: any }) {
  if (piece.string) {
    if (piece.underline) {
      return md([""], [md.underline(piece.string)]);
    }
    return md([""], [md.bold(piece.string)]);
  }
  if (typeof piece === "string") {
    return md([piece]);
  }
}
