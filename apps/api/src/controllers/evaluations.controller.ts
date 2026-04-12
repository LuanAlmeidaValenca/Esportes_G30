import { Request, Response } from 'express';
import { db } from '../config/database';

export const getEvaluations = async (req: Request, res: Response) => {
  const { player_id, sport_id } = req.query;

  let query = `
    SELECT e.id, e.date, p.name as player_name, s.name as sport_name, e.scores, e.player_id, e.sport_id
    FROM evaluations e
    JOIN players p ON e.player_id = p.id
    JOIN sports s ON e.sport_id = s.id
    WHERE 1=1
  `;
  const args: any[] = [];

  if (player_id) {
    query += " AND e.player_id = ?";
    args.push(player_id);
  }
  if (sport_id) {
    query += " AND e.sport_id = ?";
    args.push(sport_id);
  }

  query += " ORDER BY e.date DESC";

  try {
    const result = await db.execute({ sql: query, args });
    const evaluations = result.rows.map(row => ({
      ...row,
      scores: typeof row.scores === 'string' ? JSON.parse(row.scores) : row.scores
    }));
    res.json(evaluations);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch evaluations" });
  }
};

export const createEvaluation = async (req: Request, res: Response) => {
  const { date, player_id, sport_id, scores } = req.body;
  if (!date || !player_id || !sport_id || !scores) {
    return res.status(400).json({ error: "Missing required fields" });
  }

  const scoresStr = typeof scores === 'string' ? scores : JSON.stringify(scores);

  try {
    const result = await db.execute({
      sql: "INSERT INTO evaluations (date, player_id, sport_id, scores) VALUES (?, ?, ?, ?) RETURNING *",
      args: [date, player_id, sport_id, scoresStr]
    });
    res.status(201).json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: "Failed to create evaluation" });
  }
};
