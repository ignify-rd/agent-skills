#!/usr/bin/env node
import { program } from 'commander';
import { createRequire } from 'module';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const pkg = JSON.parse(readFileSync(join(__dirname, '..', 'package.json'), 'utf8'));

import { initCommand } from '../src/commands/init.js';
import { versionsCommand } from '../src/commands/versions.js';
import { updateCommand } from '../src/commands/update.js';
import { uploadCommand } from '../src/commands/upload.js';
import { extractCommand } from '../src/commands/extract.js';

program
  .name('test-genie')
  .description('AI skills for test case and test design generation')
  .version(pkg.version);

program
  .command('init')
  .description('Install test-genie skills into your AI assistant configuration')
  .option('--ai <type>', 'AI assistant type (claude|cursor|windsurf|copilot|kiro|codex|roocode|gemini|trae|opencode|continue|codebuddy|all)')
  .action((options) => initCommand(options));

program
  .command('versions')
  .description('List available versions')
  .action(() => versionsCommand());

program
  .command('update')
  .description('Update skills to the latest version')
  .option('--ai <type>', 'AI assistant type (claude|cursor|windsurf|copilot|kiro|codex|roocode|gemini|trae|opencode|continue|codebuddy|all)')
  .action((options) => updateCommand(options));

program
  .command('extract')
  .description('Extract structure.json from excel_template/template.xlsx')
  .option('--template <path>', 'Path to .xlsx template (default: excel_template/template.xlsx)')
  .option('--output <path>', 'Output path for structure.json (default: excel_template/structure.json)')
  .option('--sheet <name>', 'Sheet name to extract (auto-detected if omitted)')
  .option('--project-root <path>', 'Project root directory (default: current directory)')
  .action((options) => extractCommand(options));

program
  .command('upload <test-case-name>')
  .description('Upload test-cases.json to Google Sheets')
  .option('--project-root <path>', 'Project root directory (default: current directory)')
  .action((testCaseName, options) => uploadCommand(testCaseName, options));

program.parse();
