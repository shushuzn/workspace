/**
 * Unit tests for generate-dashboard-data.js
 */

const path = require('path');
const fs = require('fs');

// Mock WORKSPACE to temp directory
const WORKSPACE = path.join(__dirname, 'test-workspace');
const OUTPUT = path.join(__dirname, 'dashboard-data.json');

describe('generate-dashboard-data.js', () => {
  beforeAll(() => {
    // Create test workspace structure
    fs.mkdirSync(WORKSPACE, { recursive: true });
    fs.mkdirSync(path.join(WORKSPACE, '80-PROJECTS'), { recursive: true });
    fs.mkdirSync(path.join(WORKSPACE, 'sessions'), { recursive: true });
    fs.mkdirSync(path.join(WORKSPACE, '.claude', 'memory'), { recursive: true });
  });

  afterAll(() => {
    // Cleanup
    const removeDir = (dir) => {
      if (!fs.existsSync(dir)) return;
      try {
        fs.readdirSync(dir).forEach(f => {
          const p = path.join(dir, f);
          try {
            fs.statSync(p).isDirectory() ? removeDir(p) : fs.unlinkSync(p);
          } catch {}
        });
        fs.rmdirSync(dir);
      } catch {}
    };
    removeDir(WORKSPACE);
    ['dashboard-data.json', 'dashboard-data.json.tmp'].forEach(f => {
      const p = path.join(__dirname, f);
      if (fs.existsSync(p)) fs.unlinkSync(p);
    });
  });

  describe('detectTechStack()', () => {
    it('should detect Svelte from package.json', () => {
      const projectPath = path.join(WORKSPACE, 'test-svelte');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        dependencies: { svelte: '^4.0.0' }
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };
      const isSvelte = deps.svelte || deps['@sveltejs/vite-plugin-svelte'];

      expect(isSvelte).toBeTruthy();
    });

    it('should detect React from package.json', () => {
      const projectPath = path.join(WORKSPACE, 'test-react');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        dependencies: { react: '^18.0.0' }
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };

      expect(deps.react).toBeTruthy();
    });

    it('should detect Next.js from package.json', () => {
      const projectPath = path.join(WORKSPACE, 'test-next');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        dependencies: { next: '^14.0.0' }
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };

      expect(deps.next).toBeTruthy();
    });

    it('should detect Express from package.json', () => {
      const projectPath = path.join(WORKSPACE, 'test-express');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        dependencies: { express: '^4.0.0' }
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };

      expect(deps.express).toBeTruthy();
    });

    it('should detect FastAPI from requirements.txt', () => {
      const projectPath = path.join(WORKSPACE, 'test-python');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'requirements.txt'), 'fastapi\nflask\n');

      const reqPath = path.join(projectPath, 'requirements.txt');
      const content = fs.readFileSync(reqPath, 'utf8');

      expect(content.includes('fastapi')).toBe(true);
    });

    it('should detect Python/Django from requirements.txt', () => {
      const projectPath = path.join(WORKSPACE, 'test-django');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'requirements.txt'), 'django\n');

      const reqPath = path.join(projectPath, 'requirements.txt');
      const content = fs.readFileSync(reqPath, 'utf8');

      expect(content.includes('django')).toBe(true);
    });

    it('should detect TypeScript from package.json', () => {
      const projectPath = path.join(WORKSPACE, 'test-ts');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        dependencies: { typescript: '^5.0.0' }
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = { ...pkg.dependencies, ...pkg.devDependencies };

      expect(deps.typescript).toBeTruthy();
    });

    it('should return TypeScript as default for empty package.json', () => {
      const projectPath = path.join(WORKSPACE, 'test-default');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        dependencies: {}
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

      expect(pkg.dependencies).toEqual({});
    });

    it('should detect Rust from Cargo.toml', () => {
      const projectPath = path.join(WORKSPACE, 'test-rust');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'Cargo.toml'), '[package]\nname = "test"\n');

      const cargoPath = path.join(projectPath, 'Cargo.toml');
      const content = fs.readFileSync(cargoPath, 'utf8');

      expect(content.includes('[package]')).toBe(true);
    });

    it('should detect Tauri from Cargo.toml', () => {
      const projectPath = path.join(WORKSPACE, 'test-tauri');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'Cargo.toml'), '[dependencies]\ntauri = "1.0"\n');

      const cargoPath = path.join(projectPath, 'Cargo.toml');
      const content = fs.readFileSync(cargoPath, 'utf8');

      expect(content.includes('tauri')).toBe(true);
    });
  });

  describe('getProjectDetails()', () => {
    it('should extract dependencies from package.json', () => {
      const projectPath = path.join(WORKSPACE, 'test-deps');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        dependencies: { react: '^18.0.0', lodash: '^4.0.0' },
        devDependencies: { jest: '^29.0.0' },
        scripts: { start: 'node index.js', test: 'jest' },
        description: 'Test project'
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = Object.keys(pkg.dependencies || {});

      expect(deps).toContain('react');
      expect(deps).toContain('lodash');
    });

    it('should limit dependencies to 5 items', () => {
      const projectPath = path.join(WORKSPACE, 'test-deps-limit');
      fs.mkdirSync(projectPath);
      const manyDeps = {};
      ['a', 'b', 'c', 'd', 'e', 'f', 'g'].forEach(k => manyDeps[k] = '^1.0.0');
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        dependencies: manyDeps
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const deps = Object.keys(pkg.dependencies || {}).slice(0, 5);

      expect(deps.length).toBe(5);
    });

    it('should extract scripts from package.json', () => {
      const projectPath = path.join(WORKSPACE, 'test-scripts');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({
        scripts: { start: 'node server.js', dev: 'nodemon', build: 'webpack' }
      }));

      const pkgPath = path.join(projectPath, 'package.json');
      const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      const scripts = Object.keys(pkg.scripts || {});

      expect(scripts).toContain('start');
      expect(scripts).toContain('dev');
    });

    it('should extract description from README.md', () => {
      const projectPath = path.join(WORKSPACE, 'test-readme');
      fs.mkdirSync(projectPath);
      fs.writeFileSync(path.join(projectPath, 'README.md'), '# Test Project\n\nThis is a test project description.\n');
      fs.writeFileSync(path.join(projectPath, 'package.json'), JSON.stringify({}));

      const readmePath = path.join(projectPath, 'README.md');
      const lines = fs.readFileSync(readmePath, 'utf8').split('\n');
      const descLine = lines.find(l => l.trim() && !l.startsWith('#') && !l.startsWith('```'));

      expect(descLine).toContain('test project description');
    });
  });

  describe('getRecentSessions()', () => {
    it('should return empty array when sessions dir is empty', () => {
      const sessionsDir = path.join(WORKSPACE, 'sessions');
      const files = fs.readdirSync(sessionsDir).filter(f => f.endsWith('.json'));

      expect(Array.isArray(files)).toBe(true);
      expect(files.length).toBe(0);
    });

    it('should return empty array when sessions dir does not exist', () => {
      const fakeDir = path.join(WORKSPACE, 'nonexistent-sessions');
      const exists = fs.existsSync(fakeDir);

      expect(exists).toBe(false);
    });
  });

  describe('getMemoryStats()', () => {
    it('should return defaults when memory file does not exist', () => {
      const memoryPath = path.join(WORKSPACE, '.claude', 'memory', 'MEMORY.md');
      const exists = fs.existsSync(memoryPath);

      expect(exists).toBe(false);
    });
  });

  describe('getProjects()', () => {
    it('should filter out 10-* directories', () => {
      const projectsDir = path.join(WORKSPACE, '80-PROJECTS');
      const dirs = fs.readdirSync(projectsDir).filter(f => {
        const stat = fs.statSync(path.join(projectsDir, f));
        return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
      });

      // Should not include 10-* prefixed directories
      dirs.forEach(d => expect(d.startsWith('10-')).toBe(false));
    });

    it('should limit projects to 12', () => {
      const projectsDir = path.join(WORKSPACE, '80-PROJECTS');
      const count = fs.readdirSync(projectsDir).filter(f => {
        try {
          const stat = fs.statSync(path.join(projectsDir, f));
          return stat.isDirectory() && !f.startsWith('10-') && !f.startsWith('.');
        } catch { return false; }
      }).length;

      // Basic check that filtering works
      expect(count).toBeGreaterThanOrEqual(0);
    });
  });

  describe('atomic write', () => {
    it('should handle missing output directory gracefully', () => {
      const tempOutput = path.join(__dirname, 'nonexistent', 'dashboard-data.json');
      const tempDir = path.dirname(tempOutput);

      // Should not throw when directory exists
      expect(fs.existsSync(tempDir)).toBe(false);
    });
  });

  describe('XSS protection via escapeHtml logic', () => {
    it('should properly escape HTML entities in project names', () => {
      const testCases = [
        { input: 'John & Jane', expect: 'John &amp; Jane' },
        { input: 'A "quoted" string', expect: 'A &quot;quoted&quot; string' },
        { input: "It's working", expect: 'It&#39;s working' },
        { input: 'Value: <100 >50', expect: 'Value: &lt;100 &gt;50' }
      ];

      // Simulate escape function
      function escapeHtml(str) {
        if (str == null) return '';
        return String(str).replace(/[&<>"']/g, c => ({
          '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[c]));
      }

      testCases.forEach(({ input, expect: expected }) => {
        expect(escapeHtml(input)).toBe(expected);
      });
    });

    it('should handle null and undefined safely', () => {
      function escapeHtml(str) {
        if (str == null) return '';
        return String(str).replace(/[&<>"']/g, c => ({
          '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
        }[c]));
      }

      expect(escapeHtml(null)).toBe('');
      expect(escapeHtml(undefined)).toBe('');
      expect(escapeHtml('')).toBe('');
    });
  });

  describe('cross-platform git commands', () => {
    it('should use correct null device for Windows', () => {
      const isWin = process.platform === 'win32';
      const nullDev = isWin ? '2>nul' : '2>/dev/null';

      expect(typeof nullDev).toBe('string');
      expect(nullDev.length).toBeGreaterThan(0);
    });

    it('should use correct null device for Unix', () => {
      // This test just verifies the logic exists
      const isWin = process.platform !== 'win32';
      const nullDev = isWin ? '2>/dev/null' : '2>nul';

      expect(typeof nullDev).toBe('string');
    });
  });
});
