import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { cpSync, existsSync, mkdirSync, rmSync } from 'fs';
import os from 'os';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SKILLS_ROOT = join(__dirname, '..', '..'); // package root

export const AI_CONFIG = {
  claude:      '.claude/skills',
  cursor:      '.cursor/rules',
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

export async function initCommand(options = {}) {
  const ai = options.ai || 'claude';

  logger.title('test-genie Installer');

  if (ai === 'all') {
    logger.info('Installing skills for all AI assistants...');
    console.log();
    for (const [aiType, configDir] of Object.entries(AI_CONFIG)) {
      await installForAI(aiType, configDir);
    }
  } else {
    const configDir = AI_CONFIG[ai];
    if (!configDir) {
      logger.error(`Unsupported AI type: "${ai}". Supported: ${[...Object.keys(AI_CONFIG), 'all'].join(', ')}`);
      process.exit(1);
    }
    await installForAI(ai, configDir);
  }

  console.log();
  logger.info('Next steps:');
  if (ai === 'all') {
    logger.dim('Skills installed for all supported AI assistants.');
  } else {
    const installedPath = ai === 'codex' ? codexSkillsDir() : join(process.cwd(), AI_CONFIG[ai]);
    logger.dim(`Your skills are now in: ${installedPath}`);
  }
  console.log();
}

async function installForAI(ai, configDir) {
  const targetBase = ai === 'codex' ? codexSkillsDir() : join(process.cwd(), configDir);

  logger.info(`Installing skills for ${ai}...`);
  logger.dim(`Target: ${targetBase}`);
  console.log();

  mkdirSync(targetBase, { recursive: true });

  for (const skill of SKILLS) {
    const src = join(SKILLS_ROOT, skill);
    const dest = join(targetBase, skill);

    if (!existsSync(src)) {
      logger.warn(`Skill not found: ${skill} (skipping)`);
      continue;
    }

    // Reinstall cleanly so repeated init runs stay idempotent.
    rmSync(dest, { recursive: true, force: true });
    cpSync(src, dest, { recursive: true });
    logger.success(`Installed: ${skill}`);
  }

  console.log();
}
