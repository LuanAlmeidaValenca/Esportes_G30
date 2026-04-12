import { Router } from 'express';
import { getPlayers, createPlayer, updatePlayer, deletePlayer } from '../controllers/players.controller';
import { getSports, createSport, updateSport, deleteSport } from '../controllers/sports.controller';
import { getEvaluations, createEvaluation, deleteEvaluation } from '../controllers/evaluations.controller';
import { getLeaderboard, getPlayerDashboard, getComparison } from '../controllers/analytics.controller';

const router = Router();

// Players
router.get('/players', getPlayers);
router.post('/players', createPlayer);
router.put('/players/:id', updatePlayer);
router.delete('/players/:id', deletePlayer);

// Sports
router.get('/sports', getSports);
router.post('/sports', createSport);
router.put('/sports/:id', updateSport);
router.delete('/sports/:id', deleteSport);

// Evaluations
router.get('/evaluations', getEvaluations);
router.post('/evaluations', createEvaluation);
router.delete('/evaluations/:id', deleteEvaluation);

// Analytics
router.get('/analytics/leaderboard', getLeaderboard);
router.get('/analytics/dashboard/:playerId', getPlayerDashboard);
router.post('/analytics/comparison', getComparison); // POST due to multiple filters potentially

export default router;
