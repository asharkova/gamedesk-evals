import { copyFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

for (const filename of ['requirements.json', 'cases.json']) {
  await copyFile(fileURLToPath(new URL(`../${filename}`, import.meta.url)), fileURLToPath(new URL(`dist/${filename}`, import.meta.url)));
}
process.stdout.write('Synced policy requirements and draft development cases.\n');
