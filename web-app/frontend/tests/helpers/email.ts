import { spawn } from 'child_process';

const DOCKER_COMPOSE_FILE = '../../docker-compose-test.yml';
const MAX_RETRIES = 10;
const RETRY_DELAY_MS = 500;
const LOG_TAIL_LINES = 200;

/**
 * Extract verification URL from Django console logs.
 * Retries to account for async email sending.
 */
export async function extractVerificationUrl(email: string): Promise<string> {
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    const logs = await getDockerLogs();
    const url = parseVerificationUrl(logs);

    if (url) {
      return url;
    }

    if (attempt < MAX_RETRIES) {
      await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY_MS));
    }
  }

  throw new Error(
    `Failed to extract verification URL for ${email} after ${MAX_RETRIES} attempts`,
  );
}

async function getDockerLogs(): Promise<string> {
  return new Promise((resolve, reject) => {
    const proc = spawn(
      'docker',
      [
        'compose',
        '-f',
        DOCKER_COMPOSE_FILE,
        'logs',
        'app',
        '--tail',
        LOG_TAIL_LINES.toString(),
        '--no-log-prefix',
      ],
      { cwd: process.cwd() },
    );

    let output = '';
    proc.stdout?.on('data', (data) => (output += data.toString()));
    proc.stderr?.on('data', (data) => (output += data.toString()));
    proc.on('close', (code) =>
      code === 0 ? resolve(output) : reject(new Error(`Docker logs failed`)),
    );
  });
}

function parseVerificationUrl(logs: string): string | null {
  const matches = Array.from(
    logs.matchAll(
      /https?:\/\/[^\/\s]+\/verify-email\/([A-Za-z0-9_-]+)\/([A-Za-z0-9_-]+)\//g,
    ),
  );

  if (matches.length === 0) return null;

  const [, uidb64, token] = matches[matches.length - 1];
  return `/verify-email/${uidb64}/${token}/`;
}
