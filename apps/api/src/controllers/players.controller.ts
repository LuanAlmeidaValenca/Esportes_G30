import { Request, Response } from 'express';
import { db } from '../config/database';

export const getPlayers = async (req: Request, res: Response) => {
  try {
    const result = await db.execute("SELECT id, name, photo FROM players");
    res.json(result.rows);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch players" });
  }
};

export const createPlayer = async (req: Request, res: Response) => {
  const { name, photo } = req.body;
  if (!name) return res.status(400).json({ error: "Name is required" });

  try {
    const result = await db.execute({
      sql: "INSERT INTO players (name, photo) VALUES (?, ?) RETURNING *",
      args: [name, photo || null]
    });
    res.status(201).json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: "Failed to create player" });
  }
};

export const updatePlayer = async (req: Request, res: Response) => {
  const { id } = req.params;
  const { name, photo } = req.body;

  try {
    const result = await db.execute({
      sql: "UPDATE players SET name = ?, photo = ? WHERE id = ? RETURNING *",
      args: [name, photo || null, id]
    });

    if (result.rows.length === 0) {
      return res.status(404).json({ error: "Player not found" });
    }

    res.json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: "Failed to update player" });
  }
};

export const deletePlayer = async (req: Request, res: Response) => {
  const id = String(req.params.id);

  try {
    // Cascading delete evaluations first
    await db.execute({ sql: "DELETE FROM evaluations WHERE player_id = ?", args: [id] });
    const result = await db.execute({ sql: "DELETE FROM players WHERE id = ?", args: [id] });

    if (result.rowsAffected === 0) {
      return res.status(404).json({ error: "Player not found" });
    }

    res.json({ message: "Player deleted successfully" });
  } catch (error) {
    res.status(500).json({ error: "Failed to delete player" });
  }
};
