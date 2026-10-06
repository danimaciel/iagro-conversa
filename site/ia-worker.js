// Roda o modelo de linguagem (WebLLM) fora da linha principal da página,
// para que a página continue rolando e respondendo enquanto a IA trabalha.
import { WebWorkerMLCEngineHandler } from "https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm@0.2.85/+esm";

const handler = new WebWorkerMLCEngineHandler();
self.onmessage = (msg) => handler.onmessage(msg);
