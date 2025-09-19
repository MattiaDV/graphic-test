import OpenAI from "openai";
import readline from "readline";
import dotenv from "dotenv";

dotenv.config();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

async function chat() {
  while (true) {
    await new Promise<void>((resolve) => {
      rl.question("Tu: ", async (input) => {
        if (input.toLowerCase() === "exit") {
          rl.close();
          process.exit(0);
        }

        try {
          const response = await openai.chat.completions.create({
            model: "gpt-4o-mini",
            messages: [{ role: "user", content: input }],
          });

          const reply = response.choices[0].message?.content?.trim() || "...";
          console.log("Bot:", reply);
        } catch (err) {
          console.error("Errore:", err);
        }

        resolve();
      });
    });
  }
}

chat();
