import { parseInspections, summarize } from './inspection.js';
import { sampleBackup } from './sample.js';

const rows = parseInspections(JSON.stringify(sampleBackup));
console.log(JSON.stringify(summarize(rows), null, 2));
