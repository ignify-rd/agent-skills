import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { cpSync, existsSync, mkdirSync } from 'fs';
import { logger } from '../utils/logger.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const SKILLS_ROOT = join(__dirname, '..', '..'); // package root

const AI_CONFIG = {
  claude: '.claude/skills',
};

const SKILLS = [
  'test-case-generator',
  'test-design-generator',
];

export async function initCommand(options = {}) {
  const ai = options.ai || 'claude';

  logger.title('test-genie Installer');

  const configDir = AI_CONFIG[ai];
  if (!configDir) {
    logger.error(`Unsupported AI type: "${ai}". Supported: ${Object.keys(AI_CONFIG).join(', ')}`);
    process.exit(1);
  }

  const targetBase = join(process.cwd(), configDir);

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

    cpSync(src, dest, { recursive: true });
    logger.success(`Installed: ${skill}`);
  }

  console.log();
  logger.info('Next steps:');
  logger.dim(`Your skills are now in: ${configDir}/`);
  logger.dim('Claude will automatically load them from .claude/skills/');
  console.log();
}
