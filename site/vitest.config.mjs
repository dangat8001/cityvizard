import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["src/lib/**/*.test.js"],
    coverage: {
      provider: "v8",
      include: ["src/lib/**/*.js"],
      exclude: ["src/lib/**/*.test.js"],
      thresholds: {
        lines: 100,
        functions: 100,
        branches: 100,
        statements: 100,
      },
    },
  },
});
