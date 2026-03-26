import { PythonServer } from "./server";
import { AgentClient } from "./client";
import { REPL } from "./repl";
import { Display } from "./display";

const API_PORT = 8765;

async function main() {
  try {
    Display.printBanner();

    Display.printStarting();
    const server = new PythonServer(API_PORT);
    await server.start();

    Display.printInitializing();
    const startTime = Date.now();
    await server.waitUntilReady();
    const elapsedSeconds = (Date.now() - startTime) / 1000;
    Display.printReady(elapsedSeconds);

    const client = new AgentClient(`http://127.0.0.1:${API_PORT}`);
    const repl = new REPL(client);

    process.on("SIGINT", async () => {
      console.log("\n");
      Display.printGoodbye();
      await server.stop();
      process.exit(0);
    });

    process.on("SIGTERM", async () => {
      console.log("\n");
      Display.printGoodbye();
      await server.stop();
      process.exit(0);
    });

    await repl.start();

    await server.stop();
  } catch (error) {
    const message = (error as Error).message;
    Display.printError(message);
    process.exit(1);
  }
}

main();
