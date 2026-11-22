import { describe, expect, it } from "vitest";
import {
  buildExtrusionColorExpression,
  buildExtrusionHeightExpression,
  buildUpzFilter,
  interpolateDensityColor,
  sortByPopulationDesc,
  topNFeatures,
} from "./population.js";

function feature(poblacion_total, densidad_hab_ha, codigo_upz) {
  return { properties: { poblacion_total, densidad_hab_ha, codigo_upz } };
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

describe("interpolateDensityColor", () => {
  it("devuelve el color mínimo en el extremo inferior", () => {
    expect(interpolateDensityColor(0, 0, 100)).toBe("rgb(255, 237, 204)");
  });

  it("devuelve el color máximo en el extremo superior", () => {
    expect(interpolateDensityColor(100, 0, 100)).toBe("rgb(189, 0, 0)");
  });

  it("interpola un valor intermedio", () => {
    expect(interpolateDensityColor(50, 0, 100)).toBe("rgb(222, 119, 102)");
  });

  it("devuelve el color de respaldo si min y max son iguales", () => {
    expect(interpolateDensityColor(5, 5, 5)).toBe("#fca311");
  });

  it("devuelve el color de respaldo si el valor no es numérico", () => {
    expect(interpolateDensityColor(undefined, 0, 100)).toBe("#fca311");
    expect(interpolateDensityColor(NaN, 0, 100)).toBe("#fca311");
  });
});

describe("sortByPopulationDesc", () => {
  it("ordena de mayor a menor población sin mutar el arreglo original", () => {
    const features = [feature(100), feature(300), feature(200)];
    const original = [...features];
    const sorted = sortByPopulationDesc(features);
    expect(sorted.map((f) => f.properties.poblacion_total)).toEqual([300, 200, 100]);
    expect(features).toEqual(original);
  });

  it("trata población ausente como 0", () => {
    const features = [{ properties: {} }, feature(50)];
    const sorted = sortByPopulationDesc(features);
    expect(sorted[0].properties.poblacion_total).toBe(50);
  });

  it("trata un feature sin la clave properties como 0", () => {
    const features = [{}, feature(50)];
    const sorted = sortByPopulationDesc(features);
    expect(sorted[0].properties.poblacion_total).toBe(50);
  });
});

describe("topNFeatures", () => {
  const features = [feature(100), feature(300), feature(200)];

  it("devuelve las n features más pobladas", () => {
    const top2 = topNFeatures(features, 2);
    expect(top2.map((f) => f.properties.poblacion_total)).toEqual([300, 200]);
  });

  it("devuelve todas ordenadas cuando n es 'all'", () => {
    const all = topNFeatures(features, "all");
    expect(all.map((f) => f.properties.poblacion_total)).toEqual([300, 200, 100]);
  });

  it("devuelve todas ordenadas cuando n es null/undefined", () => {
    expect(topNFeatures(features, null).length).toBe(3);
  });
});

describe("buildUpzFilter", () => {
  it("no muestra nada cuando no hay códigos seleccionados", () => {
    expect(buildUpzFilter([])).toEqual(["==", ["get", "codigo_upz"], "__none__"]);
  });

  it("filtra por los códigos de UPZ dados", () => {
    expect(buildUpzFilter([1, 2])).toEqual(["in", ["get", "codigo_upz"], ["literal", [1, 2]]]);
  });
});
