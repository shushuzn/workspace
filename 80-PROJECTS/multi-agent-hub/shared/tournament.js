/**
 * Tournament system — Elo-based ranking for debate participants.
 *
 * Elo expected score: E = 1 / (1 + 10^((ratingB - ratingA) / 400))
 * New rating: R' = R + K * (S - E)
 * K-factor: 32 for new players, 16 for established (≥30 games)
 */

const K_NEW = 32;
const K_ESTABLISHED = 16;
const ESTABLISHED_GAMES = 30;

export class Tournament {
  constructor() {
    /** @type {Map<string, {rating: number, games: number}>} */
    this.players = new Map();
    this.history = []; // { winner, loser, draw, timestamp }
  }

  /**
   * Register a player (persona name or model name).
   * @param {string} name
   */
  register(name) {
    if (!this.players.has(name)) {
      this.players.set(name, { rating: 1500, games: 0 });
    }
  }

  /**
   * Record a debate result.
   * @param {string} winner - winner persona name, or null for draw
   * @param {string} loser - loser persona name
   * @param {boolean} draw
   */
  recordResult(winner, loser, draw = false) {
    const w = this.players.get(winner);
    const l = this.players.get(loser);
    if (!w || !l) return;

    const Kw = w.games >= ESTABLISHED_GAMES ? K_ESTABLISHED : K_NEW;
    const Kl = l.games >= ESTABLISHED_GAMES ? K_ESTABLISHED : K_NEW;

    const Ew = 1 / (1 + Math.pow(10, (l.rating - w.rating) / 400));
    const El = 1 - Ew;

    const Sw = draw ? 0.5 : 1;
    const Sl = draw ? 0.5 : 0;

    w.rating = Math.round(w.rating + Kw * (Sw - Ew));
    l.rating = Math.round(l.rating + Kl * (Sl - El));
    w.games++;
    l.games++;

    this.history.push({
      winner: draw ? null : winner,
      loser,
      draw,
      timestamp: Date.now(),
    });
  }

  /**
   * Get rankings sorted by rating descending.
   * @returns {{name: string, rating: number, games: number}[]}
   */
  getRankings() {
    return [...this.players.entries()]
      .map(([name, data]) => ({ name, ...data }))
      .sort((a, b) => b.rating - a.rating);
  }

  /**
   * Get a player's rating.
   * @param {string} name
   * @returns {number}
   */
  getRating(name) {
    return this.players.get(name)?.rating ?? 1500;
  }

  toJSON() {
    return {
      players: Object.fromEntries(this.players),
      history: this.history,
    };
  }

  static fromJSON(data) {
    const t = new Tournament();
    if (data.players) {
      for (const [name, d] of Object.entries(data.players)) {
        t.players.set(name, d);
      }
    }
    if (data.history) t.history = data.history;
    return t;
  }
}
