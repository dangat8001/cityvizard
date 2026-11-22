import { describe, expect, it } from "vitest";
import { roughCentroid } from "./geo.js";

describe("roughCentroid", () => {
  it("calcula el centro de un Polygon simple", () => {
    const geometry = {
      type: "Polygon",
      coordinates: [
        [
          [0, 0],
          [0, 2],
          [2, 2],
          [2, 0],
          [0, 0],
        ],
      ],
    };
    const [lng, lat] = roughCentroid(geometry);
    expect(lng).toBeCloseTo(0.8, 5);
    expect(lat).toBeCloseTo(0.8, 5);
  });

  it("promedia los vértices de un MultiPolygon", () => {
    const geometry = {
      type: "MultiPolygon",
      coordinates: [
        [
          [
            [0, 0],
            [0, 2],
            [2, 2],
            [2, 0],
          ],
        ],
        [
          [
            [10, 10],
            [10, 12],
            [12, 12],
            [12, 10],
          ],
        ],
      ],
    };
    const [lng, lat] = roughCentroid(geometry);
    expect(lng).toBeCloseTo(6, 5);
    expect(lat).toBeCloseTo(6, 5);
  });

  it("devuelve null si no hay posiciones", () => {
    expect(roughCentroid({ type: "Polygon", coordinates: [] })).toBeNull();
  });
});
