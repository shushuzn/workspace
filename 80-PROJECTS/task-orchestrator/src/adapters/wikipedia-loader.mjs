import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { readFileSync, existsSync } from 'fs';
const __DIR = dirname(fileURLToPath(import.meta.url));
const WORKSPACE_ROOT = join(__DIR, '..', '..', '..', '..', '..');
const WIKIPEDIA_INDEX = join(WORKSPACE_ROOT, 'knowledge', 'wikipedia', 'index.json');
export class ArticleLoader {
    index = null;
    loadIndex() {
        if (!this.index && existsSync(WIKIPEDIA_INDEX)) {
            try {
                this.index = JSON.parse(readFileSync(WIKIPEDIA_INDEX, 'utf-8'));
            }
            catch {
                this.index = { articles: [] };
            }
        }
        return this.index || { articles: [] };
    }
    search(query) {
        const q = query.toLowerCase();
        const idx = this.loadIndex();
        return idx.articles.filter(a => a.title.toLowerCase().includes(q) ||
            a.category.toLowerCase().includes(q) ||
            (a.tags && a.tags.some(t => t.toLowerCase().includes(q))));
    }
    retrieve(title) {
        const idx = this.loadIndex();
        return idx.articles.find(a => a.title.includes(title) || a.id.includes(title)) || null;
    }
    getAll() {
        return this.loadIndex().articles;
    }
}
export class WikipediaLoaderAdapter {
    id = 'wikipedia';
    type = 'wikipedia';
    loader = new ArticleLoader();
    canHandle(step) {
        return step.adapterType === 'wikipedia';
    }
    async execute(step, _ctx) {
        const { action, query } = this.parseArgs(step.args);
        if (action === 'search') {
            const results = this.loader.search(query || '');
            return {
                success: true,
                output: JSON.stringify(results, null, 2),
                logs: '',
                artifacts: [],
                fatal: false,
            };
        }
        else if (action === 'retrieve') {
            const article = this.loader.retrieve(query || '');
            return {
                success: true,
                output: article ? JSON.stringify(article, null, 2) : 'Article not found',
                logs: '',
                artifacts: [],
                fatal: false,
            };
        }
        else if (action === 'list') {
            const all = this.loader.getAll();
            return {
                success: true,
                output: `Total articles: ${all.length}\n` + all.map(a => `  - [${a.category}] ${a.title}`).join('\n'),
                logs: '',
                artifacts: [],
                fatal: false,
            };
        }
        return { success: false, output: 'Unknown action', logs: '', artifacts: [], error: 'Unknown action: use search <query>, retrieve <title>, or list', fatal: false };
    }
    async checkAvailable() {
        return existsSync(WIKIPEDIA_INDEX);
    }
    register() {
        return {
            adapterId: this.id,
            adapterType: this.type,
            name: 'Wikipedia Knowledge Base',
            description: 'Search and retrieve from Wikipedia knowledge base',
            keywords: ['wiki', 'knowledge', 'article', 'wikipedia'],
            commands: ['search', 'retrieve', 'list'],
            capabilities: ['search', 'retrieve', 'list'],
        };
    }
    parseArgs(args) {
        if (args.length === 0)
            return { action: 'list', query: '' };
        const [action, ...rest] = args;
        return { action, query: rest.join(' ') };
    }
}
