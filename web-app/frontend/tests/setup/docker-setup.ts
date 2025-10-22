import { chromium, FullConfig } from '@playwright/test';

const dockerComposeFile = '../../docker-compose-test.yml';

/**
 * Global setup for Docker-based E2E tests.
 * Assumes Docker Compose services are already running with docker-compose-test.yml.
 *
 * This script:
 * 1. Waits for Django server to be ready
 * 2. Initializes test database with migrations and fixtures
 * 3. Creates a test user for authentication tests
 */
async function globalSetup(config: FullConfig) {
  console.log('🐳 Setting up test environment...');

  const baseURL = config.projects[0].use?.baseURL || 'http://localhost:8000';

  // Wait for Django to be ready
  console.log(`⏳ Waiting for Django at ${baseURL}...`);
  await waitForServer(baseURL, 60000);
  console.log('✅ Django is ready!');

  // Initialize test database
  console.log('📦 Initializing test database...');
  await setupTestDatabase();
  console.log('✅ Test database initialized!');

  console.log('✅ Setup complete! Ready to run tests.\n');
}

/**
 * Wait for server to respond to HTTP requests
 */
async function waitForServer(url: string, timeout: number): Promise<void> {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    try {
      const response = await page.goto(url, {
        timeout: 5000,
        waitUntil: 'domcontentloaded',
      });

      if (response && (response.ok() || response.status() === 404)) {
        // 404 is okay - means server is running, just no page at /
        await browser.close();
        return;
      }
    } catch (error) {
      // Server not ready yet, wait and retry
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
  }

  await browser.close();
  throw new Error(
    `Server at ${url} did not start within ${timeout}ms.\n` +
      `Make sure Docker Compose is running: docker-compose up -d`,
  );
}

/**
 * Initialize test database with migrations and fixtures
 */
async function setupTestDatabase(): Promise<void> {
  // Step 1: Run migrations
  console.log('  Running migrations...');
  await runDjangoCommand('python manage.py migrate', true);

  // Step 2: Create required users (ddmal for imports, testuser for tests)
  console.log('  Creating required users...');
  await createRequiredUsers();

  // Step 3: Import languages
  console.log('  Importing languages...');
  try {
    await runDjangoCommand('python manage.py import_languages', true);
  } catch (error) {
    console.warn(
      '⚠️  Language import failed (API may be rate-limited). Continuing...',
    );
  }

  // Step 4: Import instruments
  console.log('  Importing 200 test instruments...');
  await runDjangoCommand('python manage.py import_instruments', true);
}

/**
 * Run Django management command in test mode
 * @param command - Django management command to run
 * @param suppressOutput - If true, only show summary, not full output
 */
async function runDjangoCommand(
  command: string,
  suppressOutput = false,
): Promise<void> {
  const { spawn } = await import('child_process');

  return new Promise((resolve, reject) => {
    const proc = spawn(
      'docker-compose',
      [
        '-f',
        dockerComposeFile,
        'exec',
        '-T',
        'app',
        'sh',
        '-c',
        `cd vim-app && ${command}`,
      ],
      { cwd: process.cwd() },
    );

    let output = '';
    let errorOutput = '';

    proc.stdout?.on('data', (data) => {
      output += data.toString();
    });

    proc.stderr?.on('data', (data) => {
      const err = data.toString();
      // Filter out common warnings and info messages that aren't actual errors
      const isWarning =
        err.includes('warning') ||
        err.includes('level=') ||
        err.includes('Skipping language') ||
        err.toLowerCase().includes('info');

      if (!isWarning) {
        errorOutput += err;
      }
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(
          new Error(
            `Command failed: ${command} (exit code ${code})\n${errorOutput}\n` +
              'Make sure Docker containers are running: docker-compose up -d',
          ),
        );
      } else {
        // Only show summary lines, not full verbose output
        if (output && !suppressOutput) {
          console.log(output.trim());
        } else if (output && suppressOutput) {
          // Extract and show only important summary lines
          const lines = output.trim().split('\n');
          const summaryLines = lines.filter(
            (line) =>
              line.includes('Successfully') ||
              line.includes('imported') ||
              line.includes('created') ||
              line.includes('✓'),
          );
          if (summaryLines.length > 0) {
            console.log('    ' + summaryLines.join('\n    '));
          }
        }
        resolve();
      }
    });
  });
}

/**
 * Create required users in Django database (in test database)
 * Creates both ddmal (for data imports) and testuser (for authentication tests)
 */
async function createRequiredUsers(): Promise<void> {
  const { spawn } = await import('child_process');

  const createUserScript = `
from django.contrib.auth import get_user_model
User = get_user_model()

# Create ddmal user (required for import_instruments command)
if not User.objects.filter(username='ddmal').exists():
    User.objects.create_superuser('ddmal', 'ddmal@test.com', 'ddmalpass123')
    print('✓ DDMAL user created')
else:
    print('✓ DDMAL user already exists')

# Create testuser (for authentication tests)
if not User.objects.filter(username='testuser').exists():
    User.objects.create_superuser('testuser', 'test@example.com', 'testpass123')
    print('✓ Test user created')
else:
    print('✓ Test user already exists')
`;

  return new Promise((resolve, reject) => {
    const proc = spawn(
      'docker-compose',
      [
        '-f',
        dockerComposeFile,
        'exec',
        '-T',
        'app',
        'sh',
        '-c',
        'cd vim-app && python manage.py shell',
      ],
      { cwd: process.cwd() },
    );

    let output = '';
    let errorOutput = '';

    proc.stdout?.on('data', (data) => {
      output += data.toString();
    });

    proc.stderr?.on('data', (data) => {
      const err = data.toString();
      if (!err.includes('warning') && !err.includes('level=')) {
        errorOutput += err;
      }
    });

    proc.on('close', (code) => {
      if (code !== 0) {
        reject(
          new Error(
            `Failed to create test user (exit code ${code}).\n${errorOutput}\n` +
              'Make sure Docker containers are running from project root: docker-compose -f docker-compose-test.yml up -d',
          ),
        );
      } else {
        if (output) {
          console.log(output.trim());
        }
        resolve();
      }
    });

    // Send Python script to stdin
    proc.stdin?.write(createUserScript);
    proc.stdin?.end();
  });
}

export default globalSetup;
