import { cpSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "..", "..", "data", "processed");
const destination = join(here, "..", "public", "data");

mkdirSync(destination, { recursive: true });
cpSync(source, destination, {
  recursive: true,
  filter: (src) => !src.endsWith(".gitkeep"),
});

console.log(`Datos copiados de ${source} a ${destination}`);
