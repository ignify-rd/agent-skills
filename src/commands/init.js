import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'fs';
import os from 'os';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PACKAGE_ROOT = join(__dirname, '..', '..'); // package root (node_modules/test-genie/)

const SKILLS = ['test-case-generator', 'test-design-generator'];

// Map AI name → subdirectory base (relative to cwd, or absolute for codex)
const AI_CONFIGS = {
  claude:    '.claude/skills',
  cursor:    '.cursor/skills',
  windsurf:  '.windsurf/rules',
  roocode:   '.roo/rules',
  copilot:   '.github/copilot-skills',
  kiro:      '.kiro/rules',
  gemini:    '.gemini/skills',
  agent:     '.agent/skills',
  qoder:     '.qoder/rules',
  trae:      '.trae/rules',
  opencode:  '.opencode/skills',
  continue:  '.continue/skills',
  codebuddy: '.codebuddy/skills',
  factory:   '.factory/skills',
};

const SUPPORTED_AI = [...Object.keys(AI_CONFIGS), 'codex', 'all'];

function getInstallBase(ai) {
  if (ai === 'codex') {
    const codexHome = process.env.CODEX_HOME || join(os.homedir(), '.codex');
    return join(codexHome, 'skills');
  }
  return join(process.cwd(), AI_CONFIGS[ai]);
}

function installSkills(ai) {
  const installBase = getInstallBase(ai);
  for (const skill of SKILLS) {
    const src = join(PACKAGE_ROOT, skill);
    const dest = join(installBase, skill);
    mkdirSync(dest, { recursive: true });
    cpSync(src, dest, {
      recursive: true,
      filter: (srcPath) => !srcPath.startsWith(join(src, 'data', 'catalogs')),
    });
    logger.success(`Installed: ${skill} → ${dest}`);
  }
}

export async function initCommand(options = {}) {
  const ai = options.ai || 'claude';

  logger.title('test-genie Installer');

  if (!SUPPORTED_AI.includes(ai)) {
    logger.error(`Unknown AI type: "${ai}". Supported: ${SUPPORTED_AI.join(', ')}`);
    process.exit(1);
  }

  if (ai === 'all') {
    logger.info('Installing skills for all AI assistants...');
    console.log();
    for (const name of Object.keys(AI_CONFIGS)) {
      installSkills(name);
    }
    installSkills('codex');
  } else {
    installSkills(ai);
  }

  console.log();
  installProjectStructure();

  logger.info('Next steps:');
  logger.dim(`Project catalog: ${join(process.cwd(), 'catalog')}`);
  logger.dim(`Project rules:   ${join(process.cwd(), 'AGENTS.md')}`);
  logger.dim(`Skills location: ${PACKAGE_ROOT}`);
  console.log();
}

function installProjectStructure() {
  const projectRoot = process.cwd();

  logger.info('Setting up project structure...');

  const catalogDirs = ['catalog/api', 'catalog/frontend', 'catalog/mobile'];
  for (const dir of catalogDirs) {
    const fullDir = join(projectRoot, dir);
    mkdirSync(fullDir, { recursive: true });
    const gitkeep = join(fullDir, '.gitkeep');
    if (!existsSync(gitkeep)) {
      writeFileSync(gitkeep, '', 'utf8');
    }
    logger.success(`Created: ${dir}/`);
  }

  const excelTemplateDir = join(projectRoot, 'excel_template');
  mkdirSync(excelTemplateDir, { recursive: true });
  const defaultTemplate = join(PACKAGE_ROOT, 'test-case-generator', 'data', 'templates', 'template.xlsx');
  const destTemplate = join(excelTemplateDir, 'template.xlsx');
  if (existsSync(defaultTemplate) && !existsSync(destTemplate)) {
    cpSync(defaultTemplate, destTemplate);
    logger.success('Created: excel_template/template.xlsx');
  } else if (!existsSync(destTemplate)) {
    const gitkeep = join(excelTemplateDir, '.gitkeep');
    if (!existsSync(gitkeep)) {
      writeFileSync(gitkeep, '', 'utf8');
    }
    logger.success('Created: excel_template/');
  }

  const agentsPath = join(projectRoot, 'AGENTS.md');
  if (!existsSync(agentsPath)) {
    const templateSrc = join(PACKAGE_ROOT, 'templates', 'AGENTS.md');
    if (existsSync(templateSrc)) {
      cpSync(templateSrc, agentsPath);
    } else {
      writeFileSync(agentsPath, '# Project Rules\n\nAdd project-specific overrides here.\n', 'utf8');
    }
    logger.success('Created: AGENTS.md');
  } else {
    logger.dim('AGENTS.md already exists (skipped)');
  }

  const credentialsPath = join(projectRoot, 'credentials.json');
  if (!existsSync(credentialsPath)) {
    const credentialsTemplate = {
      type: 'service_account',
      project_id: '',
      private_key_id: '',
      private_key: '',
      client_email: '',
      client_id: '',
      auth_uri: 'https://accounts.google.com/o/oauth2/auth',
      token_uri: 'https://oauth2.googleapis.com/token',
      auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
      client_x509_cert_url: '',
    };
    writeFileSync(credentialsPath, JSON.stringify(credentialsTemplate, null, 2), 'utf8');
    logger.success('Created: credentials.json (fill in your Service Account details)');
  } else {
    logger.dim('credentials.json already exists (skipped)');
  }

  const gitignorePath = join(projectRoot, '.gitignore');
  const gitignoreEntry = 'credentials.json';
  if (!existsSync(gitignorePath)) {
    writeFileSync(gitignorePath, `${gitignoreEntry}\n`, 'utf8');
    logger.success('Created: .gitignore (credentials.json excluded)');
  } else {
    const existing = readFileSync(gitignorePath, 'utf8');
    if (!existing.split('\n').map(l => l.trim()).includes(gitignoreEntry)) {
      const separator = existing.endsWith('\n') ? '' : '\n';
      writeFileSync(gitignorePath, `${existing}${separator}${gitignoreEntry}\n`, 'utf8');
      logger.success('Updated: .gitignore (added credentials.json)');
    } else {
      logger.dim('.gitignore already excludes credentials.json (skipped)');
    }
  }

  console.log();
}
