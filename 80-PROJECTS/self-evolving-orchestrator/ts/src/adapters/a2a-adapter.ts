interface A2AMessage {
    id: string;
    type: string;
    from: string;
    to: string;
    payload: unknown;
}

interface PeerInfo {
    id: string;
    name: string;
    capabilities: string[];
}

export class A2AAdapter {
    private agentId: string;
    private capabilities: string[];
    private messageHandler: (msg: A2AMessage) => Promise<void>;

    constructor(agentId: string, capabilities: string[]) {
        this.agentId = agentId;
        this.capabilities = capabilities;
    }

    async register(
        messageHandler: (msg: A2AMessage) => Promise<void>
    ): Promise<void> {
        this.messageHandler = messageHandler;
        // In production: register with A2A router
        console.log(`A2A agent ${this.agentId} registered with capabilities: ${this.capabilities.join(', ')}`);
    }

    async send(task: string, targetAgents: string[]): Promise<unknown> {
        // In production: send via A2A router
        console.log(`Sending task to agents: ${targetAgents.join(', ')}`);
        return { status: 'forwarded' };
    }

    onMessage(msg: A2AMessage): void {
        if (this.messageHandler) {
            this.messageHandler(Promise.resolve(msg) as any);
        }
    }

    getAgentId(): string {
        return this.agentId;
    }

    getCapabilities(): string[] {
        return this.capabilities;
    }
}
