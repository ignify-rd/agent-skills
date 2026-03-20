import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { cpSync, existsSync, mkdirSync, readFileSync, writeFileSync } from 'fs';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PACKAGE_ROOT = join(__dirname, '..', '..'); // package root (node_modules/test-genie/)

const COMMANDS = [
  {
    command: 'generate-test-case',
    skill: 'test-case-generator',
    description: 'Generate test cases from mindmap + RSD/PTTK and push to Google Sheets. Use when user says "sinh test case", "tạo test case", "generate test case", "xuất test case"',
  },
  {
    command: 'generate-test-design',
    skill: 'test-design-generator',
    description: 'Generate a test design mindmap (.md) from RSD/PTTK. Use when user says "sinh test design", "tạo mindmap", "generate test design"',
  },
];

export async function initCommand(options = {}) {
  const ai = options.ai || 'claude';

  logger.title('test-genie Installer');

  if (ai === 'all') {
    logger.info('Installing commands for all AI assistants...');
    console.log();
    installClaudeCommands();
    installCursorCommands();
    installCursorRules();
  } else {
    if (!['claude', 'cursor'].includes(ai)) {
      logger.warn(`Commands not yet supported for "${ai}". Supported: claude, cursor, all`);
    }
    if (ai === 'claude' || ai === 'all') {
      installClaudeCommands();
    }
    if (ai === 'cursor' || ai === 'all') {
      installCursorCommands();
      installCursorRules();
    }
  }

  installProjectStructure();

  console.log();
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

function installClaudeCommands() {
  const commandsDir = join(process.cwd(), '.claude', 'commands');
  mkdirSync(commandsDir, { recursive: true });

  for (const { command, skill, description } of COMMANDS) {
    const skillPath = join(PACKAGE_ROOT, skill, 'SKILL.md');
    const dest = join(commandsDir, `${command}.md`);
    const content = [
      `---`,
      `description: ${description}`,
      `---`,
      ``,
      `If \`AGENTS.md\` exists at the project root, read it first — its rules override all skill defaults.`,
      `Then read \`${skillPath}\` and follow the workflow exactly.`,
      ``,
      `$ARGUMENTS`,
      ``,
    ].join('\n');
    writeFileSync(dest, content, 'utf8');
    logger.success(`Installed: /${command}`);
  }

  console.log();
}

function installCursorCommands() {
  const commandsDir = join(process.cwd(), '.cursor', 'commands');
  mkdirSync(commandsDir, { recursive: true });

  for (const { command, skill, description } of COMMANDS) {
    const skillPath = join(PACKAGE_ROOT, skill, 'SKILL.md');
    const dest = join(commandsDir, `${command}.mdc`);
    const content = [
      `---`,
      `description: ${description}`,
      `---`,
      ``,
      `If \`AGENTS.md\` exists at the project root, read it first — its rules override all skill defaults.`,
      `Then read \`${skillPath}\` and follow the workflow exactly.`,
      ``,
      `$ARGUMENTS`,
      ``,
    ].join('\n');
    writeFileSync(dest, content, 'utf8');
    logger.success(`Installed: /${command}`);
  }

  console.log();
}

function installCursorRules() {
  const rulesDir = join(process.cwd(), '.cursor', 'rules');
  mkdirSync(rulesDir, { recursive: true });

  const commandLines = COMMANDS.map(({ command, skill, description }) => {
    const skillPath = join(PACKAGE_ROOT, skill, 'SKILL.md');
    return `- **/${command}**: ${description} → \`${skillPath}\``;
  }).join('\n');

  const content = [
    `---`,
    `description: Apply when user asks to generate test cases, test designs, or mindmaps (sinh test case, tạo test case, sinh test design, tạo mindmap, generate test case, generate test design)`,
    `alwaysApply: false`,
    `---`,
    ``,
    `# test-genie`,
    ``,
    `## Rule Priority`,
    ``,
    `1. \`AGENTS.md\` at project root — project-specific overrides (highest priority)`,
    `2. Skill \`AGENTS.md\` in package — default rules`,
    `3. Skill \`SKILL.md\` in package — workflow (never overridden)`,
    ``,
    `If \`AGENTS.md\` exists at project root, read it first. Its rules override the corresponding skill defaults.`,
    ``,
    `## Available Commands`,
    ``,
    commandLines,
    ``,
    `## How to Use`,
    ``,
    `1. Read \`AGENTS.md\` at project root (if exists)`,
    `2. Read the relevant SKILL.md path listed above`,
    `3. Follow the workflow exactly`,
    ``,
  ].join('\n');

  const dest = join(rulesDir, 'test-genie.mdc');
  writeFileSync(dest, content, 'utf8');
  logger.success('Installed: .cursor/rules/test-genie.mdc');

  console.log();
}
