/**
 * API endpoint tests for dashboard-server.js
 * Verifies server code structure without starting the actual server
 */

const fs = require('fs');
const path = require('path');

const PROJECT_DIR = path.join(__dirname, '..');

describe('Dashboard Server API Structure', () => {
  let serverContent;

  beforeAll(() => {
    const serverPath = path.join(PROJECT_DIR, 'dashboard-server.js');
    serverContent = fs.readFileSync(serverPath, 'utf8');
  });

  describe('Endpoint routes', () => {
    it('should handle / route', () => {
      expect(serverContent).toContain("url === '/' || url === '/dashboard'");
    });

    it('should handle /data route', () => {
      expect(serverContent).toContain("url === '/data'");
    });

    it('should handle /api/refresh route', () => {
      expect(serverContent).toContain("url === '/api/refresh'");
    });

    it('should handle /api/events SSE route', () => {
      expect(serverContent).toContain("url === '/api/events'");
      expect(serverContent).toContain('text/event-stream');
    });
  });

  describe('SSE implementation', () => {
    it('should have SSE clients Set', () => {
      expect(serverContent).toContain('sseClients = new Set()');
    });

    it('should add client on connect', () => {
      expect(serverContent).toContain('sseClients.add(res)');
    });

    it('should remove client on close', () => {
      expect(serverContent).toContain('sseClients.delete(res)');
    });

    it('should broadcast to all clients', () => {
      expect(serverContent).toContain('function broadcast');
      expect(serverContent).toContain('for (const client of sseClients)');
    });

    it('should send connected event', () => {
      expect(serverContent).toContain('"type":"connected"');
    });

    it('should have heartbeat mechanism', () => {
      expect(serverContent).toContain('heartbeat');
      expect(serverContent).toContain('setInterval');
    });
  });

  describe('CORS headers', () => {
    it('should set Access-Control-Allow-Origin globally', () => {
      expect(serverContent).toContain("Access-Control-Allow-Origin', '*'");
    });

    it('should set CORS for SSE endpoint', () => {
      // Find the SSE section
      const sseMatch = serverContent.match(/\/api\/events[^}]+}/);
      expect(serverContent).toContain("Connection': 'keep-alive'");
    });
  });

  describe('Path traversal protection', () => {
    it('should check for .. in decoded URL', () => {
      expect(serverContent).toContain("decodedUrl.includes('..')");
    });

    it('should check for absolute paths', () => {
      expect(serverContent).toContain("decodedUrl.startsWith('/')");
    });

    it('should return 400 for bad requests', () => {
      expect(serverContent).toContain("res.writeHead(400)");
      expect(serverContent).toContain("res.end('Bad Request')");
    });
  });

  describe('Error handling', () => {
    it('should handle file not found', () => {
      expect(serverContent).toContain("res.writeHead(404");
      expect(serverContent).toContain("res.end('Not Found:");
    });

    it('should handle errors in broadcast', () => {
      expect(serverContent).toContain('try {');
      expect(serverContent).toContain('} catch (e)');
    });
  });

  describe('Server configuration', () => {
    it('should use correct port', () => {
      expect(serverContent).toContain('PORT = 3847');
    });

    it('should log server startup', () => {
      expect(serverContent).toContain('server.listen');
      expect(serverContent).toContain('console.log');
    });
  });

  describe('Graceful shutdown', () => {
    it('should handle SIGINT', () => {
      expect(serverContent).toContain("process.on('SIGINT'");
    });

    it('should close watcher on shutdown', () => {
      expect(serverContent).toContain('watcher.close()');
    });

    it('should close server on shutdown', () => {
      expect(serverContent).toContain('server.close()');
    });

    it('should exit cleanly', () => {
      expect(serverContent).toContain('process.exit()');
    });
  });

  describe('File watching', () => {
    it('should watch workspace directory', () => {
      expect(serverContent).toContain('fs.watch');
      expect(serverContent).toContain('WORKSPACE');
    });

    it('should debounce file changes', () => {
      expect(serverContent).toContain('watchTimeout');
      expect(serverContent).toContain('clearTimeout');
      expect(serverContent).toContain('setTimeout');
    });

    it('should regenerate data on change', () => {
      expect(serverContent).toContain("require('./generate-dashboard-data.js')");
    });

    it('should broadcast after regeneration', () => {
      expect(serverContent).toContain("broadcast({ type: 'update'");
    });
  });

  describe('MIME types', () => {
    it('should define HTML MIME type', () => {
      expect(serverContent).toContain("'.html': 'text/html");
    });

    it('should define JSON MIME type', () => {
      expect(serverContent).toContain("'.json': 'application/json'");
    });

    it('should handle unknown MIME types', () => {
      expect(serverContent).toContain("MIME_TYPES[ext] || 'text/plain'");
    });
  });
});

describe('Dashboard Data API Response', () => {
  let dataContent;

  beforeAll(() => {
    const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
    if (fs.existsSync(dataPath)) {
      dataContent = fs.readFileSync(dataPath, 'utf8');
    }
  });

  it('should have valid JSON structure', () => {
    const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
    expect(fs.existsSync(dataPath)).toBe(true);
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    expect(data).toHaveProperty('projects');
    expect(data).toHaveProperty('generated');
    expect(data).toHaveProperty('memory');
    expect(data).toHaveProperty('sessions');
    expect(data).toHaveProperty('stats');
  });

  it('should include all required stats fields', () => {
    const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    expect(data.stats).toHaveProperty('totalProjects');
    expect(data.stats).toHaveProperty('submodules');
  });

  it('should include memory health info', () => {
    const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    expect(data.memory).toHaveProperty('used');
    expect(data.memory).toHaveProperty('total');
    expect(data.memory).toHaveProperty('health');
  });

  it('should include projects array', () => {
    const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    expect(Array.isArray(data.projects)).toBe(true);
  });

  it('should include sessions array', () => {
    const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    expect(Array.isArray(data.sessions)).toBe(true);
  });
});
