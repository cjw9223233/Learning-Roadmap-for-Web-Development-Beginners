// Lesson driver for the genuine TypeScript 6.0 compiler API (not the official tsc CLI).
const ts = require('typescript');
const path = require('node:path');
const args = process.argv.slice(2);
if (args.length === 1 && args[0] === '--version') {
  console.log(`TypeScript ${ts.version} (lesson compiler API driver)`);
  process.exit(0);
}
if (args[0] !== '--project' || !args[1] || args.length > 3 || (args[2] && args[2] !== '--noEmit')) {
  console.error('Usage: node tools/compiler.cjs --project CONFIG [--noEmit] | --version');
  process.exit(2);
}
const configPath = path.resolve(args[1]);
const host = { getCanonicalFileName: f => f, getCurrentDirectory: ts.sys.getCurrentDirectory, getNewLine: () => ts.sys.newLine };
function report(diagnostics) {
  if (diagnostics.length) console.error(ts.formatDiagnostics(diagnostics, host));
}
const read = ts.readConfigFile(configPath, ts.sys.readFile);
if (read.error) { report([read.error]); process.exit(1); }
const parsed = ts.parseJsonConfigFileContent(read.config, ts.sys, path.dirname(configPath), args[2] ? { noEmit: true } : {}, configPath);
if (parsed.errors.length) { report(parsed.errors); process.exit(1); }
const program = ts.createProgram({ rootNames: parsed.fileNames, options: parsed.options });
const before = ts.getPreEmitDiagnostics(program);
const emitted = program.emit();
const diagnostics = ts.sortAndDeduplicateDiagnostics([...before, ...emitted.diagnostics]);
report(diagnostics);
const failed = diagnostics.some(d => d.category === ts.DiagnosticCategory.Error);
if (!failed) console.log(`TypeScript ${ts.version}: ${parsed.options.noEmit ? 'checked (no emit)' : 'checked and emitted JavaScript'}`);
process.exitCode = failed ? 1 : 0;
