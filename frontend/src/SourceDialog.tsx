import React, { useEffect, useRef } from "react";
export function SourceDialog({
  source,
  onClose,
}: {
  source: any;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    ref.current?.querySelector<HTMLButtonElement>("button")?.focus();
    function key(e: KeyboardEvent) {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
      if (e.key === "Tab") {
        e.preventDefault();
        ref.current?.querySelector<HTMLButtonElement>("button")?.focus();
      }
    }
    document.addEventListener("keydown", key);
    return () => {
      document.removeEventListener("keydown", key);
      previous?.focus();
    };
  }, [onClose]);
  return (
    <div className="modal-backdrop">
      <div
        className="source-reader"
        role="dialog"
        aria-modal="true"
        aria-labelledby="source-title"
        ref={ref}
      >
        <button className="text-button close" onClick={onClose}>
          Close source
        </button>
        <p className="eyebrow">
          {source.source} · REVISION {source.revision}
        </p>
        <h2 id="source-title">{source.title}</h2>
        <pre>{source.content}</pre>
      </div>
    </div>
  );
}
