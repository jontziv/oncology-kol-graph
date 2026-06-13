import { useRef, useCallback, useMemo } from "react";
import ForceGraph2D, { type NodeObject, type LinkObject } from "react-force-graph-2d";
import type { GraphNode, GraphData } from "@/types";

const LINK_COLORS: Record<string, string> = {
  affiliated_with: "#475569",
  co_investigates: "#f59e0b",
  co_authored: "#22c55e",
  investigates: "#38bdf8",
};

const NODE_COLORS: Record<string, string> = {
  kol: "#38bdf8",
  institution: "#64748b",
};

interface KOLGraphProps {
  data: GraphData;
  onNodeClick: (npi: string) => void;
  highlightNpi?: string | null;
  width: number;
  height: number;
}

export function KOLGraph({ data, onNodeClick, highlightNpi, width, height }: KOLGraphProps) {
  const fgRef = useRef<{ centerAt: (x: number, y: number, ms: number) => void } | null>(null);

  const handleNodeClick = useCallback(
    (node: NodeObject) => {
      const n = node as NodeObject & GraphNode;
      if (n.type === "kol") {
        const npi = n.id.replace("kol-", "");
        onNodeClick(npi);
      }
    },
    [onNodeClick]
  );

  const paintNode = useCallback(
    (node: NodeObject, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const n = node as NodeObject & GraphNode & { x: number; y: number };
      const isHighlighted = highlightNpi && n.id === `kol-${highlightNpi}`;
      const baseRadius = n.type === "kol" ? 4 + (n.score / 100) * 8 : 6;
      const radius = isHighlighted ? baseRadius * 1.4 : baseRadius;

      ctx.beginPath();
      ctx.arc(n.x, n.y, radius, 0, 2 * Math.PI);
      ctx.fillStyle = NODE_COLORS[n.type] ?? "#64748b";
      ctx.fill();

      if (isHighlighted) {
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2 / globalScale;
        ctx.stroke();
      }

      if (globalScale > 2 && n.label) {
        ctx.font = `${10 / globalScale}px Inter, sans-serif`;
        ctx.fillStyle = "#e2e8f0";
        ctx.textAlign = "center";
        ctx.fillText(n.label.split(" ").slice(0, 2).join(" "), n.x, n.y + radius + 6 / globalScale);
      }
    },
    [highlightNpi]
  );

  const linkColor = useCallback((link: LinkObject) => {
    const l = link as LinkObject & { type: string };
    return LINK_COLORS[l.type] ?? "#334155";
  }, []);

  const nodeTooltip = useCallback((node: NodeObject) => {
    const n = node as NodeObject & GraphNode;
    if (n.type === "kol") {
      return `${n.label}\n${n.institution ?? ""}\nKOL Score: ${n.score.toFixed(0)}`;
    }
    return n.label;
  }, []);

  const graphData = useMemo(() => ({
    nodes: data.nodes.map((n) => ({ ...n })),
    links: data.links.map((l) => ({ ...l })),
  }), [data]);

  return (
    <ForceGraph2D
      ref={fgRef as never}
      graphData={graphData}
      width={width}
      height={height}
      backgroundColor="#020617"
      nodeCanvasObject={paintNode}
      nodeCanvasObjectMode={() => "replace"}
      linkColor={linkColor}
      linkWidth={0.8}
      onNodeClick={handleNodeClick}
      nodeLabel={nodeTooltip}
      enableNodeDrag={true}
      cooldownTicks={120}
      d3AlphaDecay={0.02}
      d3VelocityDecay={0.4}
    />
  );
}
