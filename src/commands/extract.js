import { fileURLToPath } from 'url';
import { dirname, join, resolve } from 'path';
import { existsSync, statSync } from 'fs';
import { execSync } from 'child_process';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PACKAGE_ROOT = join(__dirname, '..', '..');
const SCRIPTS_DIR = join(PACKAGE_ROOT, 'test-case-generator-api', 'scripts');

function getPythonCommand() {
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

export function extractCommand(options) {
  const projectRoot = options.projectRoot || process.cwd();
  const scriptPath = join(SCRIPTS_DIR, 'extract_structure.py');

  if (!existsSync(scriptPath)) {
    logger.error(`Extract script not found: ${scriptPath}`);
    logger.info('Run "npm install -g git+https://github.com/ignify-rd/agent-skills.git" to reinstall.');
    process.exit(1);
  }

  const templatePath = options.template
    ? resolve(projectRoot, options.template)
    : join(projectRoot, 'excel_template', 'template.xlsx');

  if (!existsSync(templatePath)) {
    logger.error(`Template not found: ${templatePath}`);
    logger.info('Place your .xlsx template at: excel_template/template.xlsx');
    process.exit(1);
  }

  const outputPath = options.output
    ? resolve(projectRoot, options.output)
    : join(projectRoot, 'excel_template', 'structure.json');

  const pythonCmd = getPythonCommand();
  if (!pythonCmd) {
    const currentVer = getPythonVersion('python');
    if (currentVer) {
      logger.error(`${currentVer} detected — Python 3.6+ is required.`);
    } else {
      logger.error('Python is not installed.');
    }
    logger.info('');
    logger.info('Fix: Install Python 3.6+ from https://www.python.org/downloads/');
    process.exit(1);
  }

  logger.info(`Extracting structure from: ${templatePath}`);
  logger.info(`Using: ${getPythonVersion(pythonCmd)}`);

  try {
    let cmd = `${pythonCmd} "${scriptPath}" --template "${templatePath}" --output "${outputPath}" --project-root "${projectRoot}"`;
    if (options.sheet) {
      cmd += ` --sheet "${options.sheet}"`;
    }
    const output = execSync(cmd, {
      cwd: projectRoot,
      encoding: 'utf-8',
      stdio: ['inherit', 'pipe', 'pipe'],
    });
    if (output.trim()) {
      console.log(output.trim());
    }
    logger.success(`Structure extracted → ${outputPath}`);
  } catch (err) {
    logger.error('Extraction failed.');
    if (err.stderr) {
      console.error(err.stderr);
    }
    logger.info('');
    logger.info('Check that openpyxl is installed:');
    logger.info(`  ${pythonCmd} -m pip install openpyxl`);
    process.exit(1);
  }
}

/**
 * Run extract_structure.py if structure.json is missing or older than template.xlsx.
 * Returns true if extraction ran, false if structure.json was already up-to-date.
 */
export function autoExtractIfNeeded(projectRoot) {
  const templatePath = join(projectRoot, 'excel_template', 'template.xlsx');
  const structurePath = join(projectRoot, 'excel_template', 'structure.json');

  if (!existsSync(templatePath)) {
    return false; // no template, nothing to extract
  }

  let needsExtract = false;

  if (!existsSync(structurePath)) {
    needsExtract = true;
  } else {
    // Compare mtime: if template is newer than structure.json, re-extract
    const templateMtime = statSync(templatePath).mtimeMs;
    const structureMtime = statSync(structurePath).mtimeMs;
    if (templateMtime > structureMtime) {
      needsExtract = true;
    }
  }

  if (needsExtract) {
    logger.info('Template changed — regenerating structure.json...');
    extractCommand({ projectRoot });
    return true;
  }

  return false;
}
