// ~/.omc/patrol-agent/src/research.js
// Web research integration: GitHub search + arXiv

import { execSync } from 'child_process';

/**
 * Search GitHub repositories via public REST API.
 * @param {string} query
 * @returns {Promise<Array<{title: string, url: string, stars: number, description: string}>>}
 */
export async function searchGitHub(query) {
  try {
    const url = `https://api.github.com/search/repositories?q=${encodeURIComponent(query)}&per_page=5&sort=stars`;
    const output = execSync(
      `curl -s -H "Accept: application/vnd.github.v3+json" "${url}"`,
      { encoding: 'utf-8', timeout: 15000 }
    );
    const data = JSON.parse(output);
    if (!data.items) return [];
    return data.items.map(item => ({
      title: item.full_name,
      url: item.html_url,
      stars: item.stargazers_count,
      description: item.description || '',
    }));
  } catch {
    return [];
  }
}

/**
 * Search arXiv via public Atom feed.
 * @param {string} query
 * @returns {Promise<Array<{title: string, url: string, summary: string, published: string}>>}
 */
export async function searchArxiv(query) {
  try {
    const url = `https://export.arxiv.org/api/query?search_query=all:${encodeURIComponent(query)}&max_results=5&sortBy=relevance`;
    const output = execSync(
      `curl -s "${url}"`,
      { encoding: 'utf-8', timeout: 15000 }
    );
    // Simple XML parsing for arXiv Atom feed
    const entries = [];
    const entryMatches = output.matchAll(/<entry>([\s\S]*?)<\/entry>/g);
    for (const match of entryMatches) {
      const entry = match[1];
      const title = (entry.match(/<title>([\s\S]*?)<\/title>/) || ['', ''])[1].trim();
      const url = (entry.match(/<id>([\s\S]*?)<\/id>/) || ['', ''])[1].trim();
      const summary = (entry.match(/<summary>([\s\S]*?)<\/summary>/) || ['', ''])[1].trim().slice(0, 300);
      const published = (entry.match(/<published>([\s\S]*?)<\/published>/) || ['', ''])[1].trim();
      if (title && url) {
        entries.push({ title, url, summary, published });
      }
    }
    return entries;
  } catch {
    return [];
  }
}

/**
 * Run deep research on a topic and return ranked ideas.
 * @param {string} topic
 * @returns {Promise<Array<{title: string, url: string, summary: string, confidence: number, source: string}>>}
 */
export async function deepResearch(topic) {
  const [githubResults, arxivResults] = await Promise.all([
    searchGitHub(topic),
    searchArxiv(topic),
  ]);

  const ideas = [];

  for (const item of githubResults) {
    const confidence = Math.min(1, 0.5 + (item.stars / 10000));
    ideas.push({
      title: item.title,
      url: item.url,
      summary: item.description,
      confidence,
      source: 'github',
      generated_at: new Date().toISOString(),
    });
  }

  for (const item of arxivResults) {
    const age = item.published ? (Date.now() - new Date(item.published).getTime()) / (1000 * 60 * 60 * 24 * 30) : 12;
    const confidence = Math.max(0.3, 0.9 - age * 0.05);
    ideas.push({
      title: item.title,
      url: item.url,
      summary: item.summary,
      confidence,
      source: 'arxiv',
      generated_at: new Date().toISOString(),
    });
  }

  // Sort by confidence descending
  ideas.sort((a, b) => b.confidence - a.confidence);
  return ideas;
}
