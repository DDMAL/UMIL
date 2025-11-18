import { readCookie, setCookie } from './cookies';

describe('readCookie', () => {
  beforeEach(() => {
    Object.defineProperty(document, 'cookie', {
      writable: true,
      value: '',
      configurable: true,
    });
  });

  it('should return value when cookie exists', () => {
    document.cookie = 'sessionId=abc123';
    expect(readCookie('sessionId')).toBe('abc123');
  });

  it('should return undefined when cookie does not exist', () => {
    document.cookie = 'sessionId=abc123';
    expect(readCookie('userId')).toBeUndefined();
  });

  it('should return undefined when document.cookie is empty', () => {
    document.cookie = '';
    expect(readCookie('sessionId')).toBeUndefined();
  });

  it('should return correct value with multiple cookies', () => {
    document.cookie = 'sessionId=abc123; userId=user456; theme=dark';
    expect(readCookie('userId')).toBe('user456');
  });

  it('should return undefined for cookie with empty value', () => {
    document.cookie = 'sessionId=';
    expect(readCookie('sessionId')).toBeUndefined();
  });
});

describe('setCookie', () => {
  let cookieValue: string;

  beforeEach(() => {
    cookieValue = '';
    Object.defineProperty(document, 'cookie', {
      get: () => cookieValue,
      set: (value: string) => {
        cookieValue = value;
      },
      configurable: true,
    });
  });

  it('should set cookie with default path', () => {
    setCookie('sessionId', 'abc123');
    expect(cookieValue).toContain('sessionId=abc123');
    expect(cookieValue).toContain('path=/');
    expect(cookieValue).toContain('SameSite=Lax');
    expect(cookieValue).toContain('expires=');
  });

  it('should set cookie with custom path', () => {
    setCookie('sessionId', 'abc123', { path: '/admin' });
    expect(cookieValue).toContain('sessionId=abc123');
    expect(cookieValue).toContain('path=/admin');
    expect(cookieValue).toContain('SameSite=Lax');
    expect(cookieValue).toContain('expires=');
  });

  it('should set cookie with domain', () => {
    setCookie('sessionId', 'abc123', { path: '/', domain: 'example.com' });
    expect(cookieValue).toContain('sessionId=abc123');
    expect(cookieValue).toContain('path=/');
    expect(cookieValue).toContain('domain=example.com');
    expect(cookieValue).toContain('SameSite=Lax');
    expect(cookieValue).toContain('expires=');
  });

  it('should set session cookie when days is 0', () => {
    setCookie('sessionId', 'abc123', { days: 0 });
    expect(cookieValue).toContain('sessionId=abc123');
    expect(cookieValue).toContain('path=/');
    expect(cookieValue).toContain('SameSite=Lax');
    expect(cookieValue).toContain('expires=Thu, 01 Jan 1970 00:00:00 GMT');
  });

  it('should set cookie with custom SameSite', () => {
    setCookie('sessionId', 'abc123', { sameSite: 'Strict' });
    expect(cookieValue).toContain('sessionId=abc123');
    expect(cookieValue).toContain('SameSite=Strict');
  });

  it('should set secure cookie when SameSite is None', () => {
    setCookie('sessionId', 'abc123', { sameSite: 'None' });
    expect(cookieValue).toContain('sessionId=abc123');
    expect(cookieValue).toContain('SameSite=None');
    expect(cookieValue).toContain('Secure');
  });

  it('should URL encode cookie name and value', () => {
    setCookie('session id', 'value with spaces');
    expect(cookieValue).toContain('session%20id=value%20with%20spaces');
    expect(cookieValue).toContain('path=/');
  });
});
