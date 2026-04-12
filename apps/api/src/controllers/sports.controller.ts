import { Request, Response } from 'express';
import { db } from '../config/database';

export const getSports = async (req: Request, res: Response) => {
  try {
    const result = await db.execute("SELECT id, name, attributes FROM sports");
    const sports = result.rows.map(row => ({
      ...row,
      attributes: typeof row.attributes === 'string' ? JSON.parse(row.attributes) : row.attributes
    }));
    res.json(sports);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch sports" });
  }
};

export const createSport = async (req: Request, res: Response) => {
  const { name, attributes } = req.body;
  if (!name || !attributes) return res.status(400).json({ error: "Name and attributes are required" });

  let attributesStr = "";
  try {
    attributesStr = typeof attributes === 'string' ? attributes : JSON.stringify(attributes);
    JSON.parse(attributesStr); // Validate JSON
  } catch (e) {
    return res.status(400).json({ error: "Attributes must be valid JSON" });
  }

  try {
    const result = await db.execute({
      sql: "INSERT INTO sports (name, attributes) VALUES (?, ?) RETURNING *",
      args: [name, attributesStr]
    });
    res.status(201).json(result.rows[0]);
  } catch (error) {
    res.status(500).json({ error: "Failed to create sport" });
  }
};

export const deleteSport = async (req: Request, res: Response) => {
  const id = String(req.params.id);

  try {
    // Cascading delete evaluations first
    await db.execute({ sql: "DELETE FROM evaluations WHERE sport_id = ?", args: [id] });
    const result = await db.execute({ sql: "DELETE FROM sports WHERE id = ?", args: [id] });

    if (result.rowsAffected === 0) {
      return res.status(404).json({ error: "Sport not found" });
    }

    res.json({ message: "Sport deleted successfully" });
  } catch (error) {
    res.status(500).json({ error: "Failed to delete sport" });
  }
};
