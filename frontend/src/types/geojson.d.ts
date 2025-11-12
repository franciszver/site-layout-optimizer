// GeoJSON type definitions
declare namespace GeoJSON {
  interface Geometry {
    type: string
    coordinates: any
  }

  interface Feature {
    type: 'Feature'
    geometry: Geometry
    properties?: any
  }

  interface FeatureCollection {
    type: 'FeatureCollection'
    features: Feature[]
  }
}

