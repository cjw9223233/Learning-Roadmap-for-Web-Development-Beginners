import { parseInspections, summarize } from './dist/inspection.js';
import { sampleBackup } from './dist/examples.js';
console.log(JSON.stringify(summarize(parseInspections(JSON.stringify(sampleBackup))), null, 2));
