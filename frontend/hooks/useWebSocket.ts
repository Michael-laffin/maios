"use client";

import { useEffect, useRef } from "react";
import { wsClient } from "@/lib/websocket";
import type { WebSocketMessage } from "@/types/api";

export function useWebSocket(
  eventType: string,
  handler: (message: WebSocketMessage) => void
) {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    wsClient.connect();

    const unsubscribe = wsClient.subscribe(eventType, (message) => {
      handlerRef.current(message);
    });

    return unsubscribe;
  }, [eventType]);
}

export function useWebSocketConnection() {
  useEffect(() => {
    wsClient.connect();
    return () => wsClient.disconnect();
  }, []);
}
