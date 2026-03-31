/**
 * Integration tests for dashboard-server.js
 */

const fs = require('fs');
const path = require('path');

const PROJECT_DIR = path.join(__dirname, '..');

describe('dashboard-server.js integration', () => {
  describe('File structure', () => {
    it('should have dashboard.html', () => {
      const htmlPath = path.join(PROJECT_DIR, 'dashboard.html');
      expect(fs.existsSync(htmlPath)).toBe(true);
      const content = fs.readFileSync(htmlPath, 'utf8');
      expect(content.length).toBeGreaterThan(100);
    });

    it('should have dashboard-server.js', () => {
      const serverPath = path.join(PROJECT_DIR, 'dashboard-server.js');
      expect(fs.existsSync(serverPath)).toBe(true);
      const content = fs.readFileSync(serverPath, 'utf8');
      expect(content.includes('http.createServer')).toBe(true);
    });

    it('should have generate-dashboard-data.js', () => {
      const genPath = path.join(PROJECT_DIR, 'generate-dashboard-data.js');
      expect(fs.existsSync(genPath)).toBe(true);
    });

    it('should have package.json', () => {
      const pkgPath = path.join(PROJECT_DIR, 'package.json');
      expect(fs.existsSync(pkgPath)).toBe(true);
    });
  });

  describe('dashboard-server.js content', () => {
    it('should use correct port', () => {
      const serverPath = path.join(PROJECT_DIR, 'dashboard-server.js');
      const content = fs.readFileSync(serverPath, 'utf8');
      expect(content).toContain('PORT = 3847');
    });

    it('should have SSE endpoint', () => {
      const serverPath = path.join(PROJECT_DIR, 'dashboard-server.js');
      const content = fs.readFileSync(serverPath, 'utf8');
      expect(content).toContain('/api/events');
    });

    it('should have path traversal protection', () => {
      const serverPath = path.join(PROJECT_DIR, 'dashboard-server.js');
      const content = fs.readFileSync(serverPath, 'utf8');
      expect(content).toContain('path traversal');
    });

    it('should have graceful shutdown', () => {
      const serverPath = path.join(PROJECT_DIR, 'dashboard-server.js');
      const content = fs.readFileSync(serverPath, 'utf8');
      expect(content).toContain('SIGINT');
    });

    it('should have SSE heartbeat', () => {
      const serverPath = path.join(PROJECT_DIR, 'dashboard-server.js');
      const content = fs.readFileSync(serverPath, 'utf8');
      expect(content).toContain('heartbeat');
    });
  });

  describe('generate-dashboard-data.js integration', () => {
    it('should generate valid dashboard-data.json', () => {
      const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
      expect(fs.existsSync(dataPath)).toBe(true);
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

      expect(data).toHaveProperty('projects');
      expect(Array.isArray(data.projects)).toBe(true);
      expect(data).toHaveProperty('generated');
      expect(data).toHaveProperty('memory');
      expect(data).toHaveProperty('sessions');
      expect(data).toHaveProperty('stats');
    });

    it('should have valid project structure', () => {
      const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

      if (data.projects.length > 0) {
        const project = data.projects[0];
        expect(project).toHaveProperty('name');
        expect(typeof project.name).toBe('string');
        expect(project).toHaveProperty('meta');
        expect(typeof project.meta).toBe('string');
      }
    });

    it('should have memory stats', () => {
      const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

      expect(data.memory).toHaveProperty('used');
      expect(data.memory).toHaveProperty('total');
      expect(data.memory).toHaveProperty('health');
    });

    it('should have sessions array', () => {
      const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

      expect(Array.isArray(data.sessions)).toBe(true);
    });

    it('should have stats', () => {
      const dataPath = path.join(PROJECT_DIR, 'dashboard-data.json');
      const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));

      expect(data.stats).toHaveProperty('totalProjects');
      expect(data.stats).toHaveProperty('submodules');
    });
  });

  describe('package.json', () => {
    it('should have required scripts', () => {
      const pkgPath = path.join(PROJECT_DIR, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

      expect(pkg.scripts).toHaveProperty('start');
      expect(pkg.scripts).toHaveProperty('test');
      expect(pkg.scripts).toHaveProperty('generate');
    });

    it('should have jest as dev dependency', () => {
      const pkgPath = path.join(PROJECT_DIR, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

      expect(pkg.devDependencies).toHaveProperty('jest');
    });
  });

  describe('dashboard.html content', () => {
    it('should have SSE client code', () => {
      const htmlPath = path.join(PROJECT_DIR, 'dashboard.html');
      const content = fs.readFileSync(htmlPath, 'utf8');
      expect(content).toContain('EventSource');
      expect(content).toContain('/api/events');
    });

    it('should have XSS protection', () => {
      const htmlPath = path.join(PROJECT_DIR, 'dashboard.html');
      const content = fs.readFileSync(htmlPath, 'utf8');
      expect(content).toContain('escapeHtml');
    });

    it('should have theme support', () => {
      const htmlPath = path.join(PROJECT_DIR, 'dashboard.html');
      const content = fs.readFileSync(htmlPath, 'utf8');
      expect(content).toContain('prefers-color-scheme');
    });

    it('should have modal functionality', () => {
      const htmlPath = path.join(PROJECT_DIR, 'dashboard.html');
      const content = fs.readFileSync(htmlPath, 'utf8');
      expect(content).toContain('showProjectModal');
      expect(content).toContain('showSessionModal');
    });

    it('should have search functionality', () => {
      const htmlPath = path.join(PROJECT_DIR, 'dashboard.html');
      const content = fs.readFileSync(htmlPath, 'utf8');
      expect(content).toContain('project-search');
    });
  });
});
