/**
 * Inter-System Coordination Protocol (ISCP)
 * Enables task-orchestrator ↔ opencli ↔ CLI-Anything structured communication.
 *
 * Key differences from intra-swarm protocol:
 * - version negotiation (backward compatibility)
 * - correlationId chain (trace execution across system boundaries)
 * - structured error classification (Transient vs Fatal)
 * - cascade signaling (upstream can signal stop on error)
 * - artifact schema (typed outputs with metadata)
 */
export const ISCP_VERSION = '1.0';
export const ISCP_CONTENT_TYPE = 'application/x.iscp+v1';
export function isTransient(err) {
    return err.recoverable;
}
// ─── Factory ──────────────────────────────────────────────────────────────────
export function createCausalityLink(rootId, parentId, chain = []) {
    return {
        rootId,
        parentId,
        chain: parentId ? [...chain, parentId] : chain,
        depth: parentId ? chain.length + 1 : 0,
    };
}
export function extendCausality(childTaskId, parent) {
    return {
        rootId: parent.rootId,
        parentId: childTaskId,
        chain: [...parent.chain, childTaskId],
        depth: parent.depth + 1,
    };
}
export function createCoordinatorMessage(correlationId, lineage, type, payload) {
    return {
        version: ISCP_VERSION,
        contentType: ISCP_CONTENT_TYPE,
        correlationId,
        lineage,
        type,
        timestamp: Date.now(),
        payload,
    };
}
