import * as readline from "readline";
import { AgentClient } from "./client";
import { Display } from "./display";
import ora from "ora";

export class REPL {
  private client: AgentClient;
  private rl: readline.Interface;
  private running: boolean = true;

  constructor(client: AgentClient) {
    this.client = client;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });
  }

  async start(): Promise<void> {
    Display.printWelcome();
    Display.printHelp();

    while (this.running) {
      await this.prompt();
    }
  }

  private async prompt(): Promise<void> {
    return new Promise((resolve) => {
      this.rl.question("  You: ", async (input) => {
        const trimmed = input.trim();

        if (!trimmed) {
          resolve();
          return;
        }

        if (trimmed.startsWith("/")) {
          await this.handleCommand(trimmed);
          resolve();
          return;
        }

        await this.handleQuery(trimmed);
        resolve();
      });
    });
  }

  private async handleCommand(command: string): Promise<void> {
    const cmd = command.toLowerCase();

    if (cmd === "/reset") {
      try {
        await this.client.reset();
        Display.printConversationCleared();
      } catch (error) {
        Display.printError((error as Error).message);
      }
    } else if (cmd === "/history") {
      try {
        const historyData = await this.client.history();
        Display.printHistory(historyData.messages);
      } catch (error) {
        Display.printError((error as Error).message);
      }
    } else if (cmd === "/help") {
      Display.printHelp();
    } else if (cmd === "/exit") {
      this.running = false;
      Display.printGoodbye();
      this.rl.close();
    } else {
      console.log('  Unknown command. Type "/help" for available commands.');
      console.log("");
    }
  }

  private async handleQuery(query: string): Promise<void> {
    Display.printUserInput(query);

    const spinner = ora({
      text: "Thinking...",
      prefixText: "  ",
    }).start();

    try {
      const response = await this.client.chat(query, true);
      spinner.stop();
      Display.printAgentResponse(response.response);
    } catch (error) {
      spinner.stop();
      const errorMessage = (error as Error).message;

      if (errorMessage.includes("initializing")) {
        Display.printWaitingForInit();
      } else if (errorMessage.includes("connect")) {
        Display.printConnectionError();
        this.running = false;
      } else {
        Display.printError(errorMessage);
      }

      console.log("");
    }
  }
}
