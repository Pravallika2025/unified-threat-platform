import { useEffect, useRef, useState } from "react";

import { tokenStore } from "@/lib/api/client";

export interface LiveMessage {
  type: "connected" | "heartbeat" | "notification";
  event: string;
  data: Record<string, unknown>;
}

const RECONNECT_BASE_MS = 1000;
const RECONNECT_MAX_MS = 30000;

/**
 * Live feed with exponential backoff. The token goes in the query string because
 * browsers cannot set headers on a WebSocket handshake; the server verifies it
 * exactly as it would a bearer header.
 */
export function useLiveFeed(onMessage?: (message: LiveMessage) => void) {
  const [connected, setConnected] = useState(false);
  const [lastMessageAt, setLastMessageAt] = useState<Date | null>(null);
  const attemptRef = useRef(0);
  const handlerRef = useRef(onMessage);
  handlerRef.current = onMessage;

  useEffect(() => {
    let socket: WebSocket | null = null;
    let timer: number | undefined;
    let closed = false;

    const connect = () => {
      const token = tokenStore.access;
      if (!token || closed) return;

      const base = import.meta.env.VITE_API_URL ?? window.location.origin;
      const url = new URL("/ws/live", base);
      url.protocol = url.protocol.replace("http", "ws");
      url.searchParams.set("token", token);

      socket = new WebSocket(url.toString());

      socket.onopen = () => {
        attemptRef.current = 0;
        setConnected(true);
      };
      socket.onmessage = (event) => {
        setLastMessageAt(new Date());
        try {
          const message = JSON.parse(event.data) as LiveMessage;
          if (message.type !== "heartbeat") handlerRef.current?.(message);
        } catch {
          /* ignore malformed frames */
        }
      };
      socket.onclose = () => {
        setConnected(false);
        if (closed) return;
        const delay = Math.min(RECONNECT_BASE_MS * 2 ** attemptRef.current++, RECONNECT_MAX_MS);
        timer = window.setTimeout(connect, delay);
      };
      socket.onerror = () => socket?.close();
    };

    connect();
    return () => {
      closed = true;
      window.clearTimeout(timer);
      socket?.close();
    };
  }, []);

  return { connected, lastMessageAt };
}
