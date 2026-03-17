import chalk from 'chalk';
import { getLatestRelease } from '../utils/github.js';
import { logger } from '../utils/logger.js';
import { initCommand } from './init.js';

export async function updateCommand(options = {}) {
  logger.title('test-genie Updater');

  try {
    const release = await getLatestRelease();
    logger.info(`Latest version: ${chalk.cyan(release.tag_name)}`);
    console.log();
    await initCommand(options);
  } catch (error) {
    logger.warn('Could not fetch latest release (offline?)');
    logger.dim('Running local install instead...');
    console.log();
    await initCommand(options);
  }
}
