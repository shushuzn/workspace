import { existsSync, readFileSync } from 'fs';
import { homedir } from 'os';
import { join } from 'path';
import yaml from 'yaml';
import { validateInputSlots } from './validators/inputSlotValidator.mjs';
const BUILT_IN_RULES = [
    {
        keywords: ['截图', '截屏', 'screenshot', '屏幕截图'],
        adapterId: 'opencli',
        adapterType: 'opencli',
        command: 'operate screenshot',
        args: [],
        outputSlots: ['screenshot:path'],
    },
    {
        keywords: ['wiki', 'wikipedia', '维基', '论文'],
        adapterId: 'wikipedia',
        adapterType: 'wikipedia',
        command: 'search',
        args: ['__QUERY__'],
        outputSlots: [],
    },
    {
        keywords: ['小红书', 'bilibili', '知乎', 'twitter', 'reddit', 'youtube', '打开', 'open'],
        adapterId: 'opencli',
        adapterType: 'opencli',
        command: 'operate open',
        args: [],
        outputSlots: [],
    },
    {
        keywords: ['录制', '录屏', '录视频', 'OBS', 'obs'],
        adapterId: 'cli-anything-obs',
        adapterType: 'cli-anything',
        command: 'record',
        args: [],
        outputSlots: ['video:path'],
    },
    {
        keywords: ['blender', 'Blender'],
        adapterId: 'cli-anything-blender',
        adapterType: 'cli-anything',
        command: 'render',
        args: [],
        outputSlots: [],
    },
    {
        keywords: ['gimp', 'GIMP'],
        adapterId: 'cli-anything-gimp',
        adapterType: 'cli-anything',
        command: 'export',
        args: [],
        outputSlots: [],
    },
    {
        keywords: ['导出视频', 'export', '导出'],
        adapterId: 'cli-anything-obs',
        adapterType: 'cli-anything',
        command: 'export',
        args: ['--format', 'mp4'],
        outputSlots: ['video:path'],
    },
    {
        keywords: ['shell:*'],
        adapterId: 'shell',
        adapterType: 'cli-anything',
        command: '', // command extracted from keyword (shell:...)
        args: [],
        outputSlots: [],
    },
    {
        keywords: ['swarm', 'multi-agent', '多智能体', 'multiagent'],
        adapterId: 'swarm',
        adapterType: 'swarm',
        command: 'orchestrate',
        args: [],
        outputSlots: [],
    },
    {
        keywords: ['wait', 'sleep', '延时', '延迟', '等待'],
        adapterId: ':timer',
        adapterType: 'cli-anything',
        command: '',
        args: [],
        outputSlots: [],
    },
];
function ruleDataToRule(data) {
    // Aliases are treated as additional keywords
    const allKeywords = [...data.keywords, ...(data.aliases ?? [])];
    return {
        keywords: allKeywords,
        adapterId: data.adapterId,
        adapterType: data.adapterType,
        commandBuilder: (match) => ({
            command: data.command === '' && match.startsWith('shell:')
                ? match.slice(6) // extract "echo hello" from "shell:echo hello"
                : (data.command ?? ''),
            args: data.args ?? [],
            outputSlots: data.outputSlots ?? [],
            timeoutMs: data.timeoutMs,
            maxRetries: data.maxRetries,
        }),
        priority: data.priority ?? 10,
    };
}
function validateRuleData(rule, index) {
    const errors = [];
    if (!Array.isArray(rule.keywords) || rule.keywords.length === 0) {
        errors.push({ rule: index, field: 'keywords', message: 'must be a non-empty array of strings' });
    }
    else if (!rule.keywords.every((k) => typeof k === 'string')) {
        errors.push({ rule: index, field: 'keywords', message: 'must contain only strings' });
    }
    if (typeof rule.adapterId !== 'string' || !rule.adapterId) {
        errors.push({ rule: index, field: 'adapterId', message: 'must be a non-empty string' });
    }
    if (rule.adapterType !== undefined && rule.adapterType !== 'opencli' && rule.adapterType !== 'cli-anything' && rule.adapterType !== 'multi-agent-hub' && rule.adapterType !== 'swarm') {
        errors.push({ rule: index, field: 'adapterType', message: "must be 'opencli', 'cli-anything', 'multi-agent-hub', or 'swarm'" });
    }
    if (rule.command !== undefined && (typeof rule.command !== 'string' || !rule.command)) {
        errors.push({ rule: index, field: 'command', message: 'must be a non-empty string if provided' });
    }
    if (rule.args !== undefined && !Array.isArray(rule.args)) {
        errors.push({ rule: index, field: 'args', message: 'must be an array of strings' });
    }
    if (rule.outputSlots !== undefined && !Array.isArray(rule.outputSlots)) {
        errors.push({ rule: index, field: 'outputSlots', message: 'must be an array of strings' });
    }
    if (rule.timeoutMs !== undefined && (typeof rule.timeoutMs !== 'number' || rule.timeoutMs < 0)) {
        errors.push({ rule: index, field: 'timeoutMs', message: 'must be a non-negative number' });
    }
    if (rule.priority !== undefined && typeof rule.priority !== 'number') {
        errors.push({ rule: index, field: 'priority', message: 'must be a number' });
    }
    if (rule.maxRetries !== undefined && (typeof rule.maxRetries !== 'number' || rule.maxRetries < 0)) {
        errors.push({ rule: index, field: 'maxRetries', message: 'must be a non-negative number' });
    }
    return errors;
}
function loadUserRules() {
    const configPath = join(homedir(), '.unified-agent-cli', 'rules.yaml');
    if (!existsSync(configPath))
        return [];
    try {
        const content = readFileSync(configPath, 'utf-8');
        const parsed = yaml.parse(content);
        if (!parsed || !Array.isArray(parsed.rules)) {
            if (parsed && parsed.rules !== undefined) {
                console.error(`[planner] rules.yaml: "rules" must be an array, got ${typeof parsed.rules}`);
            }
            return [];
        }
        const allErrors = [];
        const validRules = [];
        for (let i = 0; i < parsed.rules.length; i++) {
            const rule = parsed.rules[i];
            const errors = validateRuleData(rule, i);
            if (errors.length > 0) {
                allErrors.push(...errors);
            }
            else {
                validRules.push(rule);
            }
        }
        if (allErrors.length > 0) {
            for (const err of allErrors) {
                console.error(`[planner] rules.yaml rule[${err.rule}].${err.field}: ${err.message}`);
            }
        }
        return validRules;
    }
    catch (err) {
        console.error(`[planner] rules.yaml parse error: ${err instanceof Error ? err.message : String(err)}`);
        return [];
    }
}
function registrationToRule(reg) {
    return {
        keywords: reg.keywords,
        adapterId: reg.adapterId,
        adapterType: reg.adapterId.startsWith('opencli-') ? 'opencli' : reg.adapterId.startsWith('multi-agent-hub') ? 'multi-agent-hub' : 'cli-anything',
        commandBuilder: (_match) => ({
            command: reg.commands[0] ?? '',
            args: [],
            outputSlots: reg.outputSlots ?? [],
        }),
        priority: reg.priority ?? 0,
    };
}
export class Planner {
    rules;
    constructor(registry) {
        const userRules = loadUserRules();
        const builtInRules = BUILT_IN_RULES.map(ruleDataToRule);
        const userRuleObjects = userRules.map(ruleDataToRule);
        // Dynamic rules from adapter self-registration (highest priority, runs last)
        const dynamicRules = [];
        if (registry) {
            for (const reg of registry.getRegistrations()) {
                dynamicRules.push(registrationToRule(reg));
            }
        }
        // Order: built-in < user < dynamic
        this.rules = [...builtInRules, ...userRuleObjects, ...dynamicRules];
    }
    /**
     * Meta-cognitive pre-audit: before parsing, ask "am I solving the right problem?"
     * Returns { issues: string[], blocked: boolean }
     *   issues: things to reflect on before proceeding
     *   blocked: true → execution should not proceed
     *
     * The agent (not an external LLM) performs this check by examining the prompt
     * for self-reflect error class patterns (未测试/未验证/未接入/未修复/没检查/没问自己).
     */
    preAudit(prompt) {
        const issues = [];
        const lower = prompt.toLowerCase();

        // Pattern: no self-question phrases detected before taking action
        const selfQuestionPhrases = ['这个问题', '我要解决', '正确的问题', '有没有', '是否正确', '是否合理', '会不会有问题', '风险是什么', '什么会出错', '遗漏了什么'];
        const hasSelfQuestion = selfQuestionPhrases.some(p => lower.includes(p));

        // Pattern: rush to action without verification markers
        const actionPhrases = ['立刻', '马上', '直接', '先做', '先执行'];
        const hasAction = actionPhrases.some(p => lower.includes(p));
        const verifyPhrases = ['验证', '检查', '确认', '思考', '分析'];
        const hasVerify = verifyPhrases.some(p => lower.includes(p));

        // Pattern: self-reflect keywords in prompt (user explicitly writing them)
        const selfReflectMarkers = ['没检查', '没问自己', '未测试', '未验证', '未接入', '未修复', '不确定', '没把握'];
        const hasSelfReflect = selfReflectMarkers.some(p => lower.includes(p));

        if (hasSelfReflect) {
            issues.push(`PROMPT_CONTAINS_SELF_REFLECT: prompt includes self-reflect marker → "${selfReflectMarkers.find(p => lower.includes(p))}"`);
        }

        if (hasAction && !hasSelfQuestion && !hasVerify) {
            issues.push(`RUSH_TO_ACTION: prompt has action language but no self-question phrases → may not have asked "is this the right problem?"`);
        }

        return { issues, blocked: hasSelfReflect };
    }

