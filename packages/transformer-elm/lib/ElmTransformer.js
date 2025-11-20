"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const plugin_1 = require("@parcel/plugin");
const diagnostic_1 = __importStar(require("@parcel/diagnostic"));
const node_elm_compiler_1 = __importDefault(require("node-elm-compiler"));
const which_1 = __importDefault(require("which"));
const node_path_1 = __importDefault(require("node:path"));
const terser_1 = require("terser");
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
exports.default = new plugin_1.Transformer({
    async transform({ asset, options, logger }) {
        logger = logger;
        const debug = !options.env.PARCEL_ELM_NO_DEBUG && options.mode !== "production";
        const optimize = asset.env.shouldOptimize;
        const report = "json";
        const pathToElm = await (0, which_1.default)("elm");
        asset.invalidateOnEnvChange("PARCEL_ELM_NO_DEBUG");
        const directory = node_path_1.default.dirname(asset.filePath);
        const basename = node_path_1.default.basename(asset.filePath);
        const invalidatorsFiles = new Set([
            node_path_1.default.join(directory, MODELS_DIR_NAME, basename),
        ]);
        invalidatorsFiles.forEach((filePath) => {
            asset.invalidateOnFileChange(filePath);
        });
        let compiled;
        try {
            compiled = await node_elm_compiler_1.default.compileToString([asset.filePath], {
                debug,
                optimize,
                report,
                pathToElm,
            });
        }
        catch (e) {
            let compilerJson = e.message.split("\n")[1];
            let compilerDiagnostics = JSON.parse(compilerJson);
            if (compilerDiagnostics.type === "compile-errors") {
                throw new diagnostic_1.default({
                    diagnostic: compilerDiagnostics.errors.flatMap(elmCompileErrorToParcelDiagnostics),
                });
            }
            // compilerDiagnostics.type === "error"
            // happens for example when compiled in prod mode with Debug.log in code
            throw new diagnostic_1.default({
                diagnostic: formatElmError(compilerDiagnostics, ""),
            });
        }
        const regex = /(function _Platform_initialize[^\{]*\{[\s\S]*?)(return ports \? \{\s*ports: ports\s*\} : \{\s*\}\s*;\s*\})/g;
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
        compiled = compiled.replace(regex, `$1` + injection + "\n};");
        // TODO HMR!
        // if (options.hmrOptions) {
        //   compiled = elmHMR.inject(compiled);
        // }
        if (optimize)
            compiled = await minifyElmOutput(compiled, logger);
        asset.type = "js";
        asset.setCode(compiled);
        return [asset];
    },
});
function elmCompileErrorToParcelDiagnostics(error) {
    const relativePath = node_path_1.default.relative(process.cwd(), error.path);
    return error.problems.map((problem) => formatElmError(problem, relativePath));
}
function formatElmError(problem, relativePath) {
    const padLength = Math.max(80 - 5 - problem.title.length - relativePath.length, 1);
    const dashes = "-".repeat(padLength);
    const message = [
        "",
        `-- ${problem.title} ${dashes} ${relativePath}`,
        "",
        problem.message.map(formatMessagePiece).join(""),
    ].join("\n");
    return {
        message,
        origin: "@confidenceman/parcel-transformer-djelm",
        stack: "", // set stack to empty since it is not useful
    };
}
async function minifyElmOutput(source, logger) {
    // Recommended minification
    // Based on: http://elm-lang.org/0.19.0/optimize
    try {
        let result = await (0, terser_1.minify)(source, {
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
        if (result.code != null)
            return result.code;
    }
    catch (e) {
        logger.error(e);
        throw e;
    }
}
function formatMessagePiece(piece) {
    if (piece.string) {
        if (piece.underline) {
            return (0, diagnostic_1.md)([""], [diagnostic_1.md.underline(piece.string)]);
        }
        return (0, diagnostic_1.md)([""], [diagnostic_1.md.bold(piece.string)]);
    }
    if (typeof piece === "string") {
        return (0, diagnostic_1.md)([piece]);
    }
}
