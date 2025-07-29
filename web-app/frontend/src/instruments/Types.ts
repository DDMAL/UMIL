export type DisplayMode = 'masonry' | 'standard';

export type PaginateBy = 20 | 50 | 100;

/**
 * Instrument Name Entry
 */
export type NameEntry = {
  language: string;
  name: string;
  source: string;
  alias?: string; // Optional - used during publishing
};

export type AddNameForm = {
  display_name: string;
  wikidata_id: string;
  names: NameEntry[];
};

export type WikidataQueryResult = {
  exists: boolean;
  name?: string;
};

export type NameBinding = {
  nameLabel: {
    type: string;
    value: string;
    'xml:lang'?: string;
  };
};

export type NameQueryResult = {
  head: { vars: string[] };
  results: { bindings: NameBinding[] };
};

export type WikidataLanguage = {
  wikidata_code: string;
  autonym: string;
  en_label: string;
};

export type ValidationResult = {
  isValid: boolean;
  message: string;
  type: 'success' | 'error' | 'warning';
};
