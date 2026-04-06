/**
 * Agent Arena - Tournament System
 * Elo rating + Tournament bracket management
 */

export const INITIAL_ELO = 1000;
export const K_FACTOR = 32; // K-factor for Elo calculation

/**
 * Calculate expected score for player A vs player B
 */
export function expectedScore(ratingA, ratingB) {
  return 1 / (1 + Math.pow(10, (ratingB - ratingA) / 400));
}

/**
 * Update Elo ratings after a match
 * @returns [newRatingA, newRatingB]
 */
export function updateElo(ratingA, ratingB, scoreA) {
  // scoreA: 1 = win, 0.5 = draw, 0 = loss
  const expectedA = expectedScore(ratingA, ratingB);
  const newRatingA = Math.round(ratingA + K_FACTOR * (scoreA - expectedA));
  const newRatingB = Math.round(ratingB + K_FACTOR * ((1 - scoreA) - (1 - expectedA)));
  return [newRatingA, newRatingB];
}

/**
 * Get Elo rank label
 */
export function getEloRank(rating) {
  if (rating >= 2400) return { label: '大师', color: '#f59e0b', tier: 'master' };
  if (rating >= 2000) return { label: '钻石', color: '#a855f7', tier: 'diamond' };
  if (rating >= 1600) return { label: '黄金', color: '#eab308', tier: 'gold' };
  if (rating >= 1200) return { label: '白银', color: '#9ca3af', tier: 'silver' };
  return { label: '青铜', color: '#92400e', tier: 'bronze' };
}

/**
 * Generate a unique match ID
 */
export function generateMatchId() {
  return `M${Date.now().toString(36)}${Math.random().toString(36).substr(2, 5)}`.toUpperCase();
}

/**
 * Create a new arena match record
 */
export function createArenaMatch({
  id = generateMatchId(),
  player1Id,
  player2Id,
  player1Name,
  player2Name,
  player1Elo,
  player2Elo,
  player1Agent,
  player2Agent,
  status = 'pending',
  score1 = null,
  score2 = null,
  winnerId = null,
  rounds = [],
  timestamp = Date.now()
} = {}) {
  return {
    id,
    player1Id,
    player2Id,
    player1Name,
    player2Name,
    player1Elo,
    player2Elo,
    player1Agent,
    player2Agent,
    status,
    score1,
    score2,
    winnerId,
    rounds,
    timestamp
  };
}

/**
 * Create a tournament session
 */
export function createTournamentSession({
  id = `T${Date.now().toString(36)}`,
  name = '联赛杯',
  status = 'open', // open | live | finished
  maxParticipants = 16,
  prize = { coins: 10000, gems: 50 },
  registrationDeadline = Date.now() + 86400000, // 24h from now
  startTime = Date.now() + 86400000 * 2, // starts 48h from now
  participants = [], // [{agentId, agentName, ownerId, elo, registeredAt}]
  matches = [], // ArenaMatch[]
  standings = [], // [{rank, agentId, agentName, elo, wins, losses}]
  championId = null,
  createdAt = Date.now()
} = {}) {
  return {
    id,
    name,
    status,
    maxParticipants,
    prize,
    registrationDeadline,
    startTime,
    participants,
    matches,
    standings,
    championId,
    createdAt
  };
}

/**
 * Start the tournament — generate first round brackets
 */
export function startTournament(session) {
  if (session.status !== 'open') return session;
  if (session.participants.length < 2) return session;

  const sorted = [...session.participants].sort((a, b) => b.elo - a.elo);
  const matches = [];

  // Generate round-robin first: pair by ranking
  for (let i = 0; i < sorted.length - 1; i += 2) {
    const p1 = sorted[i];
    const p2 = sorted[i + 1];
    matches.push(createArenaMatch({
      player1Id: p1.agentId,
      player2Id: p2.agentId,
      player1Name: p1.agentName,
      player2Name: p2.agentName,
      player1Elo: p1.elo,
      player2Elo: p2.elo,
      player1Agent: p1.agent,
      player2Agent: p2.agent,
      status: 'pending'
    }));
  }

  return {
    ...session,
    status: 'live',
    participants: sorted,
    matches,
    standings: sorted.map((p, i) => ({
      rank: i + 1,
      agentId: p.agentId,
      agentName: p.agentName,
      elo: p.elo,
      wins: 0,
      losses: 0,
      draws: 0
    }))
  };
}

/**
 * Record a match result and update Elo
 */
export function recordMatchResult(session, matchId, winnerId, score1, score2) {
  const match = session.matches.find(m => m.id === matchId);
  if (!match) return session;

  const updatedMatches = session.matches.map(m => {
    if (m.id !== matchId) return m;
    return {
      ...m,
      status: 'completed',
      winnerId,
      score1,
      score2,
      rounds: match.rounds || []
    };
  });

  // Update standings
  const winnerStanding = session.standings.find(s => s.agentId === winnerId);
  const loserId = winnerId === match.player1Id ? match.player2Id : match.player1Id;
  const loserStanding = session.standings.find(s => s.agentId === loserId);

  let updatedStandings = session.standings;
  if (winnerStanding && loserStanding) {
    const [newEloWinner, newEloLoser] = updateElo(winnerStanding.elo, loserStanding.elo, 1);
    updatedStandings = session.standings.map(s => {
      if (s.agentId === winnerId) return { ...s, elo: newEloWinner, wins: s.wins + 1 };
      if (s.agentId === loserId) return { ...s, elo: newEloLoser, losses: s.losses + 1 };
      return s;
    });
  }

  // Sort standings by elo
  updatedStandings = [...updatedStandings].sort((a, b) => b.elo - a.elo)
    .map((s, i) => ({ ...s, rank: i + 1 }));

  // Check if tournament is over (all matches completed)
  const allDone = updatedMatches.every(m => m.status === 'completed');
  const championId = allDone ? updatedStandings[0]?.agentId || null : null;

  return {
    ...session,
    matches: updatedMatches,
    standings: updatedStandings,
    status: allDone ? 'finished' : 'live',
    championId
  };
}

/**
 * Get top N agents for leaderboard
 */
export function getLeaderboard(session, limit = 10) {
  return session.standings.slice(0, limit);
}

/**
 * Format Elo change string
 */
export function formatEloChange(oldElo, newElo) {
  const diff = newElo - oldElo;
  if (diff > 0) return `+${diff}`;
  return `${diff}`;
}
