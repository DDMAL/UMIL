import { CookieDictionary } from './interfaces';

/**
 * Reads a cookie value by name from document.cookie
 * @param name - The name of the cookie to retrieve
 * @returns The cookie value if found, undefined otherwise
 */
export function readCookie(name: string): string | undefined {
  // Early return if no cookies exist
  if (!document.cookie) {
    return undefined;
  }

  // Split and parse cookies - stop early if we find the target cookie
  const cookieStrings = document.cookie.split('; ');

  for (const cookieString of cookieStrings) {
    const equalIndex = cookieString.indexOf('=');

    // Skip malformed cookies (no '=' found)
    if (equalIndex === -1) continue;

    const key = cookieString.slice(0, equalIndex).trim();

    // Early return if we found our target cookie
    if (key === name) {
      const value = cookieString.slice(equalIndex + 1).trim();
      return value || undefined; // Return undefined for empty values
    }
  }

  return undefined;
}

/**
 * Sets a cookie with the specified name and value
 * @param name - The name of the cookie
 * @param value - The value of the cookie
 * @param path - The path of the cookie (defaults to '/')
 * @param domain - The domain of the cookie (optional)
 */
export function setCookie(
  name: string,
  value: string,
  path: string = '/',
  domain?: string,
): void {
  let cookieString = `${name}=${value}; path=${path}`;

  if (domain) {
    cookieString += `; domain=${domain}`;
  }

  document.cookie = cookieString;
}
