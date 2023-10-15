"use strict";
const _core = require("@parcel/core");
let bundler = new _core.Parcel({
  entries: "./djelm_src/*.ts",
  defaultConfig: "@parcel/config-default",
  defaultTargetOptions: {
    distDir: "../static/dist",
  },
});
async function Main() {
  try {
    let { bundleGraph, buildTime } = await bundler.run();
    let bundles = bundleGraph.getBundles();
    console.log(`✨ Built ${bundles.length} bundles in ${buildTime}ms!`);
  } catch (err) {
    console.error(err.diagnostics);
    process.exit(1);
  }
}
Main().then(() => process.exit());