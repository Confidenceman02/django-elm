"use strict";
const _core = require("@parcel/core");
const args = process.argv.slice(2);
let bundler = new _core.Parcel({
  entries: "./djelm_src/*.ts",
  defaultConfig: "@parcel/config-default",
  mode: args[0],
  defaultTargetOptions: {
    distDir: "../static/dist",
  },
});
async function Main() {
  try {
    let { bundleGraph, buildTime } = await bundler.run();
    let bundles = bundleGraph.getBundles();
    console.log(`✨ Built ${bundles.length} bundles in ${buildTime}ms!\n`);
  } catch (err) {
    console.error(err.diagnostics);
    process.exit(1);
  }
}
Main().then(() => process.exit());
