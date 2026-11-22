import { describe, expect, it } from "vitest";
import { buildSurfaceFilter, uniqueSurfaceTypes } from "./filters.js";

describe("uniqueSurfaceTypes", () => {
  it("dedupe y ordena alfabéticamente", () => {
    const features = [
      { properties: { tipo_superficie: "Asfalto" } },
      { properties: { tipo_superficie: "Concreto" } },
      { properties: { tipo_superficie: "Asfalto" } },
    ];
    expect(uniqueSurfaceTypes(features)).toEqual(["Asfalto", "Concreto"]);
  });

  it("ignora features sin la propiedad o con properties ausentes", () => {
    const features = [
      { properties: { tipo_superficie: "Asfalto" } },
      { properties: {} },
      {},
    ];
    expect(uniqueSurfaceTypes(features)).toEqual(["Asfalto"]);
  });

  it("devuelve un arreglo vacío si no hay features", () => {
    expect(uniqueSurfaceTypes([])).toEqual([]);
  });
});

describe("buildSurfaceFilter", () => {
  it("no muestra nada cuando no hay tipos seleccionados", () => {
    expect(buildSurfaceFilter([])).toEqual(["==", ["get", "tipo_superficie"], "__none__"]);
  });

  it("filtra por los tipos seleccionados", () => {
    expect(buildSurfaceFilter(["Asfalto", "Concreto"])).toEqual([
      "in",
      ["get", "tipo_superficie"],
      ["literal", ["Asfalto", "Concreto"]],
    ]);
  });
});
