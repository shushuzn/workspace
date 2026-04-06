/**
 * GitHub Issues Importer for Knowledge Bridge
 *
 * Imports GitHub issues as knowledge nodes in the KnowledgeGraph.
 * Supports: title, body, labels, comments, state, author, dates.
 *
 * Usage:
 *   import { importGitHubIssues } from './importers/github-issues.js';
 *   await importGitHubIssues({ owner: 'owner', repo: 'repo', labels: ['bug'] });
 */

const GITHUB_API = 'https://api.github.com';

export interface GitHubIssue {
  number: number;
  title: string;
  body: string | null;
  state: 'open' | 'closed';
  labels: { id: number; name: string; color: string }[];
  user: { login: string; avatar_url: string };
  created_at: string;
  updated_at: string;
  comments: number;
  html_url: string;
}

export interface GitHubComment {
  id: number;
  body: string;
  user: { login: string };
  created_at: string;
}

export interface ImportOptions {
  owner: string;
  repo: string;
  labels?: string[];       // filter by labels (comma-separated or array)
  state?: 'open' | 'closed' | 'all';
  maxPerPage?: number;
  maxPages?: number;
  includeComments?: boolean;
  token?: string;          // GitHub token for higher rate limits
}

interface GraphNode {
  id: string;
  label: string;
  domain: string;
  description: string;
  connections: string[];
  metadata: Record<string, unknown>;
}

interface GraphEdge {
  from: string;
  to: string;
  type: string;
  strength: number;
  id: string;
}

// Minimal GitHub Graph type compatible with knowledgeGraph.js
export class GitHubIssuesImporter {
  private token?: string;

  constructor(token?: string) {
    this.token = token;
  }

