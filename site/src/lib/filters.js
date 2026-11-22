/** Extrae y ordena los valores distintos de `tipo_superficie` de un set de features GeoJSON. */
export function uniqueSurfaceTypes(features) {
  const types = new Set();
  for (const feature of features) {
    const value = feature?.properties?.tipo_superficie;
    if (value) {
      types.add(value);
    }
  }
  return [...types].sort();
}

/** Construye una expresión de filtro MapLibre que solo muestra los tipos seleccionados. */
export function buildSurfaceFilter(selectedTypes) {
  if (selectedTypes.length === 0) {
    return ["==", ["get", "tipo_superficie"], "__none__"];
  }
  return ["in", ["get", "tipo_superficie"], ["literal", selectedTypes]];
}
