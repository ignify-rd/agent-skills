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

program
  .name('test-genie')
  .description('AI skills for test case and test design generation')
  .version(pkg.version);

program
  .command('init')
  .description('Install test-genie skills into your AI assistant configuration')
  .option('--ai <type>', 'AI assistant type (claude|cursor|windsurf|antigravity|copilot|kiro|codex|qoder|roocode|gemini|trae|opencode|continue|codebuddy|droid|all)', 'claude')
  .action((options) => initCommand(options));

program
  .command('versions')
  .description('List available versions')
  .action(() => versionsCommand());

program
  .command('update')
  .description('Update skills to the latest version')
  .option('--ai <type>', 'AI assistant type (claude|cursor|windsurf|antigravity|copilot|kiro|codex|qoder|roocode|gemini|trae|opencode|continue|codebuddy|droid|all)', 'claude')
  .action((options) => updateCommand(options));

program.parse();
