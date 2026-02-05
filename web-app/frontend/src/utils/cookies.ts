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

    const key = decodeURIComponent(cookieString.slice(0, equalIndex).trim());

    // Early return if we found our target cookie
    if (key === name) {
      const value = decodeURIComponent(
        cookieString.slice(equalIndex + 1).trim(),
      );
      return value || undefined; // Return undefined for empty values
    }
  }

  return undefined;
}

/**
 * Sets a cookie with the specified name and value
 * Works reliably on Chrome, Firefox, Safari, WebKit (locally and CI)
 * @param name - Cookie name
 * @param value - Cookie value
 * @param options - Optional settings
 * @param options.days - Number of days until expiration (default 365)
 * @param options.path - Cookie path (default '/')
 * @param options.domain - Cookie domain (optional, avoid unless necessary)
 * @param options.sameSite - SameSite policy ('Lax' by default)
 * @param options.secure - Whether cookie is Secure (default false)
 */
export function setCookie(
  name: string,
  value: string,
  options: {
    days?: number;
    path?: string;
    domain?: string;
    sameSite?: 'Lax' | 'Strict' | 'None';
    secure?: boolean;
  } = {},
): void {
  const {
    days = 365,
    path = '/',
    domain,
    sameSite = 'Lax',
    secure = false,
  } = options;

  const encodedName = encodeURIComponent(name);
  const encodedValue = encodeURIComponent(value);

  let cookieString = `${encodedName}=${encodedValue}`;

  // Set expiration date
  if (days > 0) {
    const expirationDate = new Date();
    expirationDate.setTime(
      expirationDate.getTime() + days * 24 * 60 * 60 * 1000,
    );
    cookieString += `; expires=${expirationDate.toUTCString()}`;
  } else if (days === 0) {
    // Immediate expiration → delete cookie
    cookieString += `; expires=Thu, 01 Jan 1970 00:00:00 GMT`;
  }
  // else no expiration = session cookie

  // Set path
  cookieString += `; path=${path}`;

  // Set domain if provided (only if necessary)
  if (domain) {
    cookieString += `; domain=${domain}`;
  }

  // SameSite attribute
  cookieString += `; SameSite=${sameSite}`;

  // Secure attribute required if SameSite=None
  const mustSecure = sameSite === 'None';
  if (secure || mustSecure) {
    cookieString += `; Secure`;
  }

  document.cookie = cookieString;
}

/**
 * Deletes a cookie by setting its expiration date in the past.
 * Make sure to use the same path and domain as when the cookie was set.
 *
 * @param name - The name of the cookie to delete
 * @param options - Optional cookie attributes to match for deletion
 * @param options.path - The path of the cookie (default '/')
 * @param options.domain - The domain of the cookie (optional)
 */
export function deleteCookie(
  name: string,
  options: { path?: string; domain?: string } = {},
): void {
  const { path = '/', domain } = options;

  let cookieString = `${encodeURIComponent(name)}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=${path}`;

  if (domain) {
    cookieString += `; domain=${domain}`;
  }

  // Setting Secure or SameSite not needed when deleting cookies
  document.cookie = cookieString;
}

/**
 * Retrieves CSRF token from Django's csrftoken cookie.
 * Django automatically sets this cookie for CSRF protection.
 * @throws {Error} If CSRF token cookie not found or empty
 * @returns CSRF token string
 */
export function getCsrfToken(): string {
  const token = readCookie('csrftoken');

  if (!token) {
    throw new Error(
      'Security token not found. Please refresh the page and try again.',
    );
  }

  return token;
}
