import { useState } from "react";

import { EmptyState, Panel, SeverityBadge } from "@/components/ui";
import { useLiveFeed } from "@/lib/realtime/socket";
import type { LiveMessage } from "@/lib/realtime/socket";
import { formatTime } from "@/lib/utils/format";

interface FeedItem extends LiveMessage {
  receivedAt: string;
}

const MAX_ITEMS = 100;

export function LiveMonitorPage() {
  const [items, setItems] = useState<FeedItem[]>([]);
  const { connected } = useLiveFeed((message) =>
    setItems((previous) => [{ ...message, receivedAt: new Date().toISOString() }, ...previous].slice(0, MAX_ITEMS)),
  );

  return (
    <Panel
      title="Live monitor"
      action={
        <span className="flex items-center gap-2 text-xs text-muted">
          <span className={`h-2 w-2 rounded-full ${connected ? "bg-ok" : "bg-sev-medium"}`} />
          {connected ? "Connected" : "Reconnecting"}
        </span>
      }
    >
      {items.length === 0 ? (
        <EmptyState
          title="Waiting for events"
          hint="Alerts and new incidents appear here the moment they are raised."
        />
      ) : (
        <ul className="space-y-1.5">
          {items.map((item, index) => (
            <li
              key={`${item.receivedAt}-${index}`}
              className="flex items-center gap-3 rounded-md border border-line bg-raised px-3 py-2 text-sm"
            >
              <span className="data shrink-0 text-faint">{formatTime(item.receivedAt)}</span>
              {typeof item.data.severity === "string" && (
                <SeverityBadge severity={item.data.severity} />
              )}
              <span className="truncate text-ink">
                {String(item.data.title ?? item.data.reference ?? item.event)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </Panel>
  );
}
