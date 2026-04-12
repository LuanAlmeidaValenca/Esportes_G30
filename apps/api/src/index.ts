import express, { Express, Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import apiRoutes from './routes';

dotenv.config();

const app: Express = express();
const port = process.env.PORT || 4000;

app.use(cors());
app.use(express.json({ limit: '50mb' })); // Allow large payloads for base64 images

app.get('/', (req: Request, res: Response) => {
  res.send('Sports Tracker API is running!');
});

app.use('/api', apiRoutes);

app.listen(port, () => {
  console.log(`Server is running at http://localhost:${port}`);
});
