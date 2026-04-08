import { existsSync } from 'fs';
import { isAbsolute, resolve } from 'path';
/**
 * Validates inputSlots after parse.
 * Returns warnings for:
 * - inputSlot path doesn't exist (for file:path, dir:path, existing-file:path types)
 * - malformed slot reference
 */
export function validateInputSlots(inputSlots, stepCommand, cwd = process.cwd()) {
    const warnings = [];
    for (const slot of inputSlots) {
        // slot format: "type:path" e.g. "file:/tmp/screenshot.png", "screenshot:path"
        const colonIdx = slot.indexOf(':');
        if (colonIdx === -1)
            continue;
        const type = slot.slice(0, colonIdx);
        const rawPath = slot.slice(colonIdx + 1);
        // Only validate file-system paths (skip abstract slot names like "screenshot", "html")
        if (!rawPath || rawPath.startsWith('$') || !isAbsolute(rawPath))
            continue;
        const resolved = isAbsolute(rawPath) ? rawPath : resolve(cwd, rawPath);
        const shouldExist = type === 'file' || type === 'dir' || type === 'existing-file';
        if (shouldExist && !existsSync(resolved)) {
            warnings.push(`inputSlot "${slot}" on "${stepCommand}": path does not exist (${resolved})`);
        }
    }
    return warnings;
}