    /** Parse a natural language prompt into ordered Steps */
    parse(prompt) {
        const steps = [];
        const errors = [];
        const warnings = [];
        const matchedKeywords = [];
        // Group matches by keyword: each keyword → best rule (highest priority)
        const keywordBestRule = new Map();
        for (const rule of this.rules) {
            for (const keyword of rule.keywords) {
                const actualMatch = this.keywordActualMatch(prompt, keyword);
                if (actualMatch !== null) {
                    matchedKeywords.push(keyword);
                    const existing = keywordBestRule.get(keyword);
                    if (!existing || rule.priority > existing.rule.priority) {
                        keywordBestRule.set(keyword, { rule, match: actualMatch });
                    }
                    break; // one rule per keyword per rule iteration (but we keep searching for higher-priority)
                }
            }
        }
        for (const { rule, match } of keywordBestRule.values()) {
            const { command, args, outputSlots, timeoutMs } = rule.commandBuilder(match);
            // Substitute __QUERY__ placeholder with the original prompt text
            const finalArgs = args.map(a => a === '__QUERY__' ? prompt : a);
            // Skip rules that produce no command (keyword-only marking rules)
            if (!command)
                continue;
            const step = {
                adapterId: rule.adapterId,
                adapterType: rule.adapterType,
                command,
                args: finalArgs,
                inputSlots: [],
                outputSlots,
                timeoutMs,
            };
            // Validate inputSlots: warn on missing files/dirs
            if (step.inputSlots.length > 0) {
                const slotWarnings = validateInputSlots(step.inputSlots, command);
                warnings.push(...slotWarnings);
            }
            steps.push(step);
        }
        // Detect rule conflicts: same (adapterId, command) produced by multiple rules → warnings
        const stepKeyToKeywords = new Map();
        for (const [kw, { rule }] of keywordBestRule.entries()) {
            const key = `${rule.adapterId}:${rule.commandBuilder('').command}`;
            if (!stepKeyToKeywords.has(key))
                stepKeyToKeywords.set(key, []);
            stepKeyToKeywords.get(key).push(kw);
        }
        for (const [key, kws] of stepKeyToKeywords) {
            if (kws.length > 1) {
                warnings.push(`Rule conflict: keywords [${kws.join(', ')}] all matched "${key}" — first wins`);
            }
        }
        // Wire adjacent steps: previous outputSlots → current inputSlots
        for (let i = 1; i < steps.length; i++) {
            const prev = steps[i - 1];
            const curr = steps[i];
            if (prev.outputSlots.length > 0 && curr.inputSlots.length === 0) {
                curr.inputSlots = [...prev.outputSlots];
            }
        }
        if (steps.length === 0 && matchedKeywords.length === 0) {
            errors.push(`No recognizable keywords in prompt: "${prompt}". Recognized: ${this.rules.flatMap(r => r.keywords).join(', ')}`);
        }
        const matchedRules = [...keywordBestRule.entries()].map(([keyword, { rule, match }]) => {
            const { command } = rule.commandBuilder(match);
            return { keyword, ruleId: rule.id ?? rule.adapterId, adapterId: rule.adapterId, command: command ?? '' };
        });
        return { steps, errors, warnings, matchedKeywords, matchedRules };
    }
    /** True if prompt contains keyword, supporting * as wildcards (match any substring) */
    keywordMatches(prompt, keyword) {
        if (!keyword.includes('*'))
            return prompt.includes(keyword);
        const regex = this.globToRegex(keyword);
        return regex.test(prompt);
    }
    /** Convert a simple glob pattern (* only) to a case-insensitive RegExp */
    keywordActualMatch(prompt, keyword) {
        if (!keyword.includes("*")) {
            return prompt.includes(keyword) ? keyword : null;
        }
        const regex = this.globToRegex(keyword);
        const m = regex.exec(prompt);
        return m ? m[0] : null;
    }
    globToRegex(pattern) {
        // Escape special regex chars, then replace * with .* and ? with .
        const escaped = pattern
            .replace(/[.+^${}()|[\]\\]/g, (c) => `\\${c}`)
            .replaceAll('*', '.*')
            .replaceAll('?', '.');
        return new RegExp(escaped, 'i');
    }
}
