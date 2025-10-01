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
    expect(cookieValue).toBe('sessionId=abc123; path=/');
  });

  it('should set cookie with custom path', () => {
    setCookie('sessionId', 'abc123', '/admin');
    expect(cookieValue).toBe('sessionId=abc123; path=/admin');
  });

  it('should set cookie with domain', () => {
    setCookie('sessionId', 'abc123', '/', 'example.com');
    expect(cookieValue).toBe('sessionId=abc123; path=/; domain=example.com');
  });
});
