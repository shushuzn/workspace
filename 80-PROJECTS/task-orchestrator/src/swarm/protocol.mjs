/**
 * Swarm Protocol - message types for inter-agent orchestration
 */
export function createMessage(type, from, payload, to) {
    return {
        type,
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        from,
        to,
        payload,
        timestamp: Date.now(),
    };
}
