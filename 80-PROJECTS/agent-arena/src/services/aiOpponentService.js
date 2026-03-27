const API_URL = 'https://api.minimaxi.com/v1/chat/completions';

const SYSTEM_PROMPT = `你是一个游戏叙事设计师。请为玩家的竞技场对手生成简短信息。

格式（严格按此格式返回，每行一个字段）：
名字: [角色名]
性格: [从列表选择：鲁莽/狡猾/坚韧/均衡/狂暴/冷静]
故事: [1-2句背景故事，要有趣]

要求：
- 名字要有科幻/赛博朋克风格，2-4个字
- 性格标签从给定列表中选一个
- 故事内容要有趣味性，可以提及过去的战绩、名声或特点
- 不要编造具体的战力数值`;

export async function generateOpponentNarrative() {
  const apiKey = import.meta.env.VITE_MINIMAX_API_KEY;

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'MiniMax-M2.7-highspeed',
        max_tokens: 200,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: '生成一个竞技场对手的叙事信息。严格按格式返回：\n名字: [角色名]\n性格: [性格]\n故事: [故事]' }
        ]
      })
    });

    if (!response.ok) throw new Error(`API error: ${response.status}`);

    const data = await response.json();
    const text = data.choices[0].message.content;

    const name = text.match(/名字:\s*(.+)/)?.[1]?.trim() || '';
    const personality = text.match(/性格:\s*(.+)/)?.[1]?.trim() || '';
    const backstory = text.match(/故事:\s*(.+)/)?.[1]?.trim() || '';

    if (!name || !personality) throw new Error('Invalid AI response format');

    return { name, personality, backstory };
  } catch (err) {
    console.warn('AI opponent generation failed, using fallback:', err);
    return {
      name: '暗影猎手',
      personality: '均衡',
      backstory: '一个穿梭于暗网的神秘竞技者，据说曾在暗网深处击败过无数对手。'
    };
  }
}
