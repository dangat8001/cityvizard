function flattenPositions(coords, acc = []) {
  if (typeof coords[0] === "number") {
    acc.push(coords);
  } else {
    for (const part of coords) {
      flattenPositions(part, acc);
    }
  }
  return acc;
}

/**
 * Centroide aproximado (promedio de vértices, no ponderado por área) de una
 * geometría GeoJSON Polygon o MultiPolygon. Suficiente para centrar el mapa
 * en una zona; no es un centroide geométrico exacto.
 */
export function roughCentroid(geometry) {
  const positions = flattenPositions(geometry.coordinates);
  if (positions.length === 0) {
    return null;
  }
  const [sumLng, sumLat] = positions.reduce(
    ([accLng, accLat], [lng, lat]) => [accLng + lng, accLat + lat],
    [0, 0]
  );
  return [sumLng / positions.length, sumLat / positions.length];
}
