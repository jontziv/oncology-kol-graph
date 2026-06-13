import { ComposableMap, Geographies, Geography, Marker } from "react-simple-maps";
import { scaleSequential } from "d3-scale";
import { interpolateBlues } from "d3-scale-chromatic";
import type { DiseaseBurdenRecord, InstitutionSummary } from "@/types";

// US AlbersUsa projection topojson
const GEO_URL = "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json";


interface DiseaseBurdenMapProps {
  burdenData: DiseaseBurdenRecord[];
  institutions: InstitutionSummary[];
  onStateClick?: (state: string) => void;
}

export function DiseaseBurdenMap({ burdenData, institutions, onStateClick }: DiseaseBurdenMapProps) {
  const maxRate = Math.max(...burdenData.map((d) => d.incidence_rate ?? 0), 1);
  const colorScale = scaleSequential(interpolateBlues).domain([0, maxRate]);

  const stateRateMap: Record<string, number> = {};
  for (const d of burdenData) {
    stateRateMap[d.state] = d.incidence_rate ?? 0;
  }

  return (
    <div className="w-full">
      <ComposableMap projection="geoAlbersUsa" className="w-full h-64">
        <Geographies geography={GEO_URL}>
          {({ geographies }: { geographies: { rsmKey: string; properties: { name: string } }[] }) =>
            geographies.map((geo) => {
              const stateName = geo.properties.name;
              const rate = stateRateMap[stateName] ?? 0;
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={rate > 0 ? colorScale(rate) : "#1e293b"}
                  stroke="#0f172a"
                  strokeWidth={0.5}
                  onClick={() => onStateClick?.(stateName)}
                  style={{
                    default: { outline: "none" },
                    hover: { fill: "#38bdf8", outline: "none", cursor: "pointer" },
                    pressed: { outline: "none" },
                  }}
                />
              );
            })
          }
        </Geographies>

        {/* Institution markers */}
        {institutions
          .filter((inst) => inst.lat && inst.lon)
          .map((inst) => (
            <Marker key={inst.id} coordinates={[inst.lon!, inst.lat!]}>
              <circle
                r={Math.min(2 + inst.trial_count * 0.5, 8)}
                fill="#f59e0b"
                fillOpacity={0.8}
                stroke="#0f172a"
                strokeWidth={0.5}
              />
            </Marker>
          ))}
      </ComposableMap>

      <div className="flex items-center justify-between text-xs text-slate-400 mt-2 px-1">
        <span>Lower NSCLC incidence</span>
        <div className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-full bg-amber-400 inline-block" />
          <span>Trial sites</span>
        </div>
        <span>Higher NSCLC incidence</span>
      </div>
    </div>
  );
}
