import { fileURLToPath } from 'url';
import { dirname, join, resolve } from 'path';
import { existsSync } from 'fs';
import { execSync } from 'child_process';
import { logger } from '../utils/logger.js';
import { autoExtractIfNeeded } from './extract.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PACKAGE_ROOT = join(__dirname, '..', '..');
const SCRIPTS_DIR = join(PACKAGE_ROOT, 'test-case-generator', 'scripts');

function getPythonCommand() {
  // On Windows, also check 'py -3' (Python Launcher)
  const candidates = process.platform === 'win32'
    ? ['py -3', 'python3', 'python']
    : ['python3', 'python'];

  for (const cmd of candidates) {
    try {
      const ver = execSync(`${cmd} --version`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
      const match = ver.match(/Python (\d+)\.(\d+)/);
      if (match && parseInt(match[1]) >= 3 && parseInt(match[2]) >= 6) {
        return cmd;
      }
    } catch {}
  }
  return null;
}

function getPythonVersion(cmd) {
  try {
    return execSync(`${cmd} --version`, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
  } catch {
    return null;
  }
}

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

  const pythonCmd = getPythonCommand();
  if (!pythonCmd) {
    // Show what python version is currently installed
    const currentVer = getPythonVersion('python');
    if (currentVer) {
      logger.error(`${currentVer} detected — Python 3.6+ is required.`);
    } else {
      logger.error('Python is not installed.');
    }
    logger.info('');
    logger.info('Fix: Install Python 3.6+ from https://www.python.org/downloads/');
    logger.info('  Windows: Download installer, check "Add Python to PATH"');
    logger.info('  After install, close and reopen terminal, then retry.');
    process.exit(1);
  }

  // Auto-regenerate structure.json if template.xlsx changed
  autoExtractIfNeeded(projectRoot);

  logger.info(`Uploading ${testCaseName}/test-cases.json to Google Sheets...`);
  logger.info(`Using: ${getPythonVersion(pythonCmd)}`);

  try {
    const cmd = `${pythonCmd} "${scriptPath}" "${testCaseName}" --project-root "${projectRoot}"`;
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
    logger.info('');
    logger.info('Check that Python 3 dependencies are installed:');
    logger.info(`  ${pythonCmd} -m pip install google-auth-oauthlib google-auth google-api-python-client openpyxl`);
    process.exit(1);
  }
}
