import { Router, type IRouter } from "express";
import healthRouter from "./health";
import railwayRouter from "./railway";

const router: IRouter = Router();

router.use(healthRouter);
router.use(railwayRouter);

export default router;
