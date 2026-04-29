#!/usr/bin/env node
"use strict";

const { spawnSync } = require("node:child_process");
const path = require("node:path");

const packageRoot = path.resolve(__dirname, "..");
const existingPythonPath = process.env.PYTHONPATH || "";
const env = {
  ...process.env,
  PYTHONPATH: existingPythonPath
    ? `${packageRoot}${path.delimiter}${existingPythonPath}`
    : packageRoot,
};

function runPython(command) {
  return spawnSync(command, ["-m", "agent_fleet.cli", ...process.argv.slice(2)], {
    env,
    stdio: "inherit",
  });
}

let result = runPython(process.env.AGENTFLEET_PYTHON || "python3");
if (result.error && result.error.code === "ENOENT") {
  result = runPython("python");
}

if (result.error) {
  console.error(`agentfleet: failed to start Python: ${result.error.message}`);
  process.exit(127);
}

process.exit(result.status ?? 1);
