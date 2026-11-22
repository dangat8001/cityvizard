const DENSITY_COLOR_MIN = "#ffedcc";
const DENSITY_COLOR_MAX = "#bd0000";
const DENSITY_FALLBACK_COLOR = "#fca311";

function numericValues(features, property) {
  return features
    .map((feature) => feature?.properties?.[property])
    .filter((value) => typeof value === "number" && !Number.isNaN(value));
}

/**
 * Expresión de MapLibre que mapea linealmente `poblacion_total` a una altura
 * en metros para una capa `fill-extrusion`, en función del rango real de los
 * datos recibidos.
 */
export function buildExtrusionHeightExpression(features, maxHeightMeters = 4000) {
  const values = numericValues(features, "poblacion_total");
  if (values.length === 0) {
    return 0;
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) {
    return maxHeightMeters / 2;
  }
  return ["interpolate", ["linear"], ["get", "poblacion_total"], min, 0, max, maxHeightMeters];
}

/**
 * Expresión de MapLibre que mapea linealmente `densidad_hab_ha` a un color
 * (de ámbar claro a rojo oscuro), en función del rango real de los datos.
 */
export function buildExtrusionColorExpression(features) {
  const values = numericValues(features, "densidad_hab_ha");
  if (values.length === 0) {
    return DENSITY_FALLBACK_COLOR;
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) {
    return DENSITY_FALLBACK_COLOR;
  }
  return [
    "interpolate",
    ["linear"],
    ["get", "densidad_hab_ha"],
    min,
    DENSITY_COLOR_MIN,
    max,
    DENSITY_COLOR_MAX,
  ];
}

function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function lerp(a, b, t) {
  return Math.round(a + (b - a) * t);
}

/**
 * Mismo criterio de color que `buildExtrusionColorExpression`, pero como
 * función JS directa (para pintar celdas de una tabla, no una capa MapLibre).
 */
export function interpolateDensityColor(value, min, max) {
  if (typeof value !== "number" || Number.isNaN(value) || min === max) {
    return DENSITY_FALLBACK_COLOR;
  }
  const t = Math.min(1, Math.max(0, (value - min) / (max - min)));
  const [r0, g0, b0] = hexToRgb(DENSITY_COLOR_MIN);
  const [r1, g1, b1] = hexToRgb(DENSITY_COLOR_MAX);
  return `rgb(${lerp(r0, r1, t)}, ${lerp(g0, g1, t)}, ${lerp(b0, b1, t)})`;
}

function populationOf(feature) {
  return feature?.properties?.poblacion_total ?? 0;
}

/** Features ordenadas por `poblacion_total` descendente (no muta el arreglo recibido). */
export function sortByPopulationDesc(features) {
  return [...features].sort((a, b) => populationOf(b) - populationOf(a));
}

/** Las `n` features más pobladas (o todas, si `n` es "all"). */
export function topNFeatures(features, n) {
  const sorted = sortByPopulationDesc(features);
  if (n === "all" || n == null) {
    return sorted;
  }
  return sorted.slice(0, Number(n));
}

/** Expresión de MapLibre que solo muestra las UPZ cuyo código está en `codes`. */
export function buildUpzFilter(codes) {
  if (codes.length === 0) {
    return ["==", ["get", "codigo_upz"], "__none__"];
  }
  return ["in", ["get", "codigo_upz"], ["literal", codes]];
}
