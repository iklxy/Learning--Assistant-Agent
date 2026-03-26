import chalk from "chalk";

export const BANNER = `
  ██╗      ██╗ ██╗   ██╗     ██████╗  ██████╗  ██████╗  ███████╗
  ██║      ╚██╗██╔╝  ╚██╗██╔╝    ██╔════╝ ██╔═══██╗ ██╔══██╗ ██╔════╝
  ██║       ╚███╔╝    ╚███╔╝     ██║      ██║   ██║ ██║  ██║ █████╗
  ██║       ██╔██╗     ╚██╔╝     ██║      ██║   ██║ ██║  ██║ ██╔══╝
  ███████╗ ██╔╝ ██╗     ██║      ╚██████╗ ╚██████╔╝ ██████╔╝ ███████╗
  ╚══════╝╚═╝   ╚═╝     ╚═╝       ╚═════╝  ╚═════╝  ╚═════╝  ╚══════╝

  Learning Assistant Agent  |  v1.0.0  |  Powered by RAG + GPT-4
  ─────────────────────────────────────────────────────────────────
`;

export const WELCOME_TITLE = `
  ┌──────────────────────────────────────────────┐
  │  LXY Code  |  Type /help for commands        │
  └──────────────────────────────────────────────┘
`;

export class Display {
  static printBanner(): void {
    console.log(chalk.magenta(BANNER));
  }

  static printWelcome(): void {
    console.log(chalk.cyan(WELCOME_TITLE));
    console.log("");
  }

  static printStarting(): void {
    console.log(chalk.blue("  [1/2] Starting Python backend..."));
  }

  static printInitializing(): void {
    console.log(chalk.blue("  [2/2] Loading RAG knowledge base (this may take ~2 minutes)..."));
  }

  static printReady(elapsedSeconds: number): void {
    console.log(chalk.green(`  Ready. (initialized in ${elapsedSeconds.toFixed(1)}s)`));
    console.log("");
  }

  static printError(message: string): void {
    console.error(chalk.red(`  Error: ${message}`));
  }

  static printUserInput(query: string): void {
    console.log(chalk.cyan(`  You: ${query}`));
  }

  static printThinking(): void {
    console.log(chalk.yellow("  Thinking..."));
  }

  static printAgentResponse(response: string): void {
    const lines = response.split("\n");
    const indentedLines = lines.map((line) => `  ${line}`);
    console.log(chalk.green(`  Agent: ${indentedLines.join("\n")}`));
    console.log("");
  }

  static printConversationCleared(): void {
    console.log(chalk.green("  Conversation cleared."));
    console.log("");
  }

  static printHistory(messages: Array<{ role: string; content: string }>): void {
    if (messages.length === 0) {
      console.log(chalk.yellow("  No conversation history."));
      console.log("");
      return;
    }

    console.log(chalk.cyan("  Conversation History:"));
    console.log(chalk.gray("  ─────────────────────"));

    for (const msg of messages) {
      const role = msg.role === "user" ? "You" : "Agent";
      const color = msg.role === "user" ? chalk.cyan : chalk.green;
      const content =
        msg.content.length > 100 ? msg.content.substring(0, 97) + "..." : msg.content;
      console.log(`  ${color(role)}: ${content}`);
    }

    console.log("");
  }

  static printHelp(): void {
    console.log(chalk.cyan("  Commands:"));
    console.log(chalk.gray("  ─────────"));
    console.log("    /reset      Reset conversation memory");
    console.log("    /history    Show conversation history");
    console.log("    /help       Show this help message");
    console.log("    /exit       Exit the program");
    console.log("");
  }

  static printGoodbye(): void {
    console.log(chalk.cyan("  Goodbye."));
  }

  static printWaitingForInit(): void {
    console.log(chalk.yellow("  System is still initializing. Please wait..."));
  }

  static printConnectionError(): void {
    console.error(
      chalk.red("  Error: Could not connect to backend. Is the server running?")
    );
  }
}
