/**
 * cdp-bridge.ts
 * OpenCLI CDP browser bridge adapter for task-orchestrator
 */
export interface CDPTaskNode {
  type: 'browser';
  action: 'click' | 'type' | 'eval' | 'navigate' | 'screenshot';
  selector?: string;
  value?: string;
  url?: string;
}

export interface CDPBridgeConfig {
  daemonUrl: string;
}

export class CDPBridge {
  constructor(private config: CDPBridgeConfig) {}

  async execute(node: CDPTaskNode): Promise<{ success: boolean; result?: unknown }> {
    switch (node.action) {
      case 'click':
        return this.click(node.selector!);
      case 'type':
        return this.type(node.selector!, node.value!);
      case 'eval':
        return this.eval(node.value!);
      case 'navigate':
        return this.navigate(node.url!);
      case 'screenshot':
        return this.screenshot();
      default:
        throw new Error(`Unknown CDP action: ${(node as CDPTaskNode).action}`);
    }
  }

  private async click(selector: string): Promise<{ success: boolean }> {
    // opencli daemon bridge
    const { execSync } = await import('child_process');
    const cmd = `npx opencli browser click "${selector}" --daemon ${this.config.daemonUrl}`;
    execSync(cmd, { encoding: 'utf8' });
    return { success: true };
  }

  private async type(selector: string, value: string): Promise<{ success: boolean }> {
    const { execSync } = await import('child_process');
    const cmd = `npx opencli browser type "${selector}" "${value}" --daemon ${this.config.daemonUrl}`;
    execSync(cmd, { encoding: 'utf8' });
    return { success: true };
  }

  private async eval(script: string): Promise<{ success: boolean; result?: unknown }> {
    const { execSync } = await import('child_process');
    const cmd = `npx opencli browser eval '${script}' --daemon ${this.config.daemonUrl}`;
    const result = execSync(cmd, { encoding: 'utf8' });
    return { success: true, result };
  }

  private async navigate(url: string): Promise<{ success: boolean }> {
    const { execSync } = await import('child_process');
    const cmd = `npx opencli browser navigate "${url}" --daemon ${this.config.daemonUrl}`;
    execSync(cmd, { encoding: 'utf8' });
    return { success: true };
  }

  private async screenshot(): Promise<{ success: boolean }> {
    const { execSync } = await import('child_process');
    const cmd = `npx opencli browser screenshot --daemon ${this.config.daemonUrl}`;
    execSync(cmd, { encoding: 'utf8' });
    return { success: true };
  }
}
