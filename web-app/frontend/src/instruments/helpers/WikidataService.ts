import { WikidataQueryResult, NameQueryResult } from '../Types';

export class WikidataService {
  private static readonly ENDPOINT_URL = 'https://query.wikidata.org/sparql';

  /**
   * Checks if a name already exists in Wikidata for the given language
   */
  static async checkIfNameExists(
    wikidataId: string,
    languageCode: string,
    nameInput: string,
  ): Promise<WikidataQueryResult> {
    const sparqlQuery = `
      SELECT ?nameLabel WHERE {
        wd:${wikidataId} (rdfs:label|skos:altLabel) ?nameLabel .
        FILTER(LANG(?nameLabel) = "${languageCode}" && CONTAINS(LCASE(?nameLabel),"${nameInput.toLowerCase()}"))
      } LIMIT 1
    `;

    try {
      const data = await this.executeSparqlQuery(sparqlQuery);

      if (data.results.bindings.length > 0) {
        return { exists: true, name: data.results.bindings[0].nameLabel.value };
      } else {
        return { exists: false };
      }
    } catch (error) {
      console.error('Error querying Wikidata:', error);
      throw new Error('Wikidata query failed');
    }
  }

  /**
   * Checks if name entry is a label or an alias in Wikidata
   */
  static async checkIfAlias(
    wikidataId: string,
    languageCode: string,
  ): Promise<WikidataQueryResult> {
    const sparqlQuery = `
      SELECT ?nameLabel WHERE {
        wd:${wikidataId} rdfs:label ?nameLabel .
        FILTER(LANG(?nameLabel) = "${languageCode}")
      } LIMIT 1
    `;

    try {
      const data = await this.executeSparqlQuery(sparqlQuery);

      if (data.results.bindings.length > 0) {
        return { exists: true, name: data.results.bindings[0].nameLabel.value };
      } else {
        return { exists: false };
      }
    } catch (error) {
      console.error('Error querying Wikidata:', error);
      throw new Error('Wikidata query failed');
    }
  }

  /**
   * Executes a SPARQL query against Wikidata
   */
  private static async executeSparqlQuery(
    sparqlQuery: string,
  ): Promise<NameQueryResult> {
    const queryUrl = `${this.ENDPOINT_URL}?query=${encodeURIComponent(sparqlQuery)}&format=json`;

    const response = await fetch(queryUrl);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
}
