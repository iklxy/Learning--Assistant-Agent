import { spawn, ChildProcess } from "child_process";
import path from "path";
import { AgentClient } from "./client";

export class PythonServer {
  private process: ChildProcess | null = null;
  private port: number;
  private projectRoot: string;

  constructor(port: number = 8765) {
    this.port = port;
    this.projectRoot = path.resolve(__dirname, "../..");
  }

  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      const serverScript = path.join(this.projectRoot, "src/api/server.py");

      this.process = spawn("python3", [serverScript], {
        cwd: this.projectRoot,
        stdio: ["ignore", "pipe", "pipe"],
        env: {
          ...process.env,
          PYTHONUNBUFFERED: "1",
          API_PORT: this.port.toString(),
        },
      });

      if (!this.process) {
        return reject(new Error("Failed to spawn Python process"));
      }

      if (this.process.stderr) {
        this.process.stderr.on("data", (data) => {
          const message = data.toString().trim();
          if (message && (message.includes("Error") || message.includes("error"))) {
            console.error(`[Python] ${message}`);
          }
        });
      }

      this.process.on("error", (error) => {
        reject(new Error(`Failed to start Python server: ${error.message}`));
      });

      this.process.on("exit", (code) => {
        if (code && code !== 0) {
          reject(new Error(`Python process exited with code ${code}`));
        }
      });

      setTimeout(() => {
        resolve();
      }, 500);
    });
  }

  async waitUntilReady(maxWaitMs: number = 300000): Promise<void> {
    const client = new AgentClient(`http://127.0.0.1:${this.port}`);
    const startTime = Date.now();
    const checkInterval = 3000;

    while (Date.now() - startTime < maxWaitMs) {
      try {
        const health = await client.health();
        if (health.status === "ready") {
          return;
        }
      } catch {
        // Service not ready yet
      }

      await new Promise((resolve) => setTimeout(resolve, checkInterval));
    }

    throw new Error(
      `Python server did not become ready within ${maxWaitMs / 1000} seconds`
    );
  }

  stop(): Promise<void> {
    return new Promise((resolve) => {
      if (!this.process) {
        return resolve();
      }

      const timeout = setTimeout(() => {
        if (this.process) {
          this.process.kill("SIGKILL");
        }
        resolve();
      }, 5000);

      this.process.on("exit", () => {
        clearTimeout(timeout);
        resolve();
      });

      this.process.kill("SIGTERM");
    });
  }

  isRunning(): boolean {
    return this.process !== null && !this.process.killed;
  }
}
