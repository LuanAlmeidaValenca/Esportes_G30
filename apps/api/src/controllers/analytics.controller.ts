import { Request, Response } from 'express';
import { db } from '../config/database';

export const getLeaderboard = async (req: Request, res: Response) => {
  // Logic for /analytics/leaderboard (Last 30 days vs previous 30 days delta)
  try {
    const query = `
      WITH recent_evals AS (
        SELECT player_id, date, scores,
               CASE WHEN date(date) >= date('now', '-30 days') THEN 1 ELSE 0 END as is_last_30,
               CASE WHEN date(date) >= date('now', '-60 days') AND date(date) < date('now', '-30 days') THEN 1 ELSE 0 END as is_prev_30
        FROM evaluations
      )
      SELECT p.id, p.name, p.photo,
             json_group_array(json_object('scores', r.scores, 'is_last_30', r.is_last_30, 'is_prev_30', r.is_prev_30)) as evals_data
      FROM players p
      LEFT JOIN recent_evals r ON p.id = r.player_id
      GROUP BY p.id;
    `;
    const result = await db.execute(query);

    const leaderboard = result.rows.map(row => {
      let evals = [];
      if (typeof row.evals_data === 'string') {
        evals = JSON.parse(row.evals_data);
      }

      let last30Sum = 0;
      let last30Count = 0;
      let prev30Sum = 0;
      let prev30Count = 0;

      for (const ev of evals) {
         if (!ev.scores) continue;
         let scoresObj = typeof ev.scores === 'string' ? JSON.parse(ev.scores) : ev.scores;

         const values = Object.values(scoresObj).map(Number).filter(v => !isNaN(v));
         if (values.length === 0) continue;
         const avg = values.reduce((a, b) => a + b, 0) / values.length;

         if (ev.is_last_30) {
           last30Sum += avg;
           last30Count++;
         } else if (ev.is_prev_30) {
           prev30Sum += avg;
           prev30Count++;
         }
      }

      const current_score = last30Count > 0 ? (last30Sum / last30Count) : 0;
      const prev_score = prev30Count > 0 ? (prev30Sum / prev30Count) : 0;
      const delta = current_score - prev_score;

      return {
        id: row.id,
        name: row.name,
        photo: row.photo,
        current_score: Number(current_score.toFixed(2)),
        delta: Number(delta.toFixed(2)),
        evaluations_count: last30Count
      };
    }).sort((a, b) => b.current_score - a.current_score);

    res.json(leaderboard);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to generate leaderboard" });
  }
};

export const getPlayerDashboard = async (req: Request, res: Response) => {
  const playerId = String(req.params.playerId);
  try {
     // Fetch Player details
     const playerResult = await db.execute({ sql: "SELECT id, name, photo FROM players WHERE id = ?", args: [playerId] });
     if (playerResult.rows.length === 0) return res.status(404).json({ error: "Player not found" });
     const player = playerResult.rows[0];

     const query = `
       SELECT e.date, e.scores, s.name as sport_name,
              CASE WHEN date(e.date) >= date('now', '-30 days') THEN 1 ELSE 0 END as is_last_30,
              CASE WHEN date(e.date) >= date('now', '-60 days') AND date(e.date) < date('now', '-30 days') THEN 1 ELSE 0 END as is_prev_30
       FROM evaluations e
       JOIN sports s ON e.sport_id = s.id
       WHERE e.player_id = ?
       ORDER BY e.date ASC
     `;
     const result = await db.execute({ sql: query, args: [playerId] });

     const history = result.rows.map(row => ({
       date: row.date,
       sport_name: row.sport_name,
       scores: typeof row.scores === 'string' ? JSON.parse(row.scores) : row.scores,
       is_last_30: row.is_last_30,
       is_prev_30: row.is_prev_30
     }));

     // Calculate averages by attribute and overall KPIs
     const attributeSums: Record<string, { sum: number, count: number }> = {};
     let last30Sum = 0; let last30Count = 0;
     let prev30Sum = 0; let prev30Count = 0;

     history.forEach(h => {
       // Average of this specific evaluation
       const vals = Object.values(h.scores).map(Number).filter(v => !isNaN(v));
       const evalAvg = vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;

       if (h.is_last_30) { last30Sum += evalAvg; last30Count++; }
       if (h.is_prev_30) { prev30Sum += evalAvg; prev30Count++; }

       // Overall attribute sums for Radar chart
       for (const [key, val] of Object.entries(h.scores)) {
         if (!attributeSums[key]) attributeSums[key] = { sum: 0, count: 0 };
         attributeSums[key].sum += Number(val);
         attributeSums[key].count += 1;
       }
     });

     const radarData = Object.entries(attributeSums).map(([key, data]) => ({
       subject: key,
       A: Number((data.sum / data.count).toFixed(2)),
       fullMark: 10
     }));

     const current_score = last30Count > 0 ? (last30Sum / last30Count) : 0;
     const prev_score = prev30Count > 0 ? (prev30Sum / prev30Count) : 0;
     const delta = current_score - prev_score;

     res.json({
       player,
       kpis: {
         current_score: Number(current_score.toFixed(2)),
         delta: Number(delta.toFixed(2)),
         evaluations_last_30: last30Count
       },
       history,
       radarData
     });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to fetch dashboard data" });
  }
};

export const getComparison = async (req: Request, res: Response) => {
  const { playerIds, sportId } = req.body;
  if (!playerIds || !Array.isArray(playerIds) || !sportId) {
    return res.status(400).json({ error: "playerIds array and sportId are required" });
  }

  try {
    const placeholders = playerIds.map(() => '?').join(',');
    const query = `
      SELECT p.id, p.name, e.scores
      FROM evaluations e
      JOIN players p ON e.player_id = p.id
      WHERE e.sport_id = ? AND e.player_id IN (${placeholders})
    `;

    const result = await db.execute({ sql: query, args: [sportId, ...playerIds] });

    // Aggregate by player
    const playerAggregations: Record<string, { name: string, sums: Record<string, number>, counts: Record<string, number> }> = {};

    for (const row of result.rows) {
      const pId = String(row.id);
      const scores = typeof row.scores === 'string' ? JSON.parse(row.scores) : row.scores;

      if (!playerAggregations[pId]) {
        playerAggregations[pId] = { name: String(row.name), sums: {}, counts: {} };
      }

      for (const [attr, val] of Object.entries(scores)) {
        if (!playerAggregations[pId].sums[attr]) {
           playerAggregations[pId].sums[attr] = 0;
           playerAggregations[pId].counts[attr] = 0;
        }
        playerAggregations[pId].sums[attr] += Number(val);
        playerAggregations[pId].counts[attr] += 1;
      }
    }

    // Format for Recharts (Radar Chart with multiple lines)
    // Structure: [{ subject: "Passe", "Joao": 8, "Maria": 7 }, ...]
    const allAttributes = new Set<string>();
    Object.values(playerAggregations).forEach(p => {
       Object.keys(p.sums).forEach(attr => allAttributes.add(attr));
    });

    const radarData = Array.from(allAttributes).map(attr => {
       const dataPoint: any = { subject: attr, fullMark: 10 };

       for (const pId in playerAggregations) {
         const p = playerAggregations[pId];
         if (p.sums[attr]) {
            dataPoint[p.name] = Number((p.sums[attr] / p.counts[attr]).toFixed(2));
         } else {
            dataPoint[p.name] = 0;
         }
       }
       return dataPoint;
    });

    res.json(radarData);

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to generate comparison data" });
  }
};