  private async request<T>(path: string): Promise<T> {
    const headers: Record<string, string> = {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'knowledge-bridge-importer',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const res = await fetch(`${GITHUB_API}${path}`, { headers });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`GitHub API error ${res.status}: ${text}`);
    }
    return res.json() as Promise<T>;
  }

  async fetchIssues(opts: ImportOptions): Promise<GitHubIssue[]> {
    const { owner, repo, labels, state = 'open', maxPerPage = 100, maxPages = 5 } = opts;
    const allIssues: GitHubIssue[] = [];

    const labelParam = labels ? `&labels=${Array.isArray(labels) ? labels.join(',') : labels}` : '';
    const stateParam = `&state=${state}`;

    for (let page = 1; page <= maxPages; page++) {
      const url = `/repos/${owner}/${repo}/issues?per_page=${maxPerPage}&page=${page}${stateParam}${labelParam}`;
      const issues: GitHubIssue[] = await this.request(url);
      // Filter out pull requests (they appear in issues API but have pull_request property)
      const pureIssues = issues.filter(i => !('pull_request' in i));
      allIssues.push(...pureIssues);
      if (pureIssues.length < maxPerPage) break;
    }

    return allIssues;
  }

  async fetchComments(owner: string, repo: string, issueNumber: number): Promise<GitHubComment[]> {
    try {
      return await this.request<GitHubComment[]>(
        `/repos/${owner}/${repo}/issues/${issueNumber}/comments?per_page=100`
      );
    } catch {
      return [];
    }
  }

  /**
   * Import issues as knowledge graph nodes.
   * Returns { nodes, edges } suitable for merging into KnowledgeGraph.
   */
  async importIssues(opts: ImportOptions): Promise<{ nodes: GraphNode[]; edges: GraphEdge[] }> {
    const { owner, repo, includeComments = false } = opts;

    const issues = await this.fetchIssues(opts);
    const nodes: GraphNode[] = [];
    const edges: GraphEdge[] = [];
    const domain = `github:${owner}/${repo}`;
    let nodeId = 0;

    for (const issue of issues) {
      const issueId = `gh-${owner}-${repo}-${issue.number}`;
      const labelList = issue.labels.map(l => l.name);

      // Main issue node
      nodes.push({
        id: issueId,
        label: `[Issue #${issue.number}] ${issue.title}`,
        domain,
        description: issue.body?.slice(0, 500) || '(no description)',
        connections: [],
        metadata: {
          type: 'github_issue',
          number: issue.number,
          state: issue.state,
          author: issue.user.login,
          labels: labelList,
          createdAt: issue.created_at,
          updatedAt: issue.updated_at,
          url: issue.html_url,
          commentCount: issue.comments,
        },
      });

      // Label nodes
      for (const label of issue.labels) {
        const labelId = `gh-label-${owner}-${repo}-${label.name.replace(/[^a-zA-Z0-9]/g, '_')}`;
        if (!nodes.find(n => n.id === labelId)) {
          nodes.push({
            id: labelId,
            label: `label:${label.name}`,
            domain,
            description: `GitHub label: ${label.name} (color: #${label.color})`,
            connections: [],
            metadata: { type: 'github_label', color: label.color },
          });
        }
        edges.push({ from: issueId, to: labelId, type: 'has_label', strength: 1, id: `e-${nodeId++}` });
      }

      // Author node
      const authorId = `gh-user-${issue.user.login}`;
      if (!nodes.find(n => n.id === authorId)) {
        nodes.push({
          id: authorId,
          label: `@${issue.user.login}`,
          domain: 'github:users',
          description: `GitHub user: ${issue.user.login}`,
          connections: [],
          metadata: { type: 'github_user', avatar: issue.user.avatar_url },
        });
      }
      edges.push({ from: issueId, to: authorId, type: 'authored_by', strength: 0.8, id: `e-${nodeId++}` });

      // Comments
      if (includeComments && issue.comments > 0) {
        const comments = await this.fetchComments(owner, repo, issue.number);
        for (const comment of comments.slice(0, 10)) { // limit to 10 comments per issue
          const commentId = `gh-comment-${owner}-${repo}-${issue.number}-${comment.id}`;
          nodes.push({
            id: commentId,
            label: `Comment by @${comment.user.login} on #${issue.number}`,
            domain,
            description: comment.body?.slice(0, 300) || '',
            connections: [],
            metadata: {
              type: 'github_comment',
              author: comment.user.login,
              createdAt: comment.created_at,
              onIssue: issue.number,
            },
          });
          edges.push({ from: commentId, to: issueId, type: 'comment_on', strength: 0.5, id: `e-${nodeId++}` });

          // Comment author
          const commentAuthorId = `gh-user-${comment.user.login}`;
          if (!nodes.find(n => n.id === commentAuthorId)) {
            nodes.push({
              id: commentAuthorId,
              label: `@${comment.user.login}`,
              domain: 'github:users',
              description: `GitHub user: ${comment.user.login}`,
              connections: [],
              metadata: { type: 'github_user' },
            });
          }
          edges.push({ from: commentId, to: commentAuthorId, type: 'authored_by', strength: 0.8, id: `e-${nodeId++}` });
        }
      }
    }

    return { nodes, edges };
  }
}

/**
 * CLI entry point:
 * node src/importers/github-issues.js --owner <owner> --repo <repo> [--labels bug,enhancement] [--token <ghp_xxx>]
 */
async function main() {
  const args = process.argv.slice(2);
  const get = (flag: string) => {
    const idx = args.indexOf(flag);
    return idx >= 0 ? args[idx + 1] : undefined;
  };

  const owner = get('--owner');
  const repo = get('--repo');
  if (!owner || !repo) {
    console.error('Usage: node github-issues.js --owner <owner> --repo <repo> [--labels bug,enhancement] [--token <token>]');
    process.exit(1);
  }

  const labels = get('--labels');
  const token = get('--token');
  const importer = new GitHubIssuesImporter(token);

  console.log(`Fetching issues from ${owner}/${repo}...`);
  const result = await importer.importIssues({
    owner,
    repo,
    labels: labels?.split(','),
    includeComments: false,
  });

  console.log(`Imported: ${result.nodes.length} nodes, ${result.edges.length} edges`);

  // Output as JSON for piping to other tools
  console.log(JSON.stringify(result, null, 2));
}

if (require.main === module) {
  main().catch(e => { console.error(e); process.exit(1); });
}
