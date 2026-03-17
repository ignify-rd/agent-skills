import { execSync } from 'child_process';
import { logger } from '../utils/logger.js';
import { initCommand } from './init.js';

const REPO_URL = 'git+https://github.com/ignify-rd/agent-skills.git';

export async function updateCommand(options = {}) {
  logger.title('test-genie Updater');

  logger.info('Pulling latest version from GitHub...');
  console.log();

  try {
    execSync(`npm install -g ${REPO_URL}`, { stdio: 'inherit' });
    console.log();
    await initCommand(options);
  } catch (error) {
    logger.warn('Could not update from GitHub.');
    logger.dim('Make sure you have access to the repository.');
    logger.dim(`  Manual update: npm install -g ${REPO_URL}`);
    console.log();
    logger.info('Installing skills from current local version...');
    console.log();
    await initCommand(options);
  }
}
