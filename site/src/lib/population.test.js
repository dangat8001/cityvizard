import { describe, expect, it } from "vitest";
import { buildExtrusionColorExpression, buildExtrusionHeightExpression } from "./population.js";

function feature(poblacion_total, densidad_hab_ha) {
  return { properties: { poblacion_total, densidad_hab_ha } };
}

describe("buildExtrusionHeightExpression", () => {
  it("interpola linealmente entre el mínimo y el máximo reales", () => {
    const features = [feature(100, 1), feature(500, 5), feature(1000, 10)];
    expect(buildExtrusionHeightExpression(features, 4000)).toEqual([
      "interpolate",
      ["linear"],
      ["get", "poblacion_total"],
      100,
      0,
      1000,
      4000,
    ]);
  });

  it("devuelve una altura constante si todos los valores son iguales", () => {
    const features = [feature(100, 1), feature(100, 1)];
    expect(buildExtrusionHeightExpression(features, 4000)).toBe(2000);
  });

  it("devuelve 0 si no hay features con el valor", () => {
    expect(buildExtrusionHeightExpression([])).toBe(0);
    expect(buildExtrusionHeightExpression([{ properties: {} }])).toBe(0);
  });
});

describe("buildExtrusionColorExpression", () => {
  it("interpola linealmente entre el mínimo y el máximo de densidad", () => {
    const features = [feature(100, 1), feature(500, 50)];
    expect(buildExtrusionColorExpression(features)).toEqual([
      "interpolate",
      ["linear"],
      ["get", "densidad_hab_ha"],
      1,
      "#ffedcc",
      50,
      "#bd0000",
    ]);
  });

  it("devuelve un color fijo si todos los valores de densidad son iguales", () => {
    const features = [feature(100, 20), feature(200, 20)];
    expect(buildExtrusionColorExpression(features)).toBe("#fca311");
  });

  it("devuelve un color fijo si no hay features con el valor", () => {
    expect(buildExtrusionColorExpression([])).toBe("#fca311");
  });
});
