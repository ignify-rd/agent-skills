import { fileURLToPath } from 'url';
import { dirname, join, resolve } from 'path';
import { existsSync } from 'fs';
import { execSync } from 'child_process';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PACKAGE_ROOT = join(__dirname, '..', '..');
const SCRIPTS_DIR = join(PACKAGE_ROOT, 'test-case-generator', 'scripts');

export function uploadCommand(testCaseName, options) {
  const projectRoot = options.projectRoot || process.cwd();
  const scriptPath = join(SCRIPTS_DIR, 'upload_gsheet.py');

  if (!existsSync(scriptPath)) {
    logger.error(`Upload script not found: ${scriptPath}`);
    logger.info('Run "npm install -g git+https://github.com/ignify-rd/agent-skills.git" to reinstall.');
    process.exit(1);
  }

  const jsonPath = resolve(projectRoot, testCaseName, 'test-cases.json');
  if (!existsSync(jsonPath)) {
    logger.error(`Test cases not found: ${jsonPath}`);
    logger.info(`Expected file at: ${testCaseName}/test-cases.json`);
    logger.info('Generate test cases first, then upload.');
    process.exit(1);
  }

  logger.info(`Uploading ${testCaseName}/test-cases.json to Google Sheets...`);

  try {
    const cmd = `python "${scriptPath}" "${testCaseName}" --project-root "${projectRoot}"`;
    const output = execSync(cmd, {
      cwd: projectRoot,
      encoding: 'utf-8',
      stdio: ['inherit', 'pipe', 'pipe'],
    });
    if (output.trim()) {
      console.log(output.trim());
    }
    logger.success('Upload completed!');
  } catch (err) {
    logger.error('Upload failed.');
    if (err.stderr) {
      console.error(err.stderr);
    }
    logger.info('Check that Python dependencies are installed:');
    logger.info('  pip install google-auth-oauthlib google-auth google-api-python-client openpyxl');
    process.exit(1);
  }
}
