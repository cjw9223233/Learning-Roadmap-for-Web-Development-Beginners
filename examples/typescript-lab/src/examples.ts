import type { Backup } from './inspection.js';

export const sampleBackup: Backup = {
  version: 1,
  rows: [
    { id: 'ts-1', equipment: 'A01 月台照明', result: '正常' },
    { id: 'ts-2', equipment: 'A02 指示燈', result: '異常' },
    { id: 'ts-3', equipment: 'B01 廣播設備', result: '正常' }
  ]
};
