import { NameValidator } from './NameValidator';

describe('NameValidator', () => {
  let validator: NameValidator;

  beforeEach(() => {
    validator = new NameValidator([]);
  });

  describe('validateNameField', () => {
    it('should return error for empty string', () => {
      const result = validator.validateNameField('');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
      expect(result.message).toContain('Please enter a name');
    });

    it('should return error for whitespace only', () => {
      const result = validator.validateNameField('   ');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
    });

    it('should return success for valid name', () => {
      const result = validator.validateNameField('Guitar');
      expect(result.isValid).toBe(true);
      expect(result.type).toBe('success');
    });
  });

  describe('validateSource', () => {
    it('should return error for empty string', () => {
      const result = validator.validateSource('');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
      expect(result.message).toContain('Please enter the source');
    });

    it('should return error for whitespace only', () => {
      const result = validator.validateSource('   ');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
    });

    it('should return success for valid source', () => {
      const result = validator.validateSource('Wikipedia');
      expect(result.isValid).toBe(true);
      expect(result.type).toBe('success');
    });
  });

  describe('validateNameId', () => {
    it('should return error for null', () => {
      const result = validator.validateNameId(null);
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
      expect(result.message).toContain('No instrument name ID');
    });

    it('should return error for empty string', () => {
      const result = validator.validateNameId('');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
    });

    it('should return error for whitespace only', () => {
      const result = validator.validateNameId('   ');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
    });

    it('should return success for valid ID', () => {
      const result = validator.validateNameId('123');
      expect(result.isValid).toBe(true);
      expect(result.type).toBe('success');
    });
  });

  describe('validateModalData', () => {
    it('should return error when name is null', () => {
      const result = validator.validateModalData(null, 'en', 'Wikipedia');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
      expect(result.message).toContain('Missing required instrument data');
    });

    it('should return error when language is null', () => {
      const result = validator.validateModalData('Guitar', null, 'Wikipedia');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
    });

    it('should return error when source is null', () => {
      const result = validator.validateModalData('Guitar', 'en', null);
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
    });

    it('should return success when all fields present', () => {
      const result = validator.validateModalData('Guitar', 'en', 'Wikipedia');
      expect(result.isValid).toBe(true);
      expect(result.type).toBe('success');
    });
  });

  describe('validateDeletion', () => {
    it('should return error for invalid name ID', () => {
      const result = validator.validateDeletion(
        null,
        'Guitar',
        'en',
        'Wikipedia',
      );
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
    });

    it('should return error for invalid modal data', () => {
      const result = validator.validateDeletion('123', null, 'en', 'Wikipedia');
      expect(result.isValid).toBe(false);
      expect(result.type).toBe('error');
    });

    it('should return success when all valid', () => {
      const result = validator.validateDeletion(
        '123',
        'Guitar',
        'en',
        'Wikipedia',
      );
      expect(result.isValid).toBe(true);
      expect(result.type).toBe('success');
    });
  });
});
