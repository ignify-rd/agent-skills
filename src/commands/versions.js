import chalk from 'chalk';
import { fetchReleases } from '../utils/github.js';
import { logger } from '../utils/logger.js';

export async function versionsCommand() {
  logger.title('test-genie Versions');

  try {
    const releases = await fetchReleases();

    if (releases.length === 0) {
      logger.warn('No releases found');
      return;
    }

    console.log(chalk.bold('Available versions:\n'));

    releases.forEach((release, index) => {
      const isLatest = index === 0;
      const tag = release.tag_name;
      const date = new Date(release.published_at).toLocaleDateString();

      if (isLatest) {
        console.log(`  ${chalk.green('*')} ${chalk.bold(tag)} ${chalk.dim(`(${date})`)} ${chalk.green('[latest]')}`);
      } else {
        console.log(`    ${tag} ${chalk.dim(`(${date})`)}`);
      }
    });

    console.log();
    logger.dim('Use: test-genie update to install the latest version');
  } catch (error) {
    logger.warn('Could not fetch remote versions (offline?)');
    logger.dim(error.message);
    process.exit(1);
  }
}
