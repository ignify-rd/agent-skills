import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { cpSync, existsSync, mkdirSync, rmSync, writeFileSync } from 'fs';
import os from 'os';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PACKAGE_ROOT = join(__dirname, '..', '..'); // package root

export const AI_CONFIG = {
  claude:      '.claude/skills',
  cursor:      '.cursor/skills',
  windsurf:    '.windsurf/rules',
  antigravity: '.agent/skills',
  copilot:     '.github/copilot-skills',
  kiro:        '.kiro/rules',
  codex:       '.codex/skills',
  qoder:       '.qoder/rules',
  roocode:     '.roo/rules',
  gemini:      '.gemini/skills',
  trae:        '.trae/rules',
  opencode:    '.opencode/skills',
  continue:    '.continue/skills',
  codebuddy:   '.codebuddy/skills',
  droid:       '.factory/skills',
};

function codexSkillsDir() {
  const codexHome = process.env.CODEX_HOME || join(os.homedir(), '.codex');
  return join(codexHome, 'skills');
}

const SKILLS = [
  'test-case-generator',
  'test-design-generator',
];

const SKILL_CONTENTS = [
  'SKILL.md',
  'AGENTS.md',
  'references',
  'scripts',
];

const SKILL_EXTRA = {
  'test-design-generator': ['data/rules'],
};

const COMMANDS = [
  {
    skill: 'test-case-generator',
    command: 'generate-test-case',
    description: 'Generate test case JSON from a mindmap file (.txt/.md) and optional RSD/PTTK',
  },
  {
    skill: 'test-design-generator',
    command: 'generate-test-design',
    description: 'Generate a test design mindmap (.md) from RSD/PTTK documents',
  },
];

export async function initCommand(options = {}) {
  const ai = options.ai || 'claude';

  logger.title('test-genie Installer');

  if (ai === 'all') {
    logger.info('Installing skills for all AI assistants...');
    console.log();
    for (const [aiType, configDir] of Object.entries(AI_CONFIG)) {
      await installSkillsForAI(aiType, configDir);
    }
    installClaudeCommands();
    installCursorCommands();
  } else {
    const configDir = AI_CONFIG[ai];
    if (!configDir) {
      logger.error(`Unsupported AI type: "${ai}". Supported: ${[...Object.keys(AI_CONFIG), 'all'].join(', ')}`);
      process.exit(1);
    }
    await installSkillsForAI(ai, configDir);
    if (ai === 'claude') {
      installClaudeCommands();
    }
    if (ai === 'cursor') {
      installCursorCommands();
    }
  }

  installProjectStructure();

  console.log();
  logger.info('Next steps:');
  if (ai === 'all') {
    logger.dim('Skills installed for all supported AI assistants.');
  } else {
    const installedPath = ai === 'codex' ? codexSkillsDir() : join(process.cwd(), AI_CONFIG[ai]);
    logger.dim(`Skills installed in: ${installedPath}`);
  }
  logger.dim(`Project catalog: ${join(process.cwd(), 'catalog')}`);
  logger.dim(`Project rules:   ${join(process.cwd(), 'AGENTS.md')}`);
  console.log();
}

async function installSkillsForAI(ai, configDir) {
  const targetBase = ai === 'codex' ? codexSkillsDir() : join(process.cwd(), configDir);

  logger.info(`Installing skills for ${ai}...`);
  logger.dim(`Target: ${targetBase}`);
  console.log();

  mkdirSync(targetBase, { recursive: true });

  for (const skill of SKILLS) {
    const src = join(PACKAGE_ROOT, skill);
    const dest = join(targetBase, skill);

    if (!existsSync(src)) {
      logger.warn(`Skill not found: ${skill} (skipping)`);
      continue;
    }

    rmSync(dest, { recursive: true, force: true });
    mkdirSync(dest, { recursive: true });

    for (const item of SKILL_CONTENTS) {
      const itemSrc = join(src, item);
      if (!existsSync(itemSrc)) continue;
      const itemDest = join(dest, item);
      cpSync(itemSrc, itemDest, { recursive: true });
    }

    const extras = SKILL_EXTRA[skill];
    if (extras) {
      for (const extra of extras) {
        const extraSrc = join(src, extra);
        if (!existsSync(extraSrc)) continue;
        const extraDest = join(dest, extra);
        mkdirSync(dirname(extraDest), { recursive: true });
        cpSync(extraSrc, extraDest, { recursive: true });
      }
    }

    logger.success(`Installed: ${skill}`);
  }

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
      writeFileSync(agentsPath, '# Project Rules\n\nAdd project-specific rules here.\n', 'utf8');
    }
    logger.success('Created: AGENTS.md');
  } else {
    logger.dim('AGENTS.md already exists (skipped)');
  }

  console.log();
}

function installClaudeCommands() {
  const commandsDir = join(process.cwd(), '.claude', 'commands');
  mkdirSync(commandsDir, { recursive: true });

  for (const { command, description } of COMMANDS) {
    const dest = join(commandsDir, `${command}.md`);
    const content = `---\ndescription: ${description}\n---\n\n$ARGUMENTS\n`;
    writeFileSync(dest, content, 'utf8');
    logger.success(`Installed slash command: /${command}`);
  }

  console.log();
}

function installCursorCommands() {
  const commandsDir = join(process.cwd(), '.cursor', 'commands');
  mkdirSync(commandsDir, { recursive: true });

  for (const { command, description } of COMMANDS) {
    const dest = join(commandsDir, `${command}.mdc`);
    const content = `---\ndescription: ${description}\n---\n\n$ARGUMENTS\n`;
    writeFileSync(dest, content, 'utf8');
    logger.success(`Installed slash command: /${command}`);
  }

  console.log();
}
