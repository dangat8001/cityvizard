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
  const fallbackColor = "#fca311";
  if (values.length === 0) {
    return fallbackColor;
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (min === max) {
    return fallbackColor;
  }
  return [
    "interpolate",
    ["linear"],
    ["get", "densidad_hab_ha"],
    min,
    "#ffedcc",
    max,
    "#bd0000",
  ];
}
